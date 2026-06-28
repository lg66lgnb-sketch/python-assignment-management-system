# Python Assignment Management System

> [中文版见下方 / Chinese version below](#chinese-version)

A small course assignment management system built with Flask and SQLite. It provides separate workflows for administrators, teachers, and students.

## Features

- Administrator approval and account management
- Course creation and student enrollment
- Assignment publishing and submission
- File uploads with original Chinese filenames preserved
- Grading, feedback, submission statistics, and CSV export
- Password hashing and role-based access control

## Quick Start

Requires Python 3.11 or later.

### Windows

Double-click `run_windows.bat`. It creates a virtual environment, installs dependencies, initializes the database, and opens the application.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
python app.py
```

Open <http://127.0.0.1:5000>.

To reset the database and restore the demo data:

```bash
python scripts/init_db.py --reset
```

## Demo Accounts

| Role | Username | Password |
| --- | --- | --- |
| Administrator | `admin` | `admin123` |
| Teacher | `teacher01` | `teacher123` |
| Student | `student01` | `student123` |

## Tests and Windows Build

```bash
python -m unittest discover -s tests -v
```

Run `build_windows_exe.bat` on Windows to build `dist/HomeworkSystem.exe`. GitHub Actions also publishes the executable as the `HomeworkSystem-Windows` artifact.

Project documentation is available in [`docs/pdf`](docs/pdf). The main application code is in [`assignment_system`](assignment_system).

---

## Chinese Version

# Python 作业管理系统

这是一个基于 Flask 和 SQLite 的课程作业管理系统，分别为管理员、教师和学生提供完整的操作流程。

## 功能

- 管理员审核和账号管理
- 教师创建课程、发布作业
- 学生选课、提交文字和附件
- 保留上传文件的原始中文文件名
- 教师评分、填写评语、统计提交并导出 CSV
- 密码哈希存储和基于角色的权限控制

## 快速运行

需要 Python 3.11 或更高版本。

### Windows

双击 `run_windows.bat`。脚本会自动创建虚拟环境、安装依赖、初始化数据库并打开系统。

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
python app.py
```

浏览器访问 <http://127.0.0.1:5000>。

如需重置数据库并恢复演示数据：

```bash
python scripts/init_db.py --reset
```

## 演示账号

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | `admin` | `admin123` |
| 教师 | `teacher01` | `teacher123` |
| 学生 | `student01` | `student123` |

## 测试与 Windows 打包

```bash
python -m unittest discover -s tests -v
```

在 Windows 上运行 `build_windows_exe.bat` 可生成 `dist/HomeworkSystem.exe`。GitHub Actions 也会构建名为 `HomeworkSystem-Windows` 的可执行文件产物。

项目文档位于 [`docs/pdf`](docs/pdf)，主要程序代码位于 [`assignment_system`](assignment_system)。
