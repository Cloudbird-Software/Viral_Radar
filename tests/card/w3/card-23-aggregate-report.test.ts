// W3-C2 验收驱动（spec AC-11 聚合面：跨账号共性特征量化、机械派生）。
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
  "from viral_radar.analysis.report.aggregate import AggregateReportBuilder",
  "def rep(aid):",
  "    return {'overview': {'account_id': aid}, 'video_details': [{'slices': [",
  "        {'time_range': '00:00-00:03', 'script_text': 'a', 'intent': '黄金3秒开头'},",
  "        {'time_range': '00:03-00:08', 'script_text': 'b', 'intent': '干货输出'}]}]}",
  "out = AggregateReportBuilder().build([rep('a1'), rep('a2')])",
  "q = out['quantified_common']",
  "print(json.dumps({",
  "  'quantified': q['hook_opener_share'] == 1.0 and q['hook_first_five_count'] == 2,",
  "  'mechanically_derived': set(q['intent_distribution'].keys()) == set(['黄金3秒开头', '痛点引入', '情绪反转', '干货输出', '引导转化']),",
  "}))",
].join("\n");

describe("W3-C2 多账号聚合对比报告", () => {
  it("爆款开头占比等量化特征由拆解结果机械派生", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.quantified).toBe(true);
    expect(payload.mechanically_derived).toBe(true);
  });
});
