"""model 模块单元测试。"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import List

from syllabus.model import (
    MAX_CONTENT,
    MAX_HOMEWORK,
    MAX_WEEK,
    Week,
    SyllabusError,
    check_rows,
    format_weeks,
    load_weeks,
    paginate,
    parse_csv,
    total_weeks,
)

SAMPLE = """周次,日期,教学内容,作业
1,9/1-9/5,第一章 集合,练习 1.1
2,9/8-9/12,第二章 函数,练习 2.1
3,9/15-9/19,函数图像,练习 2.2
"""


def make_weeks(count: int) -> List[Week]:
    return [
        Week(week=index, content="第 %d 周内容" % index)
        for index in range(1, count + 1)
    ]


class ParseCsvTest(unittest.TestCase):
    def test_sample(self) -> None:
        weeks = parse_csv(SAMPLE)
        self.assertEqual(len(weeks), 3)
        self.assertEqual(weeks[0].week, 1)
        self.assertEqual(weeks[0].date, "9/1-9/5")
        self.assertEqual(weeks[0].homework, "练习 1.1")

    def test_header_variants(self) -> None:
        for header in ("周次,日期,教学内容,作业", "周,日期,内容,作业", "星期,时间,内容,作业"):
            weeks = parse_csv(header + "\n1,9/1,集合,练习\n")
            self.assertEqual(len(weeks), 1, header)

    def test_without_header(self) -> None:
        weeks = parse_csv("1,9/1,集合,练习\n")
        self.assertEqual(weeks[0].homework, "练习")

    def test_three_columns(self) -> None:
        weeks = parse_csv("1,9/1,集合\n")
        self.assertEqual(weeks[0].homework, "")

    def test_two_columns(self) -> None:
        weeks = parse_csv("1,集合\n")
        self.assertEqual(weeks[0].content, "集合")
        self.assertEqual(weeks[0].date, "")

    def test_too_many_columns(self) -> None:
        with self.assertRaises(SyllabusError) as ctx:
            parse_csv("1,9/1,集合,练习,备注\n")
        self.assertIn("第 1 行", str(ctx.exception))

    def test_too_few_columns(self) -> None:
        with self.assertRaises(SyllabusError):
            parse_csv("1\n")

    def test_non_numeric_week(self) -> None:
        with self.assertRaises(SyllabusError) as ctx:
            parse_csv("第一周,9/1,集合\n")
        self.assertIn("第 1 行", str(ctx.exception))

    def test_week_zero(self) -> None:
        with self.assertRaises(SyllabusError):
            parse_csv("0,9/1,集合\n")

    def test_week_too_large(self) -> None:
        with self.assertRaises(SyllabusError):
            parse_csv("%d,9/1,集合\n" % (MAX_WEEK + 1))

    def test_duplicate_week(self) -> None:
        with self.assertRaises(SyllabusError) as ctx:
            parse_csv("1,9/1,集合\n1,9/8,函数\n")
        self.assertIn("第 2 行", str(ctx.exception))

    def test_empty_content(self) -> None:
        with self.assertRaises(SyllabusError):
            parse_csv("1,9/1,,练习\n")

    def test_content_too_long(self) -> None:
        with self.assertRaises(SyllabusError):
            parse_csv("1,9/1,%s,练习\n" % ("字" * (MAX_CONTENT + 1)))

    def test_homework_too_long(self) -> None:
        with self.assertRaises(SyllabusError):
            parse_csv("1,9/1,集合,%s\n" % ("字" * (MAX_HOMEWORK + 1)))

    def test_empty_text(self) -> None:
        with self.assertRaises(SyllabusError):
            parse_csv("\n\n")

    def test_non_text(self) -> None:
        with self.assertRaises(SyllabusError):
            parse_csv(123)  # type: ignore[arg-type]

    def test_bom(self) -> None:
        self.assertEqual(len(parse_csv("\ufeff" + SAMPLE)), 3)

    def test_load_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "syllabus.csv"
            path.write_text(SAMPLE, encoding="utf-8")
            self.assertEqual(len(load_weeks(path)), 3)

    def test_load_gbk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "syllabus.csv"
            path.write_bytes(SAMPLE.encode("gbk"))
            self.assertEqual(load_weeks(path)[0].content, "第一章 集合")

    def test_unknown_encoding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "syllabus.csv"
            path.write_bytes(b"\xff\xff\xff")
            with self.assertRaises(SyllabusError):
                load_weeks(path)

    def test_missing_file(self) -> None:
        with self.assertRaises(FileNotFoundError):
            load_weeks("/tmp/definitely-missing-syllabus.csv")


class WeekTest(unittest.TestCase):
    def test_trim(self) -> None:
        week = Week(week=1, content=" 集合 ", date=" 9/1 ", homework=" 练习 ")
        self.assertEqual(week.content, "集合")
        self.assertEqual(week.date, "9/1")
        self.assertEqual(week.homework, "练习")

    def test_empty_content(self) -> None:
        with self.assertRaises(SyllabusError):
            Week(week=1, content=" ")

    def test_non_text(self) -> None:
        with self.assertRaises(SyllabusError):
            Week(week=1, content=1)  # type: ignore[arg-type]

    def test_bool_week(self) -> None:
        with self.assertRaises(SyllabusError):
            Week(week=True, content="集合")  # type: ignore[arg-type]

    def test_date_too_long(self) -> None:
        with self.assertRaises(SyllabusError):
            Week(week=1, content="集合", date="字" * 21)


class PaginationTest(unittest.TestCase):
    def test_paginate(self) -> None:
        pages = paginate(make_weeks(25), rows=10)
        self.assertEqual([len(page) for page in pages], [10, 10, 5])

    def test_paginate_empty(self) -> None:
        with self.assertRaises(SyllabusError):
            paginate([])

    def test_paginate_non_week(self) -> None:
        with self.assertRaises(SyllabusError):
            paginate(["周"])  # type: ignore[list-item]

    def test_check_rows(self) -> None:
        self.assertEqual(check_rows(8), 8)
        self.assertEqual(check_rows(30), 30)
        for value in (7, 31, True, "10"):
            with self.assertRaises(SyllabusError):
                check_rows(value)  # type: ignore[arg-type]

    def test_total_weeks(self) -> None:
        self.assertEqual(total_weeks(make_weeks(18)), 18)

    def test_format_roundtrip(self) -> None:
        weeks = parse_csv(SAMPLE)
        again = parse_csv(format_weeks(weeks))
        self.assertEqual(again, weeks)

    def test_format_empty(self) -> None:
        with self.assertRaises(SyllabusError):
            format_weeks([])

    def test_format_non_week(self) -> None:
        with self.assertRaises(SyllabusError):
            format_weeks(["周"])  # type: ignore[list-item]


if __name__ == "__main__":
    unittest.main()
