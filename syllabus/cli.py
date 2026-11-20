"""命令行入口：生成可打印的学期教学进度表。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Sequence

from .model import (
    DEFAULT_ROWS,
    MAX_ROWS,
    MIN_ROWS,
    Week,
    SyllabusError,
    load_weeks,
)
from .render import render_html


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="syllabus",
        description="教学进度表：周次 CSV 一键生成 A4 可打印进度表",
    )
    parser.add_argument("--version", action="version", version="syllabus 0.1.0")
    parser.add_argument(
        "-i", "--input", required=True, help="进度 CSV（周次,日期,教学内容,作业）"
    )
    parser.add_argument(
        "-o", "--output", default="教学进度.html", help="输出 HTML 路径"
    )
    parser.add_argument(
        "--rows",
        type=int,
        default=DEFAULT_ROWS,
        help="每页行数 %d~%d，默认 %d" % (MIN_ROWS, MAX_ROWS, DEFAULT_ROWS),
    )
    parser.add_argument("--term", default="", help="学期，例如 2026 秋季学期")
    parser.add_argument("--group", default="", help="班级")
    parser.add_argument("--subject", default="", help="学科")
    parser.add_argument("--title", default="教学进度表", help="页面标题")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        weeks: List[Week] = load_weeks(args.input)
        page = render_html(
            weeks,
            title=args.title,
            rows=args.rows,
            term=args.term,
            group=args.group,
            subject=args.subject,
        )
    except SyllabusError as exc:
        print("错误: %s" % exc, file=sys.stderr)
        return 2
    except OSError as exc:
        print("错误: 读取进度失败: %s" % exc, file=sys.stderr)
        return 1

    try:
        Path(args.output).write_text(page, encoding="utf-8")
    except OSError as exc:
        print("错误: 写入文件失败: %s" % exc, file=sys.stderr)
        return 1

    pages = (len(weeks) + args.rows - 1) // args.rows
    print(
        "已生成 %s：%d 条进度，每页 %d 条，共 %d 页"
        % (args.output, len(weeks), args.rows, pages)
    )
    print("用浏览器打开后按 Ctrl/Cmd + P，纸张选 A4 纵向即可打印")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
