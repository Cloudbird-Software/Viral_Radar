// W1-C1 验收驱动（spec AC-1 / BEH-1：账号录入与平台判定、三通道归位、持久化可查）。
// fail-before：本文件单独先行 commit（红）——注册表尚未落地时 import 失败被折叠为哨兵值。
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
  "import json, os, tempfile",
  "from viral_radar.adapters.registry import AccountRegistry",
  "def fetch(src):",
  "    return {'name': '账号' + src[-3:], 'followers': 1234}",
  "reg = AccountRegistry(fetch_profile=fetch)",
  "d = reg.classify('https://www.douyin.com/user/abc123')",
  "x = reg.classify('https://www.xiaohongshu.com/user/profile/5f3a')",
  "v = reg.classify('finder-abc')",
  "rec = reg.register('https://www.douyin.com/user/abc123')",
  "with tempfile.TemporaryDirectory() as tmp_dir:",
  "    path = os.path.join(tmp_dir, 'reg.json')",
  "    reg.save(path)",
  "    reg2 = AccountRegistry.load(path, fetch_profile=fetch)",
  "    back = reg2.get('https://www.douyin.com/user/abc123')",
  "print(json.dumps({",
  "  'douyin': d == 'Douyin', 'xhs': x == 'XHS', 'video': v == 'VideoChannel',",
  "  'profile_pulled': rec.profile['followers'] == 1234,",
  "  'persisted_queryable': back.platform == 'Douyin' and back.profile['name'] == rec.profile['name'],",
  "  'platform_field': rec.platform == 'Douyin',",
  "}))",
].join("\n");

describe("W1-C1 账号录入与平台判定", () => {
  it("三平台样本正确归位、基础信息拉取、判定结果持久化可查", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.douyin).toBe(true);
    expect(payload.xhs).toBe(true);
    expect(payload.video).toBe(true);
    expect(payload.profile_pulled).toBe(true);
    expect(payload.persisted_queryable).toBe(true);
    expect(payload.platform_field).toBe(true);
  });
});
