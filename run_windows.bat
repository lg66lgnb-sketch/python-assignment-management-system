@echo off
chcp 65001 >nul
cd /d "%~dp0"

set PYTHON=python
where py >nul 2>nul
if %errorlevel%==0 set PYTHON=py -3

echo [1/4] 检查 Python 环境
%PYTHON% --version
if errorlevel 1 (
    echo 未找到 Python，请先安装 Python 3.11 或更高版本。
    pause
    exit /b 1
)

echo [2/4] 创建虚拟环境
if not exist ".venv\Scripts\python.exe" (
    %PYTHON% -m venv .venv
)

echo [3/4] 安装依赖
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo 依赖安装失败，请检查网络或 pip 配置。
    pause
    exit /b 1
)

echo [4/4] 初始化数据库并启动系统
python scripts\init_db.py
start http://127.0.0.1:5000
python app.py
pause

