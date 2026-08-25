// W1-C7 验收驱动（spec AC-7 / BEH-8 / INV-2：融合产物必须过 W0-C2 schema 校验器）。
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
  "from viral_radar.processing.unified.fusion import FusionEngine",
  "doc = FusionEngine().fuse(",
  "    task_id='t1', platform='Douyin', content_type='video',",
  "    author={'name': 'a'}, content_meta={'title': 'x'},",
  "    title='标题文案',",
  "    asr_segments=[{'start': 0.5, 'end': 3.0, 'text': '口播'}],",
  "    ocr_items=[{'order': 1, 'time_sec': 2.0, 'text': '花字'}],",
  ")",
  "sources = {e['source_type'] for e in doc['timeline_data']}",
  "no_ts_rejected = False",
  "try:",
  "    FusionEngine().fuse(task_id='t2', platform='Douyin', content_type='video',",
  "        author={'name': 'a'}, content_meta={'title': 'x'}, title='t',",
  "        asr_segments=[{'end': 3.0, 'text': '口播'}], ocr_items=[])",
  "except ValueError:",
  "    no_ts_rejected = True",
  "print(json.dumps({",
  "  'fusion_valid': sources == {'Title', 'ASR', 'OCR'} and len(doc['timeline_data']) == 3,",
  "  'ordered': doc['timeline_data'][0]['source_type'] == 'Title',",
  "  'no_timestamp_rejected': no_ts_rejected,",
  "}))",
].join("\n");

describe("W1-C7 数据融合对齐", () => {
  it("三类文案按时间轴融合为过 schema 的统一 JSON、无时间戳被拒", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.fusion_valid).toBe(true);
    expect(payload.ordered).toBe(true);
    expect(payload.no_timestamp_rejected).toBe(true);
  });
});
