# syllabus

[![CI](https://github.com/eastyou/syllabus/actions/workflows/ci.yml/badge.svg)](https://github.com/eastyou/syllabus/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-brightgreen.svg)](pyproject.toml)

给老师用的学期教学进度表：把每周的教学内容和作业整理成 CSV，一条命令生成 A4 可打印进度表。**零依赖，不联网，打印即用。**

周次、日期、教学内容、作业四列清清楚楚，行数多了自动分页并重复表头，适合贴在教案本首页或发给学生做学习规划。

## 特性

- **四列进度**：周次、日期、教学内容、作业，一页看清整学期安排
- **自动分页**：`--rows` 设置每页 8~30 条，超出自动分页并重复表头
- **学期信息**：`--term`、`--subject`、`--group` 组合成标题下方的说明行
- **周次校验**：1~30 周、重复周次、非数字周次都会指出具体行号
- **列数宽松**：支持 2~4 列，只写「周次,教学内容」也能生成
- **编码兼容**：UTF-8（含 BOM）与 GBK 自动识别
- **59 个单元测试**：覆盖 CSV 解析、字段校验、分页、渲染与命令行

## 安装

```bash
pip install syllabus
```

也可以直接下载源码，在项目目录里运行：

```bash
python -m syllabus --help
```

## 用法

准备 `进度.csv`：

```csv
周次,日期,教学内容,作业
1,9/1-9/5,第一章 集合,练习 1.1
2,9/8-9/12,第二章 函数,练习 2.1
```

生成教学进度表：

```bash
python -m syllabus -i 进度.csv --term 2026秋季学期 --subject 数学 --group 高一3班 -o 教学进度.html
```

每页 10 条，适合贴在备课本上：

```bash
python -m syllabus -i 进度.csv --rows 10 -o 教学进度.html
```

### 参数

| 参数 | 说明 | 默认 |
| --- | --- | --- |
| `-i, --input` | 进度 CSV（周次,日期,教学内容,作业） | 必填 |
| `-o, --output` | 输出 HTML 路径 | `教学进度.html` |
| `--rows` | 每页行数 8~30 | `22` |
| `--term` | 学期，例如 `2026 秋季学期` | 空 |
| `--subject` | 学科 | 空 |
| `--group` | 班级 | 空 |
| `--title` | 页面标题 | `教学进度表` |

### CSV 格式

```csv
周次,日期,教学内容,作业
1,9/1-9/5,第一章 集合,练习 1.1
2,9/8-9/12,第二章 函数,练习 2.1
```

- 表头可有可无，支持 `周次/周/星期` 与 `日期/时间/起止日期`
- 最少两列：`周次,教学内容`
- 周次必须是 1~30 的整数，不能重复
- 教学内容最多 60 个字符，作业最多 40 个字符，日期最多 20 个字符
- 编码支持 UTF-8（含 BOM）与 GBK

## 打印

用浏览器打开生成的 HTML，按 `Ctrl/Cmd + P`：

- 纸张：A4 纵向
- 边距：无 / 默认
- 勾选「背景图形」，表头底色才会打印

## 项目结构

```text
syllabus/
├── syllabus/
│   ├── model.py    # CSV 解析、周次校验与分页
│   ├── render.py   # A4 进度表排版
│   └── cli.py      # 命令行入口
├── tests/          # 59 个单元测试
└── examples/       # 示例进度表
```

## 开发

```bash
python -m unittest discover -s tests
```

## 许可证

[MIT](LICENSE) © 2026 eastyou
