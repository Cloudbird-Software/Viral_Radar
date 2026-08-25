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
- W1-C1：账号录入与平台判定——src/viral_radar/adapters/registry.py（链接域名边界/
  ID 双口径平台判定、三通道归位、基础信息拉取、判定结果持久化可查；spec AC-1 / BEH-1）。
- W1-C3：抖音采集适配器——src/viral_radar/adapters/douyin（注入式 transport、
  近 6 个月窗口过滤、点赞/转发/热门评论元数据规范化、无直连采集路径；spec AC-4 / BEH-4 / INV-3）。
- W1-C4：采集去重与频控代理——src/viral_radar/adapters/hygiene.py（去重幂等、
  频控/代理池轮换、公开数据白名单+凭据路径拦截、CompliantTransport 唯一出站通道；
  spec AC-15 / BEH-5 / BEH-16 / INV-3）。
- W1-C7：数据融合对齐——src/viral_radar/processing/unified/fusion.py（标题+ASR+OCR
  按时间轴/图片顺序融合为统一 JSON，产物过 W0-C2 schema；缺时间戳拒绝（INV-2）；
  spec AC-7 / BEH-8）。
- W4-C1：小红书采集适配器——src/viral_radar/adapters/xhs（短视频流+图文图片集、
  封面/内页图片顺序属性、文末 Hashtag；spec AC-4 小红书面）。
- W4-C3：视频号采集适配器——src/viral_radar/adapters/video_channel（视频流+点赞/
  转发/收藏社交元数据；spec AC-4 视频号面）。
