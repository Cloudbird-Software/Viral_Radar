// W1-C3 验收驱动（spec AC-4 抖音面 / BEH-4 / INV-3：抖音采集适配器规范化输出）。
// fail-before：本文件单独先行 commit（红）——适配器未落地时 import 失败被折叠为哨兵值。
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
  "from datetime import datetime, timedelta, timezone",
  "from viral_radar.adapters.douyin import DouyinAdapter",
  "now = datetime.now(timezone.utc)",
  "fresh = (now - timedelta(days=10)).isoformat()",
  "stale = (now - timedelta(days=220)).isoformat()",
  "pages = [",
  "  {'items': [{'content_id': 'v1', 'video_url': 'https://cdn/x', 'published_at': fresh,",
  "    'likes': 100, 'shares': 20, 'top_comments': ['好评', '爆了']}], 'next_cursor': 'c2'},",
  "  {'items': [{'content_id': 'old', 'video_url': 'https://cdn/o', 'published_at': stale,",
  "    'likes': 5, 'shares': 1, 'top_comments': []}], 'next_cursor': None},",
  "]",
  "calls = []",
  "def transport(cursor):",
  "    calls.append(cursor)",
  "    return pages[len(calls) - 1]",
  "adapter = DouyinAdapter(transport=transport)",
  "items = adapter.collect('acct')",
  "no_direct = False",
  "try:",
  "    DouyinAdapter().collect('acct')",
  "except RuntimeError:",
  "    no_direct = True",
  "print(json.dumps({",
  "  'window_filtered': [i['content_id'] for i in items] == ['v1'],",
  "  'metadata_normalized': items[0]['likes'] == 100 and items[0]['shares'] == 20",
  "    and items[0]['top_comments'] == ['好评', '爆了'],",
  "  'paginated': len(calls) == 2,",
  "  'no_direct_path': no_direct,",
  "}))",
].join("\n");

describe("W1-C3 抖音采集适配器", () => {
  it("近 6 个月窗口过滤、元数据规范化、无无频控直连路径", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.window_filtered).toBe(true);
    expect(payload.metadata_normalized).toBe(true);
    expect(payload.paginated).toBe(true);
    expect(payload.no_direct_path).toBe(true);
  });
});
