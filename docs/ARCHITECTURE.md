# 架构纪律（每个模块都必须遵守）

> 从 AGENTS.md 拆出以省上下文。新建模块、动模块边界、review 时读。

## Python 四层（src/viral_radar）

1. **四层依赖方向**：adapters（采集）< processing（多模态提取）< analysis（拆解与报告）< app（编排）。
   上层可依赖下层，下层禁止 import 上层——`make arch`（`tools/check_arch.py`）机器执法；
   analysis 层禁止 import adapters 层（`INV-1` 平台隔离：核心引擎不得含平台特判分支）。
2. **每层一个目录、每模块一个 public entry**（该模块 `__init__.py` 收敛公共面）。跨模块只能 import entry。
3. **每个模块目录一份 `AGENTS.md`**：写清该模块负责什么、不变量是什么、禁止做什么、如何独立验证。
4. **模块大小上限 3000 行**。超过就拆——一个模块必须能被 agent 一次性完整读完。
5. **接口设计标准**：一个 LLM 能否仅凭函数签名 + 一行 docstring 就零样本正确使用？
   答案是否 => 接口太浅，重做。
6. **测试优先级**：先写行为不变量再写实现（fail-before：tests/card 的 TS 驱动先行红，tests/pytest 补单元面）；
   关键输出用 golden test。
7. **LLM 调用纪律**：业务层不得直连供应商 SDK——一律经统一网关接口（app 层注入），
   Prompt 与意图标签集是版本化配置资产（`INV-5` / `INV-6`）。

## TS 治理脚手架（src/index.ts / tests/card）

8. **治理面资产**：`src/index.ts` 是 quality 关卡（tsc / depcruise / vitest）的扫描锚点，
   只放契约常量，不放业务逻辑；tests/card 的 TS 驱动经 child_process 驱动真实 Python 实现，
   且驱动内的 Python 载荷只许用标准库。

## 依赖规则

新增依赖前先列出"依赖名 / 用途 / 许可证 / 是否能用标准库替代"等人确认；
禁止引入 AGPL / GPL-3.0 / SSPL 的库。
规则引擎在 `.dependency-cruiser.cjs`（TS 面，勿指向 Python 业务代码）。
