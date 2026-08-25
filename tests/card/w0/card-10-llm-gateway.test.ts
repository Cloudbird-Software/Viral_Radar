// W0-C4 验收驱动（spec AC-17 / INV-5 / INV-6 / IFACE-2 / IFACE-3：
// LLM 网关统一调用 + 供应商配置化热切换 + 意图标签集与拆解 Prompt 版本化）。
// fail-before：本文件单独先行 commit（红）——网关/资产尚未落地时 import 失败被折叠为哨兵值。
// 注意：驱动 Python 载荷只使用 mock 供应商（只依赖标准库），不触碰 litellm 网络面。
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

const repoRoot = join(fileURLToPath(import.meta.url), "..", "..", "..", "..");
const python =
  process.env.PYTHON_BIN ??
  (process.platform === "win32" ? "python" : "python3");

type Probe = { ok: boolean; out: string };

function probe(script: string): Probe {
  try {
    return {
      ok: true,
      out: execFileSync(python, ["-c", script], {
        cwd: repoRoot,
        env: { ...process.env, PYTHONPATH: join(repoRoot, "src") },
        encoding: "utf8",
        timeout: 30_000,
      }),
    };
  } catch {
    return { ok: false, out: "" };
  }
}

const SCRIPT = [
  "import json",
  "from viral_radar.app.llm.gateway import LlmGateway",
  "from viral_radar.analysis.assets import AnalysisAssets",
  "gw = LlmGateway({'providers': {'a': {'kind': 'mock', 'tag': 'ALPHA'}, 'b': {'kind': 'mock', 'tag': 'BETA'}}})",
  "out_a = gw.chat('hi', provider='a')",
  "out_b = gw.chat('hi', provider='b')",
  "labels = AnalysisAssets().intent_labels()",
  "tpl = AnalysisAssets().decompose_template(version=1)",
  "print(json.dumps({",
  "  'switch_no_code_change': out_a.startswith('ALPHA') and out_b.startswith('BETA') and out_a != out_b,",
  "  'intents_enumerable': labels == ['黄金3秒开头', '痛点引入', '情绪反转', '干货输出', '引导转化'],",
  "  'template_versioned': 'time_range' in tpl and 'script_text' in tpl and 'intent' in tpl,",
  "}))",
].join("\n");

describe("W0-C4 LLM 网关与版本化 Prompt 资产", () => {
  it("mock 供应商切换业务零改动、意图标签集可枚举、拆解模板版本化", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.switch_no_code_change).toBe(true);
    expect(payload.intents_enumerable).toBe(true);
    expect(payload.template_versioned).toBe(true);
  });
});
