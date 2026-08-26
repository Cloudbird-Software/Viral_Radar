// W2-C2 验收驱动（spec AC-9 抖音面 / IFACE-4：节奏/BGM/黄金3秒三产物独立互不可替换）。
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
  "from viral_radar.analysis.platforms.douyin import DouyinAnalyst",
  "doc = {'platform': 'Douyin', 'timeline_data': [",
  "  {'time_start': 0, 'time_end': 3, 'source_type': 'ASR', 'raw_text': 'a'},",
  "  {'time_start': 3, 'time_end': 8, 'source_type': 'ASR', 'raw_text': 'b'}]}",
  "slices = [",
  "  {'time_range': '00:00-00:03', 'script_text': 'a', 'intent': '黄金3秒开头'},",
  "  {'time_range': '00:03-00:08', 'script_text': 'b', 'intent': '痛点引入'}]",
  "out = DouyinAnalyst().analyze(doc, slices)",
  "wrong_platform = False",
  "try:",
  "    DouyinAnalyst().analyze({'platform': 'XHS', 'timeline_data': []}, slices)",
  "except ValueError:",
  "    wrong_platform = True",
  "print(json.dumps({",
  "  'three_outputs': set(out.keys()) == {'rhythm', 'bgm', 'golden_three'},",
  "  'rhythm_mechanical': out['rhythm']['avg_segment_s'] == 4.0,",
  "  'golden3_present': out['golden_three']['golden_intent_found'] is True,",
  "  'platform_isolated': wrong_platform,",
  "}))",
].join("\n");

describe("W2-C2 抖音平台差异化分析", () => {
  it("节奏/BGM/黄金3秒三产物独立存在且平台面互不可替换", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.three_outputs).toBe(true);
    expect(payload.rhythm_mechanical).toBe(true);
    expect(payload.golden3_present).toBe(true);
    expect(payload.platform_isolated).toBe(true);
  });
});
