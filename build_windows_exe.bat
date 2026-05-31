@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PYTHON=python
where py >nul 2>nul
if %errorlevel%==0 set PYTHON=py -3

echo [1/4] 准备虚拟环境
if not exist ".venv\Scripts\python.exe" (
    %PYTHON% -m venv .venv
)
call ".venv\Scripts\activate.bat"

echo [2/4] 安装打包依赖
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

echo [3/4] 清理旧文件
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [4/4] 生成可执行文件
pyinstaller --noconfirm --clean --onefile ^
    --name HomeworkSystem ^
    --add-data "assignment_system\templates;assignment_system\templates" ^
    --add-data "assignment_system\static;assignment_system\static" ^
    --add-data "assignment_system\schema.sql;assignment_system" ^
    main.py

if errorlevel 1 (
    echo 打包失败，请检查上方错误信息。
    pause
    exit /b 1
)

echo 打包完成：dist\HomeworkSystem.exe
pause

