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
- W0-C4：LLM 网关统一路由与版本化 Prompt 资产——src/viral_radar/app/llm 与
  src/viral_radar/analysis/assets（供应商配置化热切换 / 意图标签集可枚举 / 拆解模板
  版本化落仓；spec AC-17 / INV-5 / INV-6 / IFACE-2 / IFACE-3）。
- W1-C6：OCR 画面识别——src/viral_radar/processing/ocr（RapidOCR 惰性引擎、
  花字/字幕/内嵌三类文本、帧/图片顺序属性；spec AC-6 / BEH-7）。
- W2-C1：秒级结构化拆解引擎——src/viral_radar/analysis/decompose.py（时间轴切片、
  time_range/script_text/intent 三字段、intent 枚举值域 fail-closed；spec AC-8 / IFACE-2）。
- W2-C1：秒级结构化拆解引擎——src/viral_radar/analysis/decompose.py（时间轴切片、
  time_range/script_text/intent 三字段、intent 枚举值域 fail-closed；spec AC-8 / IFACE-2）。
- W1-C5：ASR 音轨转写——src/viral_radar/processing/asr（faster-whisper 惰性引擎、
  segment 级时间戳、无时间戳产物 fail-closed 拒绝；spec AC-5 / INV-2 / BEH-6）。
- fix(schema)：统一数据模型校验器允许可选字段显式 null（真实执行回归——
  平台数据 followers 等可选项常缺失；必填性仍由键存在性执法）。
- W2-C3：账号爆款逻辑总结——src/viral_radar/analysis/summary.py（叙事风格/高频词汇/
  固定结构套路三要素机械派生；spec AC-10 / BEH-11）。
- W2-C2：抖音平台差异化分析——src/viral_radar/analysis/platforms/douyin.py（节奏/
  BGM卡点/黄金3秒三产物独立、平台面互不可替换；spec AC-9 / IFACE-4）。
- W2-C4：抖音全链竖切冒烟收口——src/viral_radar/app/pipeline.py（录入→采集→融合→
  拆解→总结端到端 fixture 驱动 + 队列容错；W1+W2 集成收口）。
- W3-C1：单账号深度报告——src/viral_radar/analysis/report/single.py（概览/视频级
  拆解/结构化大纲/逻辑总结四节齐备；spec AC-11 单账号面）。
- W3-C1：单账号深度报告——src/viral_radar/analysis/report/single.py（概览/视频级
  拆解/结构化大纲/逻辑总结四节齐备；spec AC-11 单账号面）。
- W3-C2：多账号聚合对比报告——src/viral_radar/analysis/report/aggregate.py（爆款
  开头占比等量化共性特征由拆解结果机械派生；spec AC-11 聚合面）。
- W3-C3：拍摄 SOP 标准化输出——src/viral_radar/analysis/sop.py（必含元素清单/
  时长限制/分镜要求三类可执行条目；spec AC-12 / BEH-13）。
- W3-C4：报告在线阅读与 PDF 导出——src/viral_radar/app/report_web.py（HTML 在线
  阅读零依赖 + reportlab PDF 导出与在线文本同源、pypdf 测试抽取一致；spec AC-14）。
- W3-C1：单账号深度报告——src/viral_radar/analysis/report/single.py（概览/视频级
  拆解/结构化大纲/逻辑总结四节齐备；spec AC-11 单账号面）。
- W3-C2：多账号聚合对比报告——src/viral_radar/analysis/report/aggregate.py（爆款
  开头占比等量化共性特征由拆解结果机械派生；spec AC-11 聚合面）。
- W3-C3：拍摄 SOP 标准化输出——src/viral_radar/analysis/sop.py（必含元素清单/
  时长限制/分镜要求三类可执行条目；spec AC-12 / BEH-13）。
- W3-C4：报告在线阅读与 PDF 导出——src/viral_radar/app/report_web.py（HTML 在线
  阅读零依赖 + reportlab PDF 导出与在线文本同源、pypdf 测试抽取一致；spec AC-14）。
