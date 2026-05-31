# Windows 接管说明

本文用于 Windows 电脑继续接管本仓库的剩余收尾工作。当前系统代码已经能运行，主要待解决问题集中在文档截图真实性和 LaTeX 图形排版。

## 1. 当前仓库状态

- GitHub 仓库：`https://github.com/lg66lgnb-sketch/python-assignment-management-system`
- 当前主分支：`main`
- 最近关键提交：
  - `914097b Replace Word docs with LaTeX PDFs`
  - `4c0b638 Preserve Windows exe in release package`
  - `7f6a3c5 Initial coursework management system`
- 正式文档已经从 Word 改成 LaTeX 渲染 PDF。
- 旧的 `docs/*.md` 和 `docs/word/*.docx` 已经删除，不要继续改 Word 文档。

## 2. Windows 快速运行

在 Windows 上打开 PowerShell 或 CMD：

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

当前三份正式文档都是 LaTeX 文件生成的 PDF，不是 Word：

| 文档 | LaTeX 源文件 | PDF 成品 |
| --- | --- | --- |
| 系统设计说明书 | `docs/latex/系统设计说明书.tex` | `docs/pdf/系统设计说明书.pdf` |
| 用户使用手册 | `docs/latex/用户使用手册.tex` | `docs/pdf/用户使用手册.pdf` |
| 过程剖析 | `docs/latex/过程剖析.tex` | `docs/pdf/过程剖析.pdf` |

Windows 端需要安装 TeX Live 或 MiKTeX，并确保 `xelatex` 可用。重新生成 PDF 时执行：

```bat
cd docs\latex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=..\pdf 系统设计说明书.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=..\pdf 系统设计说明书.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=..\pdf 用户使用手册.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=..\pdf 用户使用手册.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=..\pdf 过程剖析.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=..\pdf 过程剖析.tex
```

每份文档建议编译两次，避免目录、书签和引用信息不完整。

## 4. 当前必须继续解决的问题

### 问题一：过程剖析里的两张 bug 截图太假

当前 `过程剖析.pdf` 中：

- `图 1：初始化脚本导入失败`
- `图 2：重复初始化风险`

这两张图不是 Windows 真实运行截图，而是前期为了占位做出来的图。必须在 Windows 电脑上重新截真实截图。

当前占位图文件：

- `docs/screenshots/bug_01_import_error_flat.jpg`
- `docs/screenshots/bug_02_init_reset_flat.jpg`

LaTeX 引用位置：

- `docs/latex/过程剖析.tex`

建议替换方式：

1. 在 Windows 上新建临时分支：

   ```bat
   git switch -c windows-doc-fixes
   ```

2. 只为了截图临时复现旧问题，不要把故障代码提交。

3. 截完图后，把真实截图保存为：

   ```text
   docs/screenshots/bug_01_import_error_windows.png
   docs/screenshots/bug_02_init_reset_windows.png
   ```

4. 修改 `docs/latex/过程剖析.tex`，把图片引用从 `_flat.jpg` 改成 Windows 真实截图。

5. 重新用 `xelatex` 渲染 `docs/pdf/过程剖析.pdf`。

6. 丢弃为了复现 bug 做的临时代码改动，只提交截图、LaTeX 和 PDF。

截图复现建议：

- `bug_01_import_error`：临时移除 `scripts/init_db.py` 开头加入项目根目录到 `sys.path` 的代码，然后在 Windows 终端执行 `python scripts\init_db.py`，截取真实 `ModuleNotFoundError` 终端画面。
- `bug_02_init_reset`：临时把 `scripts/init_db.py` 改回直接调用 `init_db(seed=True)`，先制造一条提交记录，再运行初始化脚本，截图展示提交记录被清空的现象。可以用 PowerShell 里前后查询数据库记录数的方式截图。

注意：这两种临时复现只用于真实截图，复现用的故障代码不要提交。

### 问题二：系统设计说明书里的两张 TikZ 图连线有明显问题

当前 `系统设计说明书.pdf` 中：

- `图 2：数据库实体关系图`
- `图 3：系统用例图`

存在连线穿过文字、连线位置不自然、图形观感不专业的问题。

LaTeX 源文件：

```text
docs/latex/系统设计说明书.tex
```

需要重点修改两个位置：

- `\caption{数据库实体关系图}` 附近的 TikZ 代码。
- `\caption{系统用例图}` 附近的 TikZ 代码。

修改要求：

- 数据库实体关系图中，连线不能穿过实体框文字。
- `USERS`、`COURSES`、`ENROLLMENTS`、`ASSIGNMENTS`、`SUBMISSIONS` 的关系应清晰。
- 可采用上下分层布局，例如：
  - 顶部：`USERS`
  - 中部：`COURSES`、`ENROLLMENTS`、`ASSIGNMENTS`
  - 底部：`SUBMISSIONS`
  - 关系说明放在图下方，不要压在连线上。
- 系统用例图中，连线不要竖直穿过椭圆文字。
- 角色到用例的线建议从角色框底部或右侧分叉，连接到椭圆边缘，不要连接到椭圆中心。
- 如果 TikZ 调整太费时间，可以用 draw.io、Visio 或 PowerPoint 画图，导出 PNG，再在 LaTeX 中用 `\includegraphics` 引入。最终 PDF 好看优先。

修改后必须重新生成：

```text
docs/pdf/系统设计说明书.pdf
```

## 5. 推荐工作顺序

1. Windows clone 仓库并运行 `run_windows.bat`，确认系统能启动。
2. 新建分支 `windows-doc-fixes`。
3. 在 Windows 上截取两张真实 bug 图，替换过程剖析占位图。
4. 修复 `系统设计说明书.tex` 中图 2 和图 3 的连线问题。
5. 用 `xelatex` 重新生成三份 PDF，至少重点检查：
   - `docs/pdf/系统设计说明书.pdf`
   - `docs/pdf/过程剖析.pdf`
6. 运行测试：

   ```bat
   .venv\Scripts\python -m unittest discover -s tests -v
   ```

7. 重新生成交付压缩包：

   ```bat
   .venv\Scripts\python scripts\build_release.py
   ```

8. 提交并推送：

   ```bat
   git add docs README.md windowsagents.md
   git commit -m "Fix Windows documentation screenshots and diagrams"
   git push origin windows-doc-fixes
   ```

## 6. 不要做的事

- 不要恢复 Word 文档。
- 不要把临时复现 bug 的坏代码提交。
- 不要用假终端图替代真实 Windows 截图。
- 不要只改 PDF 不改 LaTeX 源文件。
- 不要把 `.venv`、`data`、`dist`、`.DS_Store`、LaTeX 临时文件提交进仓库。

## 7. 当前可接受状态

系统代码本身目前可以运行，GitHub Actions 也能在 Windows 上成功构建 `HomeworkSystem.exe`。接下来 Windows 端主要是把文档做实、做漂亮：

- 真实 Windows 截图。
- 修好系统设计说明书里的实体关系图和用例图。
- 重新渲染 PDF。
- 重新打包交付材料。

