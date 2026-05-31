from pathlib import Path
import shutil
import zipfile


ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist"


EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "data",
    "uploads",
    "build",
    "dist",
}

EXCLUDED_SUFFIXES = {".pyc", ".log"}


def should_skip(path):
    parts = set(path.relative_to(ROOT).parts)
    if parts & EXCLUDED_DIRS:
        return True
    if path.suffix in EXCLUDED_SUFFIXES:
        return True
    if path.name == ".DS_Store":
        return True
    if path.name == "Python大作业要求2026.pptx":
        return True
    return False


def write_zip(zip_path, include_runtime_notes=False, runtime_exe=None):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in ROOT.rglob("*"):
            if path.is_file() and not should_skip(path):
                archive.write(path, path.relative_to(ROOT))
        if include_runtime_notes:
            note = (
                "Windows 运行方式：\n"
                "1. 解压后双击 run_windows.bat。\n"
                "2. 如需生成 exe，在 Windows 上双击 build_windows_exe.bat。\n"
                "3. 默认访问地址：http://127.0.0.1:5000。\n"
            )
            archive.writestr("运行说明.txt", note)
        if runtime_exe:
            archive.writestr("HomeworkSystem.exe", runtime_exe)


def main():
    OUT.mkdir(exist_ok=True)
    exe_path = OUT / "HomeworkSystem.exe"
    runtime_exe = exe_path.read_bytes() if exe_path.exists() else None
    shutil.rmtree(OUT, ignore_errors=True)
    OUT.mkdir(exist_ok=True)
    if runtime_exe:
        exe_path.write_bytes(runtime_exe)
    write_zip(OUT / "源程序压缩包.zip")
    write_zip(OUT / "执行程序及运行环境压缩包.zip", include_runtime_notes=True, runtime_exe=runtime_exe)
    print(f"交付压缩包已生成：{OUT}")


if __name__ == "__main__":
    main()
