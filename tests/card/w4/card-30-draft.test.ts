// W4-C5 验收驱动（spec AC-13：三段结构草稿+特征引用可追溯）。
// fail-before：本文件单独先行 commit（红）——实现未落地时 import 失败被折叠为哨兵值。
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
  "from viral_radar.analysis.draft import ScriptDraftGenerator",
  "from viral_radar.app.llm.gateway import LlmGateway",
  'canned = \'{"scene": "居家场景", "script": "口播台词", "camera": "特写+慢推"}\'',
  "gw = LlmGateway({'providers': {'m': {'kind': 'mock', 'tag': canned}}})",
  "summary = {'style': '强钩子', 'top_words': ['美妆', '三步'],",
  "  'patterns': [{'sequence': ['黄金3秒开头', '干货输出'], 'count': 1}]}",
  "out = ScriptDraftGenerator().generate('a1', '新手美妆', summary, gw)",
  "print(json.dumps({'three_sections': set(out.keys()) == {'scene', 'script', 'camera', 'based_on'},",
  "  'traceable': out['based_on']['叙事风格'] == '强钩子' and out['based_on']['高频词汇'] == ['美妆', '三步']}))",
].join(`\n`);

describe("W4-C5 脚本草稿仿写生成", () => {
  it("场景描述/口播台词/运镜画面建议三段齐备且特征引用可追溯", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.three_sections).toBe(true);
    expect(payload.traceable).toBe(true);
  });
});
