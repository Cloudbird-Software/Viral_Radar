"""LLM 网关（app 层实现）：统一调用接口 + 供应商配置化热切换（spec AC-17 / INV-5 / IFACE-3）。

业务侧只面对 chat(...) 一个接口；供应商经配置路由——mock=标准库确定性桩，
litellm=统一供应商路由库（惰性导入：未使用 litellm 供应商时不引入其依赖、不触网）。
供应商热切换 = 改配置，业务代码零改动（AC-17）。
"""

import json
from pathlib import Path


class LlmGateway:
    """统一 LLM 网关路由。config 形态：

    {"default_provider": 可选, "providers": {"名字": {"kind": "mock"|"litellm", ...}}}
    """

    def __init__(self, config: dict) -> None:
        providers = config.get("providers") or {}
        if not providers:
            raise ValueError("网关配置缺 providers（最少一个供应商）")
        self._providers = {name: dict(spec) for name, spec in providers.items()}
        self._default = config.get("default_provider") or next(iter(self._providers))

    @classmethod
    def from_config_file(cls, path: str | Path) -> "LlmGateway":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def chat(self, prompt: str, provider: str | None = None, **kwargs) -> str:
        name = provider or self._default
        if name not in self._providers:
            raise KeyError(f"未知供应商：{name}（可用：{sorted(self._providers)}）")
        spec = self._providers[name]
        kind = spec.get("kind", "litellm")
        if kind == "mock":
            return f"{spec.get('tag', 'MOCK')}: {prompt}"
        if kind == "litellm":
            return self._via_litellm(spec, prompt, **kwargs)
        raise ValueError(f"未知供应商类型：{kind}")

    def _via_litellm(self, spec: dict, prompt: str, **kwargs) -> str:
        import litellm  # 惰性导入：mock 路径零网络零外部依赖

        model = spec["model"]
        # 供应商连接参数（api_key/api_base/temperature 等）与调用级参数合并——
        # 配置里写什么就透传什么，业务代码不感知供应商差异（INV-5）。
        provider_kwargs = {k: v for k, v in spec.items() if k not in ("kind", "model", "tag")}
        response = litellm.completion(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            **{**provider_kwargs, **kwargs},
        )
        return response["choices"][0]["message"]["content"]
