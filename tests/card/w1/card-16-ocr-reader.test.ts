// W1-C6 验收驱动（spec AC-6：OCR 三类文本抽取 + 帧/图片顺序属性保留）。
// 注意：驱动载荷用注入 stub 引擎（标准库），不触碰 RapidOCR 模型。
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
  "from viral_radar.processing.ocr import OcrReader",
  "stub = lambda p: [{'text': '底部字幕', 'y_ratio': 0.9}, {'text': '画面花字', 'y_ratio': 0.3}]",
  "video_items = OcrReader().read('/img/frame1.png', order=3, mode='video', engine=stub)",
  "image_items = OcrReader().read('/img/page1.png', order=1, mode='image', engine=stub)",
  "print(json.dumps({",
  "  'three_kinds_and_order': video_items == [",
  "    {'order': 3, 'kind': '字幕', 'text': '底部字幕'},",
  "    {'order': 3, 'kind': '花字', 'text': '画面花字'}],",
  "  'image_embedded': all(i['kind'] == '内嵌' for i in image_items) and image_items[0]['order'] == 1,",
  "}))",
].join("\n");

describe("W1-C6 OCR 画面识别", () => {
  it("字幕/花字/内嵌三类文本抽取且顺序属性保留", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.three_kinds_and_order).toBe(true);
    expect(payload.image_embedded).toBe(true);
  });
});
