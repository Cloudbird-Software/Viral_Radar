// W2-C4 验收驱动（spec 波次计划：抖音全链竖切端到端冒烟，fixture 驱动不依赖外网）。
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
  "from viral_radar.app.pipeline import AnalysisPipeline",
  "from viral_radar.app.llm.gateway import LlmGateway",
  'canned = \'[{\\"time_range\\": \\"00:00-00:03\\", \\"script_text\\": \\"提问开场\\", \\"intent\\": \\"黄金3秒开头\\"}]\'',
  "gw = LlmGateway({'providers': {'m': {'kind': 'mock', 'tag': canned}}})",
  "items = [",
  "  {'content_id': 'v1', 'title': '爆款一', 'asr_segments': [{'start': 0, 'end': 3, 'text': '提问开场'}],",
  "   'ocr_items': [{'order': 1, 'time_sec': 1.0, 'text': '花字'}]},",
  "  {'content_id': 'v2', 'title': '爆款二', 'asr_segments': [{'start': 0, 'end': 3, 'text': '提问开场'}],",
  "   'ocr_items': []},",
  "]",
  "def transport(cursor):",
  "    return {'items': items, 'next_cursor': None}",
  "out = AnalysisPipeline(",
  "    fetch_profile=lambda src: {'name': '账号', 'followers': 1},",
  "    transport=transport, gateway=gw,",
  ").run('https://www.douyin.com/user/abc123')",
  "print(json.dumps({",
  "  'full_chain': out['record'].platform == 'Douyin' and len(out['docs']) == 2",
  "    and len(out['slices']) == 2 and set(out['summary'].keys()) == {'style', 'top_words', 'patterns'},",
  "  'docs_schema_valid': out['broken'] == [],",
  "}))",
].join("\n");

describe("W2-C4 抖音全链竖切冒烟收口", () => {
  it("录入→采集→融合→拆解→总结端到端跑通（fixture 驱动）", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.full_chain).toBe(true);
    expect(payload.docs_schema_valid).toBe(true);
  });
});
