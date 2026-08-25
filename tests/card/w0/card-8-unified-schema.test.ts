// W0-C2 验收驱动（spec AC-7 / IFACE-1：统一数据模型 schema v1 + 校验器）。
// fail-before：本文件单独先行 commit（红）——validator 尚未落地时
// import 失败的 python 进程被折叠为哨兵值，红=断言失败（g050 可机器判定）。
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

// 测试文件路径 tests/card/w0/<本文件> → 上溯四级到仓根（worktree 语境同样成立）。
const repoRoot = join(fileURLToPath(import.meta.url), "..", "..", "..", "..");
const python =
  process.env.PYTHON_BIN ??
  (process.platform === "win32" ? "python" : "python3");

type Probe = { ok: boolean; out: string };

/** 折叠式 python 探针：spawn/导入异常折叠为哨兵 ok=false（红必须是断言失败） */
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
  "from viral_radar.processing.unified.validator import UnifiedValidator",
  "v = UnifiedValidator()",
  "doc = {'task_id': 't1', 'platform': 'Douyin', 'content_type': 'video',",
  "       'author': {'name': 'a'}, 'content_meta': {'title': 'x'},",
  "       'raw_text': 'hello', 'timeline_data': [",
  "           {'time_start': 0, 'time_end': 2, 'source_type': 'ASR', 'raw_text': 'hi'}]}",
  "bad = dict(doc, timeline_data=[dict(doc['timeline_data'][0], source_type='BAD')])",
  "print(json.dumps({'valid_ok': v.validate(doc) == [], 'bad_rejected': v.validate(bad) != []}))",
].join("\n");

describe("W0-C2 统一数据模型 schema v1", () => {
  it("校验器接受合法样本并拒绝非法 source_type", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as {
      valid_ok: boolean;
      bad_rejected: boolean;
    };
    expect(payload.valid_ok).toBe(true);
    expect(payload.bad_rejected).toBe(true);
  });
});
