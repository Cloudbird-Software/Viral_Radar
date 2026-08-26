"""report_web.py —— 报告在线阅读与 PDF 导出（spec AC-14 / BEH-15）。

在线阅读 = render_html（纯标准库，无外部依赖）；PDF 导出 = export_pdf（惰性导入
reportlab，导出内容与在线版本同源——两者共用同一份 _lines 文本装配，保证一致）。
"""

import html as _html
import io


class ReportExporter:
    """报告展示/导出唯一入口（HTML 面零依赖，PDF 面惰性加载）。"""

    def render_html(self, report: dict) -> str:
        sections = [
            ("概览", self._overview_lines(report)),
            ("视频级拆解详情", self._detail_lines(report)),
            ("结构化大纲", self._outline_lines(report)),
            ("爆款逻辑总结", self._conclusion_lines(report)),
        ]
        body = []
        for title, lines in sections:
            body.append(f"<h2>{_html.escape(title)}</h2>")
            body.append("<ul>")
            body.extend(f"<li>{_html.escape(line)}</li>" for line in lines)
            body.append("</ul>")
        return (
            '<!DOCTYPE html><html lang="zh"><head><meta charset="utf-8">'
            f"<title>账号分析报告</title></head><body>{''.join(body)}</body></html>"
        )

    def export_pdf(self, report: dict) -> bytes:
        from reportlab.lib.pagesizes import A4  # 惰性：HTML 面与测试驱动零依赖
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.cidfonts import UnicodeCIDFont
        from reportlab.pdfgen import canvas

        pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        pdf.setFont("STSong-Light", 12)
        y = 780
        for line in self._lines(report):
            pdf.drawString(60, y, line[:60])
            y -= 20
            if y < 60:
                pdf.showPage()
                pdf.setFont("STSong-Light", 12)
                y = 780
        pdf.save()
        return buffer.getvalue()

    def _lines(self, report: dict) -> list[str]:
        return (
            ["账号分析报告（在线阅读与导出同源）"]
            + self._overview_lines(report)
            + ["——视频级拆解——"]
            + self._detail_lines(report)
            + ["——结构化大纲——"]
            + self._outline_lines(report)
            + ["——爆款逻辑总结——"]
            + self._conclusion_lines(report)
        )

    def _overview_lines(self, report: dict) -> list[str]:
        o = report.get("overview") or {}
        return [
            f"账号：{o.get('account_id', '')}",
            f"名称：{o.get('name', '')}",
            f"粉丝数：{o.get('followers', 0)}",
            f"样本数：{o.get('video_count', 0)}",
            f"平台：{o.get('platform', '')}",
        ]

    def _detail_lines(self, report: dict) -> list[str]:
        lines = []
        for video in report.get("video_details") or []:
            for s in video["slices"]:
                lines.append(
                    f"{video['content_id']} {s['time_range']} [{s['intent']}] {s['script_text']}"
                )
        return lines

    def _outline_lines(self, report: dict) -> list[str]:
        lines = []
        for section in (report.get("outline") or {}).get("sections") or []:
            for beat in section["beats"]:
                lines.append(f"{section['content_id']} {beat['time_range']} -> {beat['hook']}")
        return lines

    def _conclusion_lines(self, report: dict) -> list[str]:
        c = report.get("conclusion") or {}
        patterns = "；".join("→".join(p.get("sequence") or []) for p in c.get("patterns") or [])
        return list(
            {
                f"叙事风格：{c.get('style', '')}",
                f"高频词汇：{'、'.join(c.get('top_words') or [])}",
                f"固定结构套路：{patterns}",
            }
        )
