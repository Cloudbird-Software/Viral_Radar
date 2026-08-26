// W4-C4 验收驱动（spec AC-9 视频号面：社交货币/情绪共鸣两产物互不可替换）
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
  "from viral_radar.analysis.platforms.video_channel import VideoChannelAnalyst",
  "doc = {'platform': 'VideoChannel', 'timeline_data': [",
  "  {'time_start': 0, 'time_end': 2, 'source_type': 'ASR', 'raw_text': '治愈共鸣'}]}",
  "slices = [{'time_range': '00:00-00:02', 'script_text': '治愈共鸣', 'intent': '情绪反转'}]",
  "out = VideoChannelAnalyst().analyze(doc, slices)",
  "print(json.dumps({'two_outputs': set(out.keys()) == {'social_currency', 'emotional_resonance'},",
  "  'emotion_found': '治愈' in out['emotional_resonance']['emotive_words_found']}))",
].join("\n");

describe("W4-C4 视频号差异化分析", () => {
  it("社交货币属性与情绪共鸣点两产物独立存在", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.two_outputs).toBe(true);
    expect(payload.emotion_found).toBe(true);
  });
});
