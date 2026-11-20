"""教学进度数据模型：周次 CSV 解析、字段校验与分页。"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence, Tuple, Union

MIN_WEEK = 1
MAX_WEEK = 30
MAX_DATE = 20
MAX_CONTENT = 60
MAX_HOMEWORK = 40
MIN_ROWS = 8
MAX_ROWS = 30
DEFAULT_ROWS = 22

WEEK_HEADERS = {"周次", "周", "星期"}
DATE_HEADERS = {"日期", "时间", "起止日期"}


class SyllabusError(ValueError):
    """进度数据或参数不合法。"""


@dataclass(frozen=True)
class Week:
    """一行教学进度：周次、日期、教学内容与作业。"""

    week: int
    content: str
    date: str = ""
    homework: str = ""

    def __post_init__(self) -> None:
        if isinstance(self.week, bool) or not isinstance(self.week, int):
            raise SyllabusError("周次必须是整数")
        if not MIN_WEEK <= self.week <= MAX_WEEK:
            raise SyllabusError(
                "周次必须在 %d~%d 之间，当前是 %d"
                % (MIN_WEEK, MAX_WEEK, self.week)
            )
        content = _clean(self.content, "教学内容")
        if not content:
            raise SyllabusError("教学内容不能为空")
        if len(content) > MAX_CONTENT:
            raise SyllabusError(
                "教学内容最多 %d 个字符，当前 %d 个" % (MAX_CONTENT, len(content))
            )
        date = _clean(self.date, "日期")
        homework = _clean(self.homework, "作业")
        if len(date) > MAX_DATE:
            raise SyllabusError("日期最多 %d 个字符" % MAX_DATE)
        if len(homework) > MAX_HOMEWORK:
            raise SyllabusError("作业最多 %d 个字符" % MAX_HOMEWORK)
        object.__setattr__(self, "content", content)
        object.__setattr__(self, "date", date)
        object.__setattr__(self, "homework", homework)


def _clean(value: str, label: str) -> str:
    if not isinstance(value, str):
        raise SyllabusError("%s必须是文本，当前是 %r" % (label, value))
    return value.strip()


def _decode(data: bytes) -> str:
    if not isinstance(data, (bytes, bytearray)):
        raise SyllabusError("文件内容必须是字节")
    for encoding in ("utf-8-sig", "gbk"):
        try:
            return bytes(data).decode(encoding)
        except UnicodeDecodeError:
            continue
    raise SyllabusError("无法识别文件编码，请另存为 UTF-8 或 GBK 后重试")


def _is_header(cells: Sequence[str]) -> bool:
    if not cells:
        return False
    if cells[0] in WEEK_HEADERS:
        return True
    return len(cells) > 1 and cells[1] in DATE_HEADERS


def parse_csv(text: str, source: str = "输入内容") -> List[Week]:
    """解析进度 CSV：周次,日期,教学内容,作业；表头可选。"""
    if not isinstance(text, str):
        raise SyllabusError("CSV 内容必须是文本")
    text = text.lstrip("\ufeff")
    reader = csv.reader(io.StringIO(text))
    weeks: List[Week] = []
    seen: Dict[int, int] = {}
    header_checked = False
    for line_no, row in enumerate(reader, start=1):
        cells = [cell.strip() for cell in row]
        if not any(cells):
            continue
        if not header_checked:
            header_checked = True
            if _is_header(cells):
                continue
        if len(cells) > 4:
            raise SyllabusError(
                "%s 第 %d 行有 %d 列，最多 4 列（周次,日期,教学内容,作业）"
                % (source, line_no, len(cells))
            )
        if len(cells) < 2:
            raise SyllabusError(
                "%s 第 %d 行至少需要 2 列（周次,教学内容）" % (source, line_no)
            )
        raw_week = cells[0]
        if not raw_week.isdigit():
            raise SyllabusError(
                "%s 第 %d 行周次必须是数字：%s" % (source, line_no, raw_week)
            )
        week = int(raw_week)
        if week in seen:
            raise SyllabusError(
                "%s 第 %d 行与第 %d 行周次重复：%d"
                % (source, line_no, seen[week], week)
            )
        date = cells[1] if len(cells) > 1 else ""
        content = cells[2] if len(cells) > 2 else ""
        homework = cells[3] if len(cells) > 3 else ""
        if len(cells) == 2:
            content, date = date, ""
        try:
            weeks.append(
                Week(week=week, content=content, date=date, homework=homework)
            )
        except SyllabusError as exc:
            raise SyllabusError("%s 第 %d 行：%s" % (source, line_no, exc)) from exc
        seen[week] = line_no
    if not weeks:
        raise SyllabusError("%s 中没有有效的进度记录" % source)
    return weeks


def load_weeks(path: Union[str, Path]) -> List[Week]:
    """读取进度 CSV 文件。"""
    target = Path(path)
    return parse_csv(_decode(target.read_bytes()), source=str(target))


def check_rows(rows: int) -> int:
    """校验每页行数。"""
    if isinstance(rows, bool) or not isinstance(rows, int):
        raise SyllabusError("每页行数必须是整数")
    if not MIN_ROWS <= rows <= MAX_ROWS:
        raise SyllabusError(
            "每页行数必须在 %d~%d 之间，当前是 %d" % (MIN_ROWS, MAX_ROWS, rows)
        )
    return rows


def paginate(weeks: Sequence[Week], rows: int = DEFAULT_ROWS) -> List[List[Week]]:
    """按每页行数分页。"""
    if not isinstance(weeks, (list, tuple)) or not weeks:
        raise SyllabusError("进度列表不能为空")
    for item in weeks:
        if not isinstance(item, Week):
            raise SyllabusError("进度列表里出现了非 Week 对象")
    size = check_rows(rows)
    pages: List[List[Week]] = []
    for start in range(0, len(weeks), size):
        pages.append(list(weeks[start : start + size]))
    return pages


def total_weeks(weeks: Sequence[Week]) -> int:
    """周次跨度，用于页脚统计。"""
    if not isinstance(weeks, (list, tuple)) or not weeks:
        raise SyllabusError("进度列表不能为空")
    return max(item.week for item in weeks)


def format_weeks(weeks: Sequence[Week]) -> str:
    """把进度写回 CSV 文本。"""
    if not isinstance(weeks, (list, tuple)) or not weeks:
        raise SyllabusError("进度列表不能为空")
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(["周次", "日期", "教学内容", "作业"])
    for item in weeks:
        if not isinstance(item, Week):
            raise SyllabusError("进度列表里出现了非 Week 对象")
        writer.writerow([item.week, item.date, item.content, item.homework])
    return buffer.getvalue()
