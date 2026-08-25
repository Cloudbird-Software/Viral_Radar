// W1-C2 验收驱动（spec AC-2 / BEH-2：对标组 5-20 规模收敛 + 四维筛选结果可复核）。
// fail-before：本文件单独先行 commit（红）——组管理未落地时 import 失败被折叠为哨兵值。
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
  "from viral_radar.app.benchmark import BenchmarkGroup, GroupFilters",
  "pool = {",
  "  'a1': {'tags': ['美妆'], 'likes': 100, 'shares': 50, 'recent_viral_count': 3},",
  "  'a2': {'tags': ['美食'], 'likes': 200, 'shares': 10, 'recent_viral_count': 1},",
  "  'a3': {'tags': ['美妆'], 'likes': 300, 'shares': 60, 'recent_viral_count': 5},",
  "  'a4': {'tags': ['知识'], 'likes': 50, 'shares': 5, 'recent_viral_count': 0},",
  "  'a5': {'tags': ['美妆'], 'likes': 80, 'shares': 20, 'recent_viral_count': 2},",
  "}",
  "g = BenchmarkGroup('g1', ['a1', 'a2', 'a3', 'a4', 'a5'])",
  "lower_ok = False",
  "try:",
  "    BenchmarkGroup('g2', ['a1'])",
  "except ValueError:",
  "    lower_ok = True",
  "upper_ok = False",
  "big = ['x' + str(i) for i in range(21)]",
  "try:",
  "    BenchmarkGroup('g3', big)",
  "except ValueError:",
  "    upper_ok = True",
  "f = GroupFilters(keyword='美妆', min_likes=150, min_shares=55, min_viral=4)",
  "hits = f.apply(pool)",
  "print(json.dumps({",
  "  'lower_bound': lower_ok, 'upper_bound': upper_ok,",
  "  'four_dim_filter': hits == ['a3'],",
  "  'member_query': g.members() == ['a1', 'a2', 'a3', 'a4', 'a5'],",
  "}))",
].join("\n");

describe("W1-C2 对标组管理与四维筛选", () => {
  it("组规模收敛于 5-20 边界、四维筛选结果可复核", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.lower_bound).toBe(true);
    expect(payload.upper_bound).toBe(true);
    expect(payload.four_dim_filter).toBe(true);
    expect(payload.member_query).toBe(true);
  });
});
