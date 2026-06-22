from pathlib import Path
import shutil
import sys
import zipfile


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from assignment_system import create_app
from assignment_system.database import init_db


SOURCE_DIRS = {
    "assignment_system",
    "docs",
    "scripts",
    "tests",
}

SOURCE_FILES = {
    ".gitignore",
    "app.py",
    "main.py",
    "requirements.txt",
    "run_windows.bat",
    "build_windows_exe.bat",
    "README.md",
}

EXCLUDED_DIRS = {
    ".git",
    ".github",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "build",
    "data",
    "dist",
    "instance",
}

EXCLUDED_FILES = {
    "Python大作业要求2026.pptx",
    "windowsagents.md",
    "交付运行与答辩说明.md",
}

EXCLUDED_SUFFIXES = {
    ".aux",
    ".log",
    ".out",
    ".pyc",
}


def should_skip(path):
    relative = path.relative_to(ROOT)
    parts = set(relative.parts)
    if parts & EXCLUDED_DIRS:
        return True
    if path.name in EXCLUDED_FILES:
        return True
    if path.name == ".DS_Store":
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return True
    return False


def source_paths():
    for name in SOURCE_FILES:
        path = ROOT / name
        if path.exists() and not should_skip(path):
            yield path
    for dirname in SOURCE_DIRS:
        directory = ROOT / dirname
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if path.is_file() and not should_skip(path):
                yield path


def write_source_zip(zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source_paths()):
            archive.write(path, path.relative_to(ROOT))


def make_runtime_database():
    runtime_dir = OUT / "_runtime_data"
    shutil.rmtree(runtime_dir, ignore_errors=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    db_path = runtime_dir / "assignment_system.sqlite3"
    upload_path = runtime_dir / "uploads"
    app = create_app(
        {
            "DATABASE": str(db_path),
            "UPLOAD_FOLDER": str(upload_path),
            "SECRET_KEY": "coursework-runtime-secret",
        }
    )
    with app.app_context():
        init_db(seed=True)
    return db_path


def write_runtime_zip(zip_path, exe_path):
    if not exe_path.exists():
        raise FileNotFoundError("请先生成 dist\\HomeworkSystem.exe，再运行发布脚本。")

    db_path = make_runtime_database()
    run_bat = """@echo off
chcp 65001 >nul
cd /d "%~dp0"
start "" "%~dp0HomeworkSystem.exe"
timeout /t 2 /nobreak >nul
start "" http://127.0.0.1:5000
echo 系统已启动，浏览器会打开 http://127.0.0.1:5000
echo 如需停止系统，请关闭 HomeworkSystem.exe 窗口。
pause
"""
    note = """作业管理系统运行说明

1. 解压本压缩包。
2. 双击“启动系统.bat”。
3. 浏览器访问 http://127.0.0.1:5000。
4. 默认账号：
   管理员 admin / admin123
   教师 teacher01 / teacher123
   学生 student01 / student123
5. 如果系统数据需要恢复为初始状态，可删除 data 文件夹后重新解压本压缩包。
"""

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.write(exe_path, "HomeworkSystem.exe")
        archive.write(db_path, "data/assignment_system.sqlite3")
        archive.writestr("启动系统.bat", run_bat)
        archive.writestr("运行说明.txt", note)


def main():
    OUT.mkdir(exist_ok=True)
    exe_path = OUT / "HomeworkSystem.exe"
    exe_bytes = exe_path.read_bytes() if exe_path.exists() else None

    for old_zip in [OUT / "源程序压缩包.zip", OUT / "执行程序及运行环境压缩包.zip"]:
        old_zip.unlink(missing_ok=True)
    shutil.rmtree(OUT / "_runtime_data", ignore_errors=True)

    if exe_bytes is not None:
        exe_path.write_bytes(exe_bytes)

    write_source_zip(OUT / "源程序压缩包.zip")
    write_runtime_zip(OUT / "执行程序及运行环境压缩包.zip", exe_path)
    shutil.rmtree(OUT / "_runtime_data", ignore_errors=True)
    print(f"交付压缩包已生成：{OUT}")


if __name__ == "__main__":
    main()
