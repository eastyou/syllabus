"""把教学进度渲染成可打印的 A4 纵向表格。"""

from __future__ import annotations

import html
from typing import List, Sequence

from .model import (
    DEFAULT_ROWS,
    SyllabusError,
    Week,
    check_rows,
    paginate,
    total_weeks,
)

PAGE_WIDTH_MM = 210.0
PAGE_HEIGHT_MM = 297.0
COLUMNS = (
    ("周次", "14mm"),
    ("日期", "30mm"),
    ("教学内容", "86mm"),
    ("作业", "50mm"),
)


def _num(value: float) -> str:
    text = "%.1f" % value
    return text.rstrip("0").rstrip(".") if "." in text else text


def row_height_mm(rows: int) -> float:
    """按每页行数计算行高。"""
    size = check_rows(rows)
    return min(12.0, 210.0 / size)


def _table_markup(weeks: Sequence[Week], start: int, rows: int) -> str:
    cols = "".join('<col style="width:%s">' % width for _, width in COLUMNS)
    heads = "".join("<th>%s</th>" % label for label, _ in COLUMNS)
    body: List[str] = []
    for offset in range(rows):
        position = start + offset
        if offset < len(weeks):
            item = weeks[offset]
            body.append(
                "<tr>"
                '<td class="week">%d</td>'
                '<td class="date">%s</td>'
                '<td class="content">%s</td>'
                '<td class="homework">%s</td>'
                "</tr>"
                % (
                    item.week,
                    html.escape(item.date),
                    html.escape(item.content),
                    html.escape(item.homework),
                )
            )
        else:
            body.append(
                '<tr class="empty"><td class="week"></td><td></td><td></td><td></td></tr>'
            )
    return (
        '<table class="plan"><colgroup>%s</colgroup>'
        "<thead><tr>%s</tr></thead><tbody>%s</tbody></table>"
        % (cols, heads, "".join(body))
    )


def render_html(
    weeks: Sequence[Week],
    title: str = "教学进度表",
    rows: int = DEFAULT_ROWS,
    term: str = "",
    group: str = "",
    subject: str = "",
) -> str:
    """生成完整 HTML：进度跨页，每页重复表头。"""
    if not isinstance(weeks, (list, tuple)) or not weeks:
        raise SyllabusError("进度列表不能为空")
    for item in weeks:
        if not isinstance(item, Week):
            raise SyllabusError("进度列表里出现了非 Week 对象")
    if not isinstance(title, str) or not title.strip():
        raise SyllabusError("标题不能为空")
    for value, label in ((term, "学期"), (group, "班级"), (subject, "学科")):
        if not isinstance(value, str):
            raise SyllabusError("%s必须是文本" % label)
        if len(value.strip()) > 20:
            raise SyllabusError("%s最多 20 个字符" % label)

    size = check_rows(rows)
    pages = paginate(weeks, size)
    total = len(pages)
    height = row_height_mm(size)
    span = total_weeks(weeks)

    meta_parts = [
        value.strip()
        for value in (term, subject, group)
        if value.strip()
    ]
    meta = " · ".join(meta_parts)

    sheets: List[str] = []
    for page_index, page_weeks in enumerate(pages):
        start = page_index * size
        label = html.escape(title.strip())
        if page_index:
            label += "（续）"
        head = (
            '<header class="head"><h1>%s</h1>'
            '<p class="meta">%s</p></header>'
            % (label, html.escape(meta) if meta else "&nbsp;")
        )
        foot = (
            '<footer class="foot"><span>共 %d 条进度 · 周次 1~%d</span>'
            "<span>第 %d / %d 页</span></footer>" % (len(weeks), span, page_index + 1, total)
        )
        sheets.append(
            '<section class="sheet">%s%s%s</section>'
            % (head, _table_markup(page_weeks, start, size), foot)
        )

    toolbar = (
        '<div class="toolbar"><strong>%s</strong>'
        "<span>%s · %d 条进度 · 每页 %d 条 · 共 %d 页</span></div>"
        % (
            html.escape(title.strip()),
            html.escape(meta) if meta else "教学进度",
            len(weeks),
            size,
            total,
        )
    )

    return (
        "<!doctype html>\n"
        '<html lang="zh-CN">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        "<title>%s</title>\n<style>%s</style>\n</head>\n<body>\n%s\n%s\n</body>\n</html>\n"
        % (
            html.escape(title.strip()),
            _style(height),
            toolbar,
            "\n".join(sheets),
        )
    )


def _style(height: float) -> str:
    template = """
  :root { color-scheme: light; }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    padding: 8mm 0 12mm;
    background: #e2e8f0;
    color: #0f172a;
    font-family: "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;
  }
  .toolbar {
    width: 210mm;
    margin: 0 auto 6mm;
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    color: #334155;
    font-size: 13px;
  }
  .toolbar strong { font-size: 15px; letter-spacing: 1px; }
  .toolbar span { color: #64748b; font-size: 12px; }
  .sheet {
    width: 210mm;
    height: 297mm;
    margin: 0 auto 8mm;
    padding: 14mm 15mm 10mm;
    background: #fff;
    box-shadow: 0 6px 22px rgba(15, 23, 42, 0.14);
    display: flex;
    flex-direction: column;
    page-break-after: always;
    break-after: page;
    overflow: hidden;
  }
  .sheet:last-child { page-break-after: auto; break-after: auto; }
  .head { text-align: center; margin-bottom: 4mm; }
  .head h1 {
    margin: 0 0 1.5mm;
    font-size: 20pt;
    font-weight: 600;
    letter-spacing: 4pt;
  }
  .head .meta { margin: 0; font-size: 10pt; color: #475569; }
  table.plan {
    width: 180mm;
    border-collapse: collapse;
    table-layout: fixed;
  }
  table.plan th,
  table.plan td {
    border: 0.25mm solid #94a3b8;
    padding: 1mm 1.5mm;
    font-size: 9.5pt;
    vertical-align: middle;
    overflow-wrap: anywhere;
  }
  table.plan th {
    height: 8mm;
    background: #f1f5f9;
    font-weight: 600;
    text-align: center;
  }
  table.plan td { height: __ROW_HEIGHT__mm; }
  table.plan td.week { text-align: center; font-weight: 600; }
  table.plan td.date { text-align: center; color: #475569; }
  table.plan td.content { text-align: left; }
  table.plan td.homework { text-align: left; color: #334155; }
  table.plan tr.empty td { color: #cbd5e1; }
  .foot {
    margin-top: auto;
    padding-top: 2mm;
    display: flex;
    justify-content: space-between;
    font-size: 8pt;
    color: #64748b;
    border-top: 0.2mm solid #e2e8f0;
  }
  @page { size: A4 portrait; margin: 0; }
  @media print {
    body { background: #fff; padding: 0; }
    .toolbar { display: none; }
    .sheet { margin: 0; box-shadow: none; }
    * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  }
"""
    return template.replace("__ROW_HEIGHT__", _num(height))
