// W4-C2 验收驱动（spec AC-9 小红书面：封面/种草路径/图文排版三产物互不可替换）
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
  "from viral_radar.analysis.platforms.xhs import XhsAnalyst",
  "doc = {'platform': 'XHS', 'content_meta': {'title': '5 秒判断美妆干货？'},",
  "  'timeline_data': [{'time_start': 0, 'time_end': 1, 'source_type': 'OCR', 'raw_text': '封面'}]}",
  "slices = [{'time_range': '00:00-00:03', 'script_text': 'x', 'intent': '干货输出'},",
  "          {'time_range': '00:03-00:06', 'script_text': 'x', 'intent': '引导转化'}]",
  "out = XhsAnalyst().analyze(doc, slices)",
  "wrong = False",
  "try: XhsAnalyst().analyze({'platform': 'Douyin'}, slices)",
  "except ValueError: wrong = True",
  "print(json.dumps({'three_outputs': set(out.keys()) == {'cover_appeal', 'seeding_path', 'layout_logic'},",
  "  'isolated': wrong}))",
].join("\n");

describe("W4-C2 小红书差异化分析", () => {
  it("封面吸引力/种草转化路径/图文排版逻辑三产物独立存在", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.three_outputs).toBe(true);
    expect(payload.isolated).toBe(true);
  });
});
