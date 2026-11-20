"""syllabus：A4 可打印学期教学进度表。"""

from __future__ import annotations

from .model import (
    DEFAULT_ROWS,
    MAX_CONTENT,
    MAX_DATE,
    MAX_HOMEWORK,
    MAX_ROWS,
    MAX_WEEK,
    MIN_ROWS,
    MIN_WEEK,
    SyllabusError,
    Week,
    check_rows,
    format_weeks,
    load_weeks,
    paginate,
    parse_csv,
    total_weeks,
)
from .render import render_html, row_height_mm

__version__ = "0.1.0"

__all__ = [
    "DEFAULT_ROWS",
    "MAX_CONTENT",
    "MAX_DATE",
    "MAX_HOMEWORK",
    "MAX_ROWS",
    "MAX_WEEK",
    "MIN_ROWS",
    "MIN_WEEK",
    "SyllabusError",
    "Week",
    "check_rows",
    "format_weeks",
    "load_weeks",
    "paginate",
    "parse_csv",
    "render_html",
    "row_height_mm",
    "total_weeks",
    "__version__",
]
