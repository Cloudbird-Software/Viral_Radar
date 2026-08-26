// W1-C5 验收驱动（spec AC-5 / INV-2：ASR 带时间戳转写，无时间戳产物被拒绝）。
// 注意：驱动载荷用注入 stub 引擎（标准库），不触碰 faster-whisper 模型加载。
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
  "from viral_radar.processing.asr import WhisperTranscriber",
  "good = [{'start': 0.0, 'end': 2.5, 'text': '黄金三秒'},",
  "        {'start': 2.5, 'end': 5.0, 'text': '痛点引入'}]",
  "out = WhisperTranscriber().transcribe('/nonexistent/audio.wav', engine=lambda a: good)",
  "rejected = False",
  "try:",
  "    WhisperTranscriber().transcribe('/x', engine=lambda a: [{'end': 2.0, 'text': '无start'}])",
  "except ValueError:",
  "    rejected = True",
  "print(json.dumps({",
  "  'timestamps_preserved': out == [{'start': 0.0, 'end': 2.5, 'text': '黄金三秒'},",
  "                                    {'start': 2.5, 'end': 5.0, 'text': '痛点引入'}],",
  "  'no_timestamp_rejected': rejected,",
  "}))",
].join("\n");

describe("W1-C5 ASR 音轨转写", () => {
  it("带时间戳分段保留、无时间戳产物被拒绝（fail-closed）", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.timestamps_preserved).toBe(true);
    expect(payload.no_timestamp_rejected).toBe(true);
  });
});
