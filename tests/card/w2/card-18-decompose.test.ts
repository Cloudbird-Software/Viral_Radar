// W2-C1 验收驱动（spec AC-8 / IFACE-2：拆解输出三点字段 schema + intent 枚举值域）。
// 注意：gateway 用 mock 供应商（LLM 响应 tag 携带 JSON 数组），全程标准库。
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
  "from viral_radar.analysis.decompose import DecomposeEngine",
  "from viral_radar.app.llm.gateway import LlmGateway",
  'canned = \'[{"time_range": "00:00-00:03", "script_text": "提问开场", "intent": "黄金3秒开头"}]\'',
  "gw = LlmGateway({'providers': {'m': {'kind': 'mock', 'tag': canned}}})",
  "doc = {'task_id': 't', 'platform': 'Douyin', 'content_type': 'video',",
  "       'author': {'name': 'a'}, 'content_meta': {'title': 'x'}, 'raw_text': 'r',",
  "       'timeline_data': [{'time_start': 0, 'time_end': 3, 'source_type': 'ASR', 'raw_text': '提问开场'}]}",
  "out = DecomposeEngine().decompose(doc, gw)",
  "bad_enum = False",
  "try:",
  "    gw2 = LlmGateway({'providers': {'m': {'kind': 'mock', 'tag': '[{\"time_range\": \"00:00-00:03\", \"script_text\": \"x\", \"intent\": \"乱来\"}]'}}})",
  "    DecomposeEngine().decompose(doc, gw2)",
  "except ValueError:",
  "    bad_enum = True",
  "print(json.dumps({",
  "  'three_fields': out == [{'time_range': '00:00-00:03', 'script_text': '提问开场', 'intent': '黄金3秒开头'}],",
  "  'enum_enforced': bad_enum,",
  "}))",
].join("\n");

describe("W2-C1 秒级结构化拆解引擎", () => {
  it("输出三点字段 schema 且 intent 枚举值域被强制", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.three_fields).toBe(true);
    expect(payload.enum_enforced).toBe(true);
  });
});
