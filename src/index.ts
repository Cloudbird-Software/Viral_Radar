/**
 * governance shim —— TS 治理脚手架锚点（quality 关卡 g020/depcruise、tsc、vitest 均以
 * src 为扫描面；Python 业务代码不受影响）。声明仓的运行时契约，供治理工具链与
 * tests/smoke.test.ts 校验（该测试为 g060 锁定集，勿改预期）。
 */
export function greet(name: string): string {
  return `Hello, ${name}!`;
}

/** 业务运行时语言契约：src/viral_radar 为 Python 包（ADR-0084 同型豁免）。 */
export const RUNTIME = "python";

export const CONTRACT = {
  runtime: RUNTIME,
  entry: "src/viral_radar",
};
