// W0-C1 验收驱动（spec 波次计划 W0 测试要求：骨架冒烟测试零网络零新依赖）。
// fail-before：本文件单独先行 commit（红）——python 骨架尚未落地时
// import viral_radar 失败的 python 进程被折叠为哨兵值，红=断言失败（g050 可机器判定）。
// 命名约定 tests/card/w<波次>/card-<卡号>-*.test.ts；执行经 tools/g050-runner.sh。
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

// 测试文件路径 tests/card/w0/<本文件> → 上溯四级（文件→w0→card→tests→仓根）；
// worktree 语境同样成立（红复现时该文件位于 reports/g050-worktree 内，上溯命中 worktree 根）。
const repoRoot = join(fileURLToPath(import.meta.url), "..", "..", "..", "..");
const python =
  process.env.PYTHON_BIN ??
  (process.platform === "win32" ? "python" : "python3");

type Probe = { ok: boolean; out: string };

/** 折叠式 python 探针：spawn/导入异常折叠为哨兵 ok=false（红必须是断言失败，不许抛运行时错） */
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
  "import json, importlib, viral_radar",
  "layers = ['adapters', 'processing', 'analysis', 'app']",
  "ok = all(importlib.import_module('viral_radar.' + m) for m in layers)",
  "print(json.dumps({'version': viral_radar.__version__, 'layers': ok}))",
].join("\n");

describe("W0-C1 Python 项目骨架（四层目录 + 版本契约）", () => {
  it("src/viral_radar 四层包均可导入且版本契约存在", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as {
      version: string;
      layers: boolean;
    };
    expect(payload.layers).toBe(true);
    expect(payload.version.split(".")).toHaveLength(3);
  });
});
