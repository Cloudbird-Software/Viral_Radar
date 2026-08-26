// W2-C3 验收驱动（spec AC-10 / BEH-11：叙事风格/高频词汇/固定结构套路三要素显式存在）。
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
  "from viral_radar.analysis.summary import AccountSummarizer",
  "results = [",
  "  [{'time_range': '00:00-00:03', 'script_text': '黄金3秒开头 提问开场', 'intent': '黄金3秒开头'},",
  "   {'time_range': '00:03-00:08', 'script_text': '痛点引入 怎么省钱', 'intent': '痛点引入'},",
  "   {'time_range': '00:08-00:12', 'script_text': '情绪反转 万万没想到', 'intent': '情绪反转'}],",
  "  [{'time_range': '00:00-00:03', 'script_text': '黄金3秒开头 提问开场', 'intent': '黄金3秒开头'},",
  "   {'time_range': '00:03-00:08', 'script_text': '干货输出 三步法', 'intent': '干货输出'}],",
  "]",
  "out = AccountSummarizer().summarize('acct1', results)",
  "print(json.dumps({",
  "  'three_elements': set(out.keys()) == {'style', 'top_words', 'patterns'},",
  "  'top_word_mechanical': '黄金3秒开头' in out['top_words'][:2],",
  "  'pattern_recorded': any(p['sequence'] == ['黄金3秒开头', '痛点引入', '情绪反转'] for p in out['patterns']),",
  "  'style_present': isinstance(out['style'], str) and len(out['style']) > 0,",
  "}))",
].join("\n");

describe("W2-C3 账号爆款逻辑总结", () => {
  it("叙事风格/高频词汇/固定结构套路三要素显式存在且机械派生", () => {
    const p = probe(SCRIPT);
    expect(p.ok).toBe(true);
    const payload = JSON.parse(p.out.trim()) as Record<string, boolean>;
    expect(payload.three_elements).toBe(true);
    expect(payload.top_word_mechanical).toBe(true);
    expect(payload.pattern_recorded).toBe(true);
    expect(payload.style_present).toBe(true);
  });
});
