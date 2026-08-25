// W4-C3 验收驱动（spec AC-4 视频号面：视频流+社交元数据）
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
  "from viral_radar.adapters.video_channel import VideoChannelAdapter",
  "entry = {'content_id': 'c1', 'video_url': 'https://finder/c1',",
  "  'published_at': '2026-08-01T00:00:00+00:00', 'likes': 3, 'shares': 4, 'favorites': 5}",
  "items = VideoChannelAdapter(transport=lambda c: {'items': [entry], 'next_cursor': None}).collect('a')",
  "print(json.dumps({'social_meta': items[0]['likes'] == 3 and items[0]['shares'] == 4",
  "  and items[0]['favorites'] == 5 and items[0]['url'] == 'https://finder/c1'}))",
].join("\n");

describe("W4-C3 视频号采集适配器", () => {
  it("视频流与点赞/转发/收藏社交元数据规范化", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.social_meta).toBe(true);
  });
});
