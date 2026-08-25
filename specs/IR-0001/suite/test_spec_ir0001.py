#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""IR-0001 套件——全网爆款对标分析系统 spec 的结构+语义锚断言（adversary 目标目录契约）。

被审"实现" = impl-dir 下的 spec.md（文档对形态：本 IR 的交付物首件是条款级
规格本身）。断言四层（对齐 specs/IR-0001 QW_Arena1 / IR-0005 套件口径）：
  L1 结构：frontmatter 字段、AC-1..AC-18 完备、条款段齐备
  L2 语义锚：真实三平台采集×多模态×拆解管线才含的机制短语 + 条款级锚绑定
  L3 负向锚：偷懒改写最易缺的深水位标志（数值/枚举/维度计数/弱化词镜像）
  L4 一致性：AC 数、版本号、卡绑定与 IR-0001 期望对齐；防模板句复用
补强口径（先例 QW_Arena1 IR-0001 红队五轮攻击沉淀，S1'-S6）：
  S1' 摆拍式 AC、S2 义务降级、S3 义务转嫁、S4 时态后移、S5 逃生舱、S6 前置堆叠。
防"最偷懒实现"（judge-deep）口径：同义模板句无法同时命中 40+ 异质锚。
"""
import os
import re
import sys
import unittest

_cwd = os.path.abspath(os.getcwd())
IMPL = None
if os.environ.get("IMPL_DIR"):
    IMPL = os.path.normpath(os.environ["IMPL_DIR"])
elif os.path.isfile(os.path.join(_cwd, "spec.md")):
    IMPL = _cwd
elif os.path.isfile(os.path.join(_cwd, "..", "spec.md")):
    IMPL = os.path.normpath(os.path.join(_cwd, ".."))
if IMPL is None:
    raise AssertionError("无法定位 impl 目录（IMPL_DIR 未设且 cwd 上下文无 spec.md）")
SPEC = os.path.join(IMPL, "spec.md")


def read(path):
    if not os.path.isfile(path):
        raise AssertionError(f"缺文件: {path}")
    with open(path, encoding="utf-8") as f:
        return f.read()


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise AssertionError("缺 frontmatter（--- 包裹的元数据块）")
    return m.group(1)


class L1Structure(unittest.TestCase):
    def test_frontmatter_keys(self):
        fm = frontmatter(read(SPEC))
        for k in ("taskId: IR-0001", "specVersion:", "irRef:", "card:"):
            self.assertIn(k, fm, f"frontmatter 缺 {k}")

    def test_ac_complete(self):
        s = read(SPEC)
        for i in range(1, 19):
            self.assertIn(f"- id: AC-{i}", s, f"缺 AC-{i}")
        self.assertEqual(len(re.findall(r"^\s*- id: AC-\d+", s, re.M)), 18,
                         "AC 总数应为 18（编号连续且无影子条款）")

    def test_ac_gwt(self):
        s = read(SPEC)
        for i in range(1, 19):
            m = re.search(rf"- id: AC-{i}\n\s+given: (.+)\n\s+when: (.+)\n\s+then: (.+)", s)
            self.assertIsNotNone(m, f"AC-{i} 缺 given/when/then 三段")
            g, w, t = (p.strip() for p in m.groups())
            # 深度下限（S1' 补强口径）：防三段皆样板短句
            self.assertGreaterEqual(len(g), 12, f"AC-{i} given 过短（<12 字）")
            self.assertGreaterEqual(len(w), 8, f"AC-{i} when 过短（<8 字）")
            self.assertGreaterEqual(len(t), 16, f"AC-{i} then 过短（<16 字）")

    def test_clause_sections(self):
        s = read(SPEC)
        for sec in ("## INV 不变量", "## BEH 行为", "## IFACE 契约",
                    "## BUDGET 预算", "## DECISION 决策", "## ASSUMPTION 假设"):
            self.assertIn(sec, s, f"缺条款段 {sec}")
        for uid in ("INV-1", "INV-6", "BEH-1", "BEH-18",
                    "IFACE-1", "IFACE-4", "BUDGET-1", "BUDGET-2",
                    "DECISION-1", "DECISION-5", "ASSUMPTION-1"):
            self.assertIn(uid, s, f"缺条款 {uid}")


class L2SemanticAnchors(unittest.TestCase):
    """真实三平台采集×多模态×拆解管线的机制短语——偷懒改写很难全部保留且位置正确。"""

    ANCHORS = [
        "抖音", "小红书", "视频号",
        "统一数据模型", "timeline_data", "source_type",
        "ASR", "OCR", "音轨分离", "时间戳",
        "花字", "字幕", "图片内嵌文案",
        "time_range", "script_text", "intent",
        "黄金3秒开头", "痛点引入", "情绪反转", "干货输出", "引导转化",
        "BGM卡点", "种草转化路径", "社交货币", "情绪共鸣",
        "叙事风格", "高频词汇", "固定结构套路",
        "单账号深度报告", "多账号聚合", "SOP",
        "场景描述", "口播台词", "运镜", "画面建议",
        "去重机制", "频控", "代理 IP 池",
        "异步处理队列", "LLM 网关", "热切换",
        "faster-whisper", "RapidOCR", "LiteLLM", "MediaCrawler", "参考不依赖",
    ]

    def test_anchor_coverage(self):
        s = read(SPEC)
        missing = [a for a in self.ANCHORS if a not in s]
        self.assertEqual(missing, [], f"语义锚缺失: {missing}")
        # 锚密度：正文（去 frontmatter）需有体量，防"关键词堆砌+空壳条款"
        body = s.split("---", 2)[-1]
        self.assertGreaterEqual(len(body), 2000, "正文过薄——疑似空壳 spec")

    # ---- S1'（摆拍式 AC）补强：语义锚绑定到条款位置——关键词搬到别处≠语义保留 ----
    CLAUSE_ANCHORS = [
        ("INV-1", ["唯一汇合点", "平台特判"]),
        ("INV-2", ["秒级或毫秒级时间戳", "拒绝"]),
        ("INV-3", ["公开可浏览数据", "频控", "代登录"]),
        ("INV-4", ["全异步化", "阻塞"]),
        ("INV-5", ["统一 LLM 网关", "直连"]),
        ("INV-6", ["版本化配置资产", "自由文本"]),
        ("BEH-1", ["自动判定所属平台", "粉丝数"]),
        ("BEH-2", ["5-20", "垂类关键词、点赞数、转发数、近期爆款频次"]),
        ("BEH-3", ["异步处理队列", "定时全量巡检"]),
        ("BEH-4", ["近 6 个月", "Top 热门评论", "文末 Hashtag"]),
        ("BEH-5", ["去重机制", "跳过重复处理"]),
        ("BEH-6", ["秒级或毫秒级时间戳"]),
        ("BEH-7", ["花字、字幕与图片内嵌文案"]),
        ("BEH-8", ["时间轴或图片顺序", "统一数据模型"]),
        ("BEH-9", ["time_range、script_text、intent"]),
        ("BEH-10", ["黄金3秒", "种草转化路径", "社交货币"]),
        ("BEH-11", ["叙事风格、高频词汇、固定结构套路"]),
        ("BEH-12", ["单账号深度报告", "多账号聚合对比报告", "量化"]),
        ("BEH-13", ["必含元素清单、时长限制、分镜要求"]),
        ("BEH-14", ["场景描述、口播台词、运镜与画面建议"]),
        ("BEH-15", ["PDF 或 Word", "一致"]),
        ("BEH-16", ["代理 IP 池", "公开可浏览数据"]),
        ("BEH-17", ["BUDGET-2"]),
        ("BEH-18", ["统一 LLM 网关", "零改动"]),
        ("IFACE-1", ["time_start、time_end、source_type、raw_text", "ASR、OCR、Title"]),
        ("IFACE-2", ["黄金3秒开头、痛点引入、情绪反转、干货输出、引导转化"]),
        ("IFACE-3", ["热切换", "版本化"]),
        ("IFACE-4", ["互不可替换"]),
        ("BUDGET-2", ["上限为 2 次"]),
        ("DECISION-1", ["faster-whisper", "RapidOCR", "LiteLLM", "参考不依赖"]),
    ]

    def test_clause_anchor_binding(self):
        s = read(SPEC)
        clauses = dict(re.findall(r"^- ((?:INV|BEH|IFACE|BUDGET|DECISION)-\d+): (.+)$", s, re.M))
        for uid, anchors in self.CLAUSE_ANCHORS:
            self.assertIn(uid, clauses, f"缺条款 {uid}")
            missing = [a for a in anchors if a not in clauses[uid]]
            self.assertEqual(missing, [], f"{uid} 条款语义锚缺失 {missing}——摆拍式改写嫌疑")

    def test_clause_normative_depth(self):
        """每条条款须 ≥20 字且 INV/BEH/IFACE 含规范性动词——空壳条款直接红。"""
        s = read(SPEC)
        clauses = re.findall(r"^- ((?:INV|BEH|IFACE|BUDGET|DECISION|ASSUMPTION)-\d+): (.+)$", s, re.M)
        self.assertGreaterEqual(len(clauses), 38, "条款总数少于 38")
        normative = ("必须", "不得", "禁止", "须", "应")
        for uid, text in clauses:
            self.assertGreaterEqual(len(text), 20, f"{uid} 条款正文短于 20 字——空壳条款")
            if uid.startswith(("INV", "BEH", "IFACE")):
                self.assertTrue(any(w in text for w in normative),
                                f"{uid} 缺规范性动词（必须/不得/禁止/须/应）——摆拍式条款")

    # ---- S2（义务降级）补强：强规范动词必须是"必须/不得/禁止" ----
    STRONG_MODALITY = ("必须", "不得", "禁止")

    def test_strong_modality(self):
        """INV/BEH/IFACE 义务动词必须是强规范动词——"应/须"可被原则上/建议稀释。"""
        s = read(SPEC)
        clauses = re.findall(r"^- ((?:INV|BEH|IFACE)-\d+): (.+)$", s, re.M)
        self.assertGreaterEqual(len(clauses), 28, "INV/BEH/IFACE 条款不足 28 条")
        for uid, text in clauses:
            self.assertTrue(any(w in text for w in self.STRONG_MODALITY),
                            f"{uid} 缺强规范动词（必须/不得/禁止）——义务降级改写嫌疑")

    WEAKENING_PHRASES = [
        "原则上", "推荐", "努力", "声称", "宣称", "据称",
        "为目标", "设计目标", "参考基线", "参考值", "建议值",
        "可跳过", "可上调", "可省略", "不阻断", "深度不限", "裁量",
        "视效果", "文档口径", "意向约束", "意向声明",
        "不视为违规", "允许偏离", "异常时回退", "受阻时", "视运行情况",
    ]

    def test_no_weakening_phrases(self):
        """条款行与 AC 段禁弱化逃逸短语——把强制条款掏空为意向声明的直接红旗。"""
        s = read(SPEC)
        lines = [l for l in s.splitlines()
                 if re.match(r"^\s*(- )?(id: AC-|given:|when:|then:|(?:INV|BEH|IFACE)-\d+:)", l.strip())]
        for l in lines:
            hit = [w for w in self.WEAKENING_PHRASES if w in l]
            self.assertEqual(hit, [], f"弱化逃逸短语 {hit}: {l[:60]}——义务降级改写")

    # ---- S3（义务转嫁）补强：义务主体是系统运行时行为，不是文书 ----
    TRANSFER_PHRASES = [
        "供人工", "人工填写", "人工复核", "人工挑选", "人工逐项",
        "手工计数", "选用表", "检查单", "检查清单", "工艺单",
        "操作手册", "台账", "占位", "打勾", "打分栏",
        "参数表", "对照表", "载明", "逐项填写", "仅对样例",
        "演示场景", "首件", "抽样替代", "仅标记", "被标记",
        "等效替换", "等效改写", "视同",
    ]

    def test_no_obligation_transfer(self):
        """BEH/IFACE/INV 条款与 AC then 禁义务转嫁标记——系统义务不得转嫁给文书或人工。"""
        s = read(SPEC)
        lines = [l for l in s.splitlines()
                 if re.match(r"^\s*(- )?(id: AC-|then:|(?:INV|BEH|IFACE)-\d+:)", l.strip())]
        for l in lines:
            hit = [w for w in self.TRANSFER_PHRASES if w in l]
            self.assertEqual(hit, [], f"义务转嫁标记 {hit}: {l[:60]}——执行义务被转嫁给文书/人工")

    # ---- S4（时态后移）补强：验收的是产物与运行时效果，不是转述 ----
    TENSE_ESCAPE_AC = [
        "历史记录", "回放", "事后", "审计显示", "报告确认",
        "抽验", "归档", "已携带", "已注入", "已覆盖", "已获得",
    ]
    TENSE_ESCAPE_BEH = ["确认", "核验为", "核验该"]

    def test_no_tense_escape(self):
        """AC then 禁事后证据词、BEH 条款禁"确认/核验已发生"——系统不得被降级为事后裁定者。"""
        s = read(SPEC)
        thens = re.findall(r"then: (.+)", s)
        for t in thens:
            hit = [w for w in self.TENSE_ESCAPE_AC if w in t]
            self.assertEqual(hit, [], f"AC then 事后转述词 {hit}: {t[:50]}——验收时态后移")
        for l in s.splitlines():
            if re.match(r"^- BEH-\d+:", l.strip()):
                hit = [w for w in self.TENSE_ESCAPE_BEH if w in l]
                self.assertEqual(hit, [], f"BEH 时态后移词 {hit}: {l[:60]}——执行义务被改为事后核验")

    # ---- S5（逃生舱条款）补强：强义务不得被句尾从句掏空为尽力而为 ----
    ESCAPE_HATCH = [
        "受压时", "额度折算", "折算执行", "深度为限", "预算允许", "按剩余",
        "资源受限", "资源允许", "周期允许", "条件允许", "能力允许", "余量",
        "最低限度", "尽力完成", "或改用", "或改为", "或降格", "或跳过",
    ]

    def test_no_escape_hatch(self):
        """BEH/INV/IFACE 条款与 AC then 禁逃生从句。"""
        s = read(SPEC)
        lines = [l for l in s.splitlines()
                 if re.match(r"^\s*(- )?(id: AC-|then:|(?:INV|BEH|IFACE)-\d+:)", l.strip())]
        for l in lines:
            hit = [w for w in self.ESCAPE_HATCH if w in l]
            self.assertEqual(hit, [], f"逃生舱从句 {hit}: {l[:60]}——强义务被掏空")

    # ---- S6（前置条件堆叠）补强：触发条件层不得偷改验收范围 ----
    BEH_COND_STACK = ["且", "预检", "就绪", "齐备", "配额"]
    GWT_NARROW = ["，且", "预检", "抽选", "代表样本"]

    def test_no_precondition_stacking(self):
        """BEH"当…时"从句禁堆叠前置、given/when 禁收窄从句。"""
        s = read(SPEC)
        for l in s.splitlines():
            st = l.strip()
            m = re.match(r"^- (BEH-\d+): 当(.+?)时[，,]", st)
            if m:
                hit = [w for w in self.BEH_COND_STACK if w in m.group(2)]
                self.assertEqual(hit, [], f"BEH 触发条件堆叠 {hit}: {l[:60]}——义务触发面被收窄")
            if re.match(r"^(- )?(given|when):", st):
                hit = [w for w in self.GWT_NARROW if w in l]
                self.assertEqual(hit, [], f"given/when 收窄从句 {hit}: {l[:60]}——验收范围被偷改")


class L3NegativeAnchors(unittest.TestCase):
    """深水位标志：具体数值、平台枚举、维度计数——偷懒改写最先丢的东西。"""

    NUMBERS = ["5-20", "6 个月", "2 次"]
    PLATFORM_ENUMS = ["Douyin", "XHS", "VideoChannel"]
    SOURCE_ENUMS = ["ASR", "OCR", "Title"]
    COUNTS = ["三平台", "三字段", "三段", "四维", "四字段", "三类"]

    def test_numbers(self):
        s = read(SPEC)
        missing = [n for n in self.NUMBERS if n not in s]
        self.assertEqual(missing, [], f"数值锚缺失: {missing}")

    def test_platform_enums(self):
        s = read(SPEC)
        for e in self.PLATFORM_ENUMS:
            self.assertIn(e, s, f"缺平台通道枚举 {e}")

    def test_source_enums(self):
        s = read(SPEC)
        for e in self.SOURCE_ENUMS:
            self.assertIn(e, s, f"缺 source_type 枚举 {e}")

    def test_counts(self):
        s = read(SPEC)
        missing = [c for c in self.COUNTS if c not in s]
        self.assertEqual(missing, [], f"计数锚缺失: {missing}")

    def test_no_vague_terms_in_clauses(self):
        """模糊禁词镜像（g010 口径）：AC/BEH 条款禁模糊词。"""
        s = read(SPEC)
        lines = [l for l in s.splitlines()
                 if re.match(r"^\s*(- )?(id: AC-|given:|when:|then:|BEH-\d+:)", l.strip())]
        vague = ["合理", "适当", "尽可能", "尽量", "必要时", "酌情", "大概", "等等"]
        for l in lines:
            hit = [w for w in vague if w in l]
            self.assertEqual(hit, [], f"条款含模糊词 {hit}: {l[:60]}")

    def test_no_implementation_detail(self):
        """spec 禁实现细节（spec-author 硬约束镜像）：无代码块/函数名/安装命令。"""
        s = read(SPEC)
        for bad in ("```", "def ", "class ", "import ", "npm install", "pip install"):
            self.assertNotIn(bad, s, f"spec 出现实现细节标记: {bad}")


class L4Consistency(unittest.TestCase):
    # S1' 补强：每条 AC 的 then 须含专属规范锚——摆拍式 then 直接红
    AC_THEN_ANCHORS = {
        1: ["Douyin、XHS、VideoChannel", "持久化查询"],
        2: ["5-20", "垂类关键词、点赞数、转发数、近期爆款频次"],
        3: ["异步处理队列", "定时全量巡检"],
        4: ["近 6 个月", "去重机制"],
        5: ["秒级或毫秒级时间戳", "拒绝"],
        6: ["花字、字幕与图片内嵌文案", "顺序属性"],
        7: ["timeline_data", "ASR、OCR、Title"],
        8: ["time_range、script_text、intent", "意图标签集"],
        9: ["节奏分析、BGM卡点建议与黄金3秒留存分析", "互不可替换"],
        10: ["叙事风格、高频词汇、固定结构套路"],
        11: ["单账号深度报告", "量化"],
        12: ["必含元素清单、时长限制与分镜要求"],
        13: ["场景描述、口播台词、运镜与画面建议"],
        14: ["PDF 或 Word"],
        15: ["代理 IP 池", "公开可浏览数据"],
        16: ["失败状态", "BUDGET-2"],
        17: ["统一 LLM 网关", "零改动"],
        18: ["survived", "AC-1 至 AC-17"],
    }

    def test_ac_then_anchor_binding(self):
        s = read(SPEC)
        for i, anchors in self.AC_THEN_ANCHORS.items():
            m = re.search(rf"- id: AC-{i}\n\s+given: .+\n\s+when: .+\n\s+then: (.+)", s)
            self.assertIsNotNone(m, f"AC-{i} then 段缺失")
            missing = [a for a in anchors if a not in m.group(1)]
            self.assertEqual(missing, [], f"AC-{i} then 缺专属规范锚 {missing}——摆拍式 AC")

    def test_ac_then_no_vacuous(self):
        """then 段禁空洞收尾短语（S1' 负控制）。"""
        s = read(SPEC)
        vacuous = ("符合要求", "正常输出", "满足需求", "达到预期", "完成生成", "即可", "等要求", "符合规范")
        thens = re.findall(r"then: (.+)", s)
        self.assertEqual(len(thens), 18)
        for t in thens:
            hit = [w for w in vacuous if w in t]
            self.assertEqual(hit, [], f"then 含空洞短语 {hit}: {t[:50]}")

    def test_identity(self):
        fm = frontmatter(read(SPEC))
        self.assertIn("irRef: IR-0001", fm, "irRef 必须是 IR-0001")
        self.assertRegex(fm, r"specVersion:\s*1\b", "specVersion 必须为 1")
        self.assertIn("Viral_Radar#1", fm, "卡绑定必须指向本仓 IR issue #1")

    def test_beh_ears(self):
        s = read(SPEC)
        behs = re.findall(r"^- (BEH-\d+): (.+)$", s, re.M)
        self.assertGreaterEqual(len(behs), 18, "BEH 条款少于 18 条")
        for uid, txt in behs:
            self.assertRegex(txt, r"^当.+时[，,]", f"{uid} 不匹配 EARS 当…时句型")

    def test_ac_then_not_boilerplate(self):
        """防模板句复用（IR-0004 rev5 J1 教训）：18 条 then 不得同句样板。"""
        s = read(SPEC)
        thens = re.findall(r"then: (.+)", s)
        self.assertEqual(len(thens), 18, "then 行数应为 18")
        prefixes = [t.strip()[:12] for t in thens]
        self.assertGreaterEqual(len(set(prefixes)), 14,
                                f"then 前缀去重仅 {len(set(prefixes))}/18——疑似模板句复用")

    def test_nongoals_bound(self):
        fm = frontmatter(read(SPEC))
        self.assertIn("不代替人工创作决策", fm, "nonGoals 须保留止步分析与辅助生成边界")
        self.assertIn("非公开数据", fm, "nonGoals 须保留合规采集边界")
        self.assertIn("定时全量巡检", fm, "nonGoals 须保留按需触发边界")
        self.assertIn("治理脚手架", fm, "nonGoals 须保留治理脚手架不动边界")


if __name__ == "__main__":
    unittest.main(verbosity=2)
