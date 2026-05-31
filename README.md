# 基于 Python 的作业管理数据库应用系统

这是一个中文界面的课程作业管理系统，采用 Flask + SQLite 实现。系统包含管理员、教师、学生三类用户，支持教师审核、课程管理、作业发布、学生提交、教师评分、提交统计和 CSV 导出。

## 快速运行

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/init_db.py
python app.py
```

浏览器访问：

```text
http://127.0.0.1:5000
```

### Windows

双击运行：

```text
run_windows.bat
```

脚本会自动创建虚拟环境、安装依赖、初始化数据库并启动系统。

如需清空数据库并恢复演示数据，可执行：

```bash
python scripts/init_db.py --reset
```

## 默认账号

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | admin | admin123 |
| 教师 | teacher01 | teacher123 |
| 学生 | student01 | student123 |

## 目录说明

```text
assignment_system/     系统代码
docs/latex/            LaTeX 文档源文件
docs/pdf/              PDF 版系统设计说明书、使用手册、过程剖析
scripts/               初始化、打包和辅助脚本
tests/                 自动化测试
run_windows.bat        Windows 一键运行脚本
build_windows_exe.bat  Windows 打包脚本
```

## 文档

正式提交建议使用 `docs/pdf/` 下的三个 PDF 文件：

- `系统设计说明书.pdf`
- `用户使用手册.pdf`
- `过程剖析.pdf`

如需重新生成 PDF，可在 macOS 或安装 TeX Live 的 Windows 环境中执行：

```bash
cd docs/latex
xelatex -output-directory=../pdf 系统设计说明书.tex
xelatex -output-directory=../pdf 用户使用手册.tex
xelatex -output-directory=../pdf 过程剖析.tex
```

## Windows 答辩建议

答辩前先在 Windows 电脑上执行一次 `run_windows.bat`。如果需要离线演示，再运行 `build_windows_exe.bat` 生成可执行文件。推荐现场优先使用源码脚本运行，exe 作为备用。

如果仓库已推送到 GitHub，也可以在 Actions 页面下载 `HomeworkSystem-Windows` 构建产物。
