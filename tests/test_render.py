"""render 模块单元测试。"""

from __future__ import annotations

import unittest
from typing import List

from syllabus.model import SyllabusError, Week
from syllabus.render import render_html, row_height_mm


def make_weeks(count: int) -> List[Week]:
    return [
        Week(week=index, content="第 %d 周内容" % index, date="9/%d" % index)
        for index in range(1, count + 1)
    ]


class RenderHtmlTest(unittest.TestCase):
    def test_basic_document(self) -> None:
        page = render_html(make_weeks(3))
        self.assertTrue(page.startswith("<!doctype html>"))
        self.assertIn("A4 portrait", page)
        self.assertIn("教学进度表", page)

    def test_headers(self) -> None:
        page = render_html(make_weeks(3))
        for label in ("周次", "日期", "教学内容", "作业"):
            self.assertIn("<th>%s</th>" % label, page)

    def test_rows(self) -> None:
        page = render_html(make_weeks(3), rows=8)
        self.assertIn('<td class="week">1</td>', page)
        self.assertIn("第 3 周内容", page)
        self.assertEqual(page.count('<tr class="empty">'), 5)

    def test_pagination(self) -> None:
        page = render_html(make_weeks(25), rows=10)
        self.assertEqual(page.count('<section class="sheet">'), 3)
        self.assertEqual(page.count("<th>周次</th>"), 3)
        self.assertIn("第 3 / 3 页", page)

    def test_second_page_rows(self) -> None:
        page = render_html(make_weeks(25), rows=10)
        parts = page.split('<section class="sheet">')
        self.assertIn('<td class="week">11</td>', parts[2])
        self.assertIn('<td class="week">20</td>', parts[2])
        self.assertNotIn('<td class="week">10</td>', parts[2])

    def test_meta(self) -> None:
        page = render_html(
            make_weeks(3), term="2026 秋季学期", subject="数学", group="初一2班"
        )
        self.assertIn("2026 秋季学期 · 数学 · 初一2班", page)

    def test_empty_meta(self) -> None:
        page = render_html(make_weeks(3))
        self.assertNotIn("2026 秋季学期", page)

    def test_title_escaped(self) -> None:
        page = render_html(make_weeks(3), title="<进度>")
        self.assertIn("&lt;进度&gt;", page)

    def test_footer(self) -> None:
        page = render_html(make_weeks(3))
        self.assertIn("共 3 条进度", page)
        self.assertIn("周次 1~3", page)

    def test_empty_weeks(self) -> None:
        with self.assertRaises(SyllabusError):
            render_html([])

    def test_non_week(self) -> None:
        with self.assertRaises(SyllabusError):
            render_html(["周"])  # type: ignore[list-item]

    def test_non_sequence(self) -> None:
        with self.assertRaises(SyllabusError):
            render_html("周")  # type: ignore[arg-type]

    def test_empty_title(self) -> None:
        with self.assertRaises(SyllabusError):
            render_html(make_weeks(3), title=" ")

    def test_non_text_meta(self) -> None:
        with self.assertRaises(SyllabusError):
            render_html(make_weeks(3), term=1)  # type: ignore[arg-type]

    def test_long_meta(self) -> None:
        with self.assertRaises(SyllabusError):
            render_html(make_weeks(3), group="字" * 21)

    def test_bad_rows(self) -> None:
        with self.assertRaises(SyllabusError):
            render_html(make_weeks(3), rows=5)

    def test_row_height(self) -> None:
        self.assertEqual(row_height_mm(8), 12.0)
        self.assertAlmostEqual(row_height_mm(30), 7.0)
        with self.assertRaises(SyllabusError):
            row_height_mm(7)


if __name__ == "__main__":
    unittest.main()
