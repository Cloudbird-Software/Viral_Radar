# Changelog

本文件记录对外可见的变更。格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

### Added

- W0-C1：Python 项目骨架——src/viral_radar 四层目录、pyproject + uv 锁定、ruff / pytest 接入、
  Makefile Python 目标与四层导入边界执法（specs/IR-0001 波次计划，治理基线不豁免）。
- W0-C2：统一数据模型 schema v1 与校验器——src/viral_radar/processing/unified（版本化
  schema 资产落盘 + 标准库校验器，合法/非法样本双向断言；spec AC-7 / IFACE-1）。
- W0-C3：异步任务队列与容错——src/viral_radar/app/queue.py（任务实体 / 状态机 / 重试上限
  2 次 / 失败留痕跳过 / 批次不阻塞；spec AC-3 / AC-16 / BUDGET-2 / INV-4）。
- W1-C2：对标组管理与四维筛选——src/viral_radar/app/benchmark.py（5-20 规模收敛
  执法、垂类关键词/点赞/转发/爆款频次四维筛选、确定序可复核；spec AC-2 / BEH-2）。
