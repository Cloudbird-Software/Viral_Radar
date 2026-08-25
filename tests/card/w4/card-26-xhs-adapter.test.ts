// W4-C1 验收驱动（spec AC-4 小红书面：图文形态图片顺序属性+Hashtag）
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
  "from viral_radar.adapters.xhs import XhsAdapter",
  "entry = {'content_id': 'n1', 'content_type': 'images', 'cover_url': 'https://cdn/cover',",
  "  'images_urls': ['https://cdn/p1', 'https://cdn/p2'], 'hashtags': ['#美妆'],",
  "  'published_at': '2026-08-01T00:00:00+00:00', 'likes': 1, 'shares': 2}",
  "items = XhsAdapter(transport=lambda c: {'items': [entry], 'next_cursor': None}).collect('a')",
  "it = items[0]",
  "print(json.dumps({",
  "  'order_attr': it['images'][0] == 'https://cdn/cover' and it['images'][-1] == 'https://cdn/p2',",
  "  'hashtags': it['hashtags'] == ['#美妆'],",
  "}))",
].join("\n");

describe("W4-C1 小红书采集适配器", () => {
  it("图文形态产出含封面与内页图片顺序属性、文末 Hashtag", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.order_attr).toBe(true);
    expect(payload.hashtags).toBe(true);
  });
});
