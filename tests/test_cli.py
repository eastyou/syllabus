"""命令行入口单元测试。"""

from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from typing import List

from syllabus.cli import main

SAMPLE = """周次,日期,教学内容,作业
1,9/1,集合,练习 1.1
2,9/8,函数,练习 2.1
"""


class CliTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.weeks = self.root / "weeks.csv"
        self.weeks.write_text(SAMPLE, encoding="utf-8")
        self.target = self.root / "plan.html"

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def run_cli(self, argv: List[str]) -> int:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            return main(argv)

    def test_generate(self) -> None:
        code = self.run_cli(["-i", str(self.weeks), "-o", str(self.target)])
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertIn("集合", page)
        self.assertIn("第 1 / 1 页", page)

    def test_meta_options(self) -> None:
        code = self.run_cli(
            [
                "-i", str(self.weeks), "-o", str(self.target),
                "--term", "2026 秋季学期", "--subject", "数学",
                "--group", "初一2班", "--title", "数学进度",
            ]
        )
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertIn("2026 秋季学期", page)
        self.assertIn("初一2班", page)
        self.assertIn("数学进度", page)

    def test_rows(self) -> None:
        code = self.run_cli(
            ["-i", str(self.weeks), "-o", str(self.target), "--rows", "8"]
        )
        self.assertEqual(code, 0)
        page = self.target.read_text(encoding="utf-8")
        self.assertEqual(page.count('<tr class="empty">'), 6)

    def test_invalid_week(self) -> None:
        bad = self.root / "bad.csv"
        bad.write_text("0,9/1,集合\n", encoding="utf-8")
        code = self.run_cli(["-i", str(bad), "-o", str(self.target)])
        self.assertEqual(code, 2)
        self.assertFalse(self.target.exists())

    def test_invalid_rows(self) -> None:
        code = self.run_cli(
            ["-i", str(self.weeks), "-o", str(self.target), "--rows", "5"]
        )
        self.assertEqual(code, 2)

    def test_missing_file(self) -> None:
        code = self.run_cli(
            ["-i", str(self.root / "missing.csv"), "-o", str(self.target)]
        )
        self.assertEqual(code, 1)

    def test_missing_input_argument(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stderr(io.StringIO()):
                main(["-o", str(self.target)])
        self.assertEqual(ctx.exception.code, 2)

    def test_help(self) -> None:
        with self.assertRaises(SystemExit) as ctx:
            with contextlib.redirect_stdout(io.StringIO()):
                main(["--help"])
        self.assertEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
