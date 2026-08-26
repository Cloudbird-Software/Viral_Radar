// W3-C3 验收驱动（spec AC-12：SOP 三类可执行条目——必含元素/时长限制/分镜要求）。
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
  "from viral_radar.analysis.sop import SopBuilder",
  "report = {'conclusion': {'style': 's', 'top_words': [],",
  "  'patterns': [{'sequence': ['黄金3秒开头', '痛点引入'], 'count': 2}]}}",
  "docs = [{'task_id': 'v1', 'timeline_data': [",
  "  {'time_start': 0, 'time_end': 3, 'source_type': 'ASR', 'raw_text': 'a'},",
  "  {'time_start': 3, 'time_end': 9, 'source_type': 'ASR', 'raw_text': 'b'}]}]",
  "out = SopBuilder().build(report, docs)",
  "print(json.dumps({",
  "  'three_sections': set(out.keys()) == {'must_have_elements', 'duration_limit', 'shot_requirements'},",
  "  'elements': any('黄金3秒' in e for e in out['must_have_elements']),",
  "  'duration': '9 秒左右' in out['duration_limit'],",
  "}))",
].join("\n");

describe("W3-C3 拍摄 SOP 标准化输出", () => {
  it("必含元素/时长限制/分镜要求三类可执行条目齐备", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.three_sections).toBe(true);
    expect(payload.elements).toBe(true);
    expect(payload.duration).toBe(true);
  });
});
