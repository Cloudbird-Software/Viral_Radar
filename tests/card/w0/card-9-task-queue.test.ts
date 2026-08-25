// W0-C3 验收驱动（spec AC-3 / AC-16 / BUDGET-2 / INV-4：异步任务队列与容错）。
// fail-before：本文件单独先行 commit（红）——队列尚未落地时 import 失败被折叠为哨兵值。
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
  "from viral_radar.app.queue import Task, TaskQueue",
  "q = TaskQueue()",
  "tid = q.submit('a1')",
  "calls = []",
  "def handler(task):",
  "    calls.append(task.task_id)",
  "    if task.task_id == 'bad': raise RuntimeError('boom')",
  "q.run_batch(['a1', 'good', 'bad'], handler)",
  "a1 = q.get(tid)",
  "bad = q.get('bad')",
  "good = q.get('good')",
  "print(json.dumps({'queryable': a1.state == 'done' and a1.task_id == tid,",
  "                   'bad_failed': bad.state == 'failed',",
  "                   'bad_attempts': bad.attempts == 3, 'bad_error': 'boom' in (bad.error or ''),",
  "                   'good_done': good.state == 'done',",
  "                   'batch_not_blocked': 'a1' in calls and 'good' in calls and len(calls) == 5}))",
].join("\n");

describe("W0-C3 异步任务队列与容错", () => {
  it("任务可查询、单条失败重试达上限后跳过且不阻塞同批次", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.queryable).toBe(true);
    expect(payload.bad_failed).toBe(true);
    expect(payload.bad_attempts).toBe(true);
    expect(payload.bad_error).toBe(true);
    expect(payload.good_done).toBe(true);
    expect(payload.batch_not_blocked).toBe(true);
  });
});