# Viral_Radar

全网多平台爆款对标分析与脚本生成系统（IR-0001）：采集（抖音 / 小红书 / 视频号）→ 多模态提取（ASR 带时间戳 + OCR 花字）→ LLM 秒级拆解 → 单账号/聚合报告 + SOP → 仿写脚本草稿。

## 语言与结构

- 业务代码为 Python（IR-0001 语言豁免，同 ADR-0084 先例）：`src/viral_radar` 下四层
  `src/viral_radar/adapters`（采集）→ `src/viral_radar/processing`（多模态提取）→
  `src/viral_radar/analysis`（拆解与报告）→ `src/viral_radar/app`（编排）。
  跨层导入方向由 `arch` 目标（`tools/check_arch.py`）机器执法。
- 仓库保留最小 TS 治理脚手架（`src/index.ts` 契约常量 + tests TS 驱动）——
  组织 quality 关卡以 src 与 tests 为扫描面，g020/g030/g040/g050/g060/g900 关卡保持活跃。

## Makefile 接口（CI 只认这个）

| 目标         | 作用                                            |
| ------------ | ----------------------------------------------- |
| `setup`      | 安装依赖（npm ci + .venv + uv sync）            |
| `fmt`        | 格式化（ruff format + prettier）                |
| `lint`       | ruff check + format 校验 + prettier + tsc       |
| `arch`       | Python 四层导入边界执法                         |
| `test`       | pytest（tests/pytest）                          |
| `build`      | compileall 语法检查                             |
| `check`      | lint + arch + test + gates-fast，提交前必须全绿 |
| `card-test`  | 读卡 AC + 卡级测试集（TS 驱动 + pytest）        |
| `gates-pr`   | 本地复现 CI quality 关卡                        |
| `gates-fast` | quality 关卡自测（check 前置）                  |

## CI 结构

- `hygiene`：密钥扫描（gitleaks）、大文件/凭据文件拦截、zizmor Actions 审计
- `check`：make setup && make check（Python 面 + TS 治理面）
- `deps`：依赖漏洞 + 许可证审查（PR 时）；`deps-audit`：push 面 npm 锁定审计
- `quality-gates`：quality 关卡（run-gates pr）
- `gate`：聚合门（组织 ruleset 的唯一必需 check）

工作流实现在 CI-Workflows，本仓只引用 `@v1`。

## 开发流

1. 领卡与开工见 `AGENTS.md`（entry-protocol：ghcb claim + 卡 AC 测试先行）。
2. Python 单元测试放 `tests/pytest/<波次>/`（make test）；机器红复现依赖 `tests/card/**` 的 TS 驱动（g050 口径）。
3. 新依赖先报批：名称 / 用途 / 许可证 / 标准库可否替代（AGENTS.md 硬规则 3）。
4. 每模块目录一份 AGENTS.md，模块边界纪律见 `docs/ARCHITECTURE.md`。
