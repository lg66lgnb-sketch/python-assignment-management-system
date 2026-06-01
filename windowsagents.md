# Windows 接管说明

本文用于在 Windows 电脑上继续接管本仓库。当前收尾重点已经从“补截图”转为“确认最终交付材料”：真实 bug 截图已替换，LaTeX PDF 已重新生成，发布压缩包也可以重新打包。

## 1. 仓库状态

- GitHub 仓库：https://github.com/lg66lgnb-sketch/python-assignment-management-system
- 当前工作分支：`windows-doc-fixes`
- 项目目录：`C:\Users\lg66l\Documents\python coursework`
- 正式文档使用 LaTeX 源文件生成 PDF，不再维护 Word 版本。

## 2. Windows 快速运行

在 PowerShell 或 CMD 中执行：

```bat
git clone https://github.com/lg66lgnb-sketch/python-assignment-management-system.git
cd python-assignment-management-system
run_windows.bat
```

默认访问地址：

```text
http://127.0.0.1:5000
```

默认账号：

| 角色 | 用户名 | 密码 |
| --- | --- | --- |
| 管理员 | admin | admin123 |
| 教师 | teacher01 | teacher123 |
| 学生 | student01 | student123 |

## 3. 文档生成方式

当前三份正式文档：

| 文档 | LaTeX 源文件 | PDF 成品 |
| --- | --- | --- |
| 系统设计说明书 | `docs/latex/系统设计说明书.tex` | `docs/pdf/系统设计说明书.pdf` |
| 用户使用手册 | `docs/latex/用户使用手册.tex` | `docs/pdf/用户使用手册.pdf` |
| 过程剖析 | `docs/latex/过程剖析.tex` | `docs/pdf/过程剖析.pdf` |

Windows 端已安装 MiKTeX。若当前终端找不到 `xelatex`，先执行：

```powershell
$env:PATH = "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64;$env:PATH"
```

重新生成 PDF：

```powershell
cd "C:\Users\lg66l\Documents\python coursework\docs\latex"
xelatex --output-directory=../pdf --interaction=nonstopmode --halt-on-error "系统设计说明书.tex"
xelatex --output-directory=../pdf --interaction=nonstopmode --halt-on-error "系统设计说明书.tex"
xelatex --output-directory=../pdf --interaction=nonstopmode --halt-on-error "用户使用手册.tex"
xelatex --output-directory=../pdf --interaction=nonstopmode --halt-on-error "用户使用手册.tex"
xelatex --output-directory=../pdf --interaction=nonstopmode --halt-on-error "过程剖析.tex"
xelatex --output-directory=../pdf --interaction=nonstopmode --halt-on-error "过程剖析.tex"
```

说明：MiKTeX 可能提示 “So far, you have not checked for MiKTeX updates.” 这是安装后的更新检查提示，不代表 PDF 编译失败。

## 4. 已修复的真实 bug 案例

过程剖析文档现在使用一个真实可复现的开发 bug：

- 问题：教师发布作业时，`course_id` 表单值如果不是整数，旧代码会直接执行 `int(...)`，导致 Flask 500 错误。
- 修复：在 `assignment_system/routes.py` 中捕获 `TypeError` 和 `ValueError`，给出“请选择有效课程。”提示并返回教师首页。
- 回归测试：`tests/test_workflow.py` 新增 `test_invalid_assignment_course_id_shows_message`。

真实截图文件：

| 截图 | 含义 |
| --- | --- |
| `docs/screenshots/bug_01_form_validation_before.png` | 修复前真实 500 页面 |
| `docs/screenshots/bug_01_form_validation_after.png` | 修复后真实提示页面 |

旧的占位 bug 图已经删除，避免交付包里混入不再使用的素材。

## 5. 验证命令

运行单元测试：

```powershell
cd "C:\Users\lg66l\Documents\python coursework"
.venv\Scripts\python -m unittest discover -s tests -v
```

重新生成交付压缩包：

```powershell
cd "C:\Users\lg66l\Documents\python coursework"
.venv\Scripts\python scripts\build_release.py
```

生成结果：

```text
dist/源程序压缩包.zip
dist/执行程序及运行环境压缩包.zip
```

## 6. 不要做的事

- 不要恢复 Word 文档。
- 不要提交为了复现 bug 临时改坏的代码。
- 不要再使用伪造终端图或占位 bug 图。
- 不要只改 PDF 不改 LaTeX 源文件。
- 不要提交 `.venv`、`data`、`dist` 或 LaTeX 临时文件。
