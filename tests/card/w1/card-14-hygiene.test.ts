// W1-C4 验收驱动（spec AC-15 / AC-4 去重面 / INV-3：去重幂等 + 频控代理轮换 + 公开数据边界）。
// fail-before：本文件单独先行 commit（红）——hygiene 未落地时 import 失败被折叠为哨兵值。
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
  "from viral_radar.adapters.hygiene import CompliantTransport, DedupeStore, HostGuard, RateLimiter",
  "dedupe = DedupeStore()",
  "first = dedupe.seen('v1')",
  "again = dedupe.seen('v1')",
  "proxies = []",
  "def fetch(url):",
  "    proxies.append(url)",
  "    return {'ok': 1}",
  "limiter = RateLimiter(proxies=['p1', 'p2'], min_interval_s=0)",
  "transport = CompliantTransport(fetch, HostGuard(['douyin.example']), limiter)",
  "transport.fetch('https://douyin.example/feed')",
  "transport.fetch('https://douyin.example/feed')",
  "login_blocked = False",
  "try:",
  "    transport.fetch('https://douyin.example/passport/login')",
  "except ValueError:",
  "    login_blocked = True",
  "host_blocked = False",
  "try:",
  "    transport.fetch('https://evil.example/x')",
  "except ValueError:",
  "    host_blocked = True",
  "print(json.dumps({",
  "  'dedupe_idempotent': not first and again,",
  "  'proxy_rotated': limiter._cursor == 2 and len(proxies) == 2,",
  "  'login_blocked': login_blocked, 'host_blocked': host_blocked,",
  "}))",
].join("\n");

describe("W1-C4 采集去重与频控代理", () => {
  it("去重幂等、代理轮换、凭据与越界主机被拦截", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.dedupe_idempotent).toBe(true);
    expect(payload.proxy_rotated).toBe(true);
    expect(payload.login_blocked).toBe(true);
    expect(payload.host_blocked).toBe(true);
  });
});
