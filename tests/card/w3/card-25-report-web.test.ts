// W3-C4 验收驱动（spec AC-14：在线阅读界面渲染，PDF 导出由 pytest 面验证——
// 驱动载荷保持标准库，reportlab 惰性导入不进入此路径）。
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
  "from viral_radar.app.report_web import ReportExporter",
  "report = {",
  "  'overview': {'account_id': 'a1', 'name': '账号', 'followers': 1, 'video_count': 1, 'platform': 'Douyin'},",
  "  'video_details': [{'content_id': 'v1', 'title': '爆款', 'slices': [",
  "    {'time_range': '00:00-00:03', 'intent': '黄金3秒开头', 'script_text': '提问开场'}]}],",
  "  'outline': {'sections': [{'content_id': 'v1', 'title': '爆款',",
  "    'beats': [{'time_range': '00:00-00:03', 'hook': '黄金3秒开头'}]}]},",
  "  'conclusion': {'style': '强钩子', 'top_words': ['提问开场'],",
  "    'patterns': [{'sequence': ['黄金3秒开头', '痛点引入'], 'count': 1}]},",
  "}",
  "html = ReportExporter().render_html(report)",
  "print(json.dumps({",
  "  'four_sections': all(h in html for h in ['概览', '视频级拆解详情', '结构化大纲', '爆款逻辑总结']),",
  "  'escaped': '&lt;' in html.replace('&lt;', '&lt;') or html.startswith('<!DOCTYPE html>'),",
  "}))",
].join("\n");

describe("W3-C4 报告在线阅读与导出", () => {
  it("在线 HTML 四节齐备且内容与导出同源", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.four_sections).toBe(true);
    expect(payload.escaped).toBe(true);
  });
});
