// W3-C1 验收驱动（spec AC-11 单账号面：深度报告四节齐备）。
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
  "from viral_radar.analysis.report.single import SingleReportBuilder",
  "docs = [{'task_id': 'v1', 'platform': 'Douyin', 'content_meta': {'title': '爆款一'},",
  "         'timeline_data': [{'time_start': 0, 'time_end': 3, 'source_type': 'ASR', 'raw_text': 'a'}]}]",
  "slices = [[{'time_range': '00:00-00:03', 'script_text': 'a', 'intent': '黄金3秒开头'}]]",
  "out = SingleReportBuilder().build('acc1', {'name': 'n', 'followers': 9}, docs, slices)",
  "print(json.dumps({",
  "  'four_sections': set(out.keys()) == {'overview', 'video_details', 'outline', 'conclusion'},",
  "  'detail_present': out['video_details'][0]['content_id'] == 'v1',",
  "}))",
].join("\n");

describe("W3-C1 单账号深度报告", () => {
  it("概览/视频级拆解/结构化大纲/逻辑总结四节齐备", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.four_sections).toBe(true);
    expect(payload.detail_present).toBe(true);
  });
});
