@echo off
echo ========================================
echo   EAIOS - 企业级Agent演示平台
echo ========================================
echo.

echo [1/3] 检查环境...
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.10+
    pause
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Node.js，请先安装Node.js 18+
    pause
    exit /b 1
)

echo Python 和 Node.js 已安装
echo.

echo [2/3] 启动后端...
cd backend
start cmd /k "python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo 后端启动中... (http://localhost:8000)
echo.

timeout /t 3 /nobreak >nul

echo [3/3] 启动前端...
cd ..\frontend
start cmd /k "npm run dev"
echo 前端启动中... (http://localhost:5173)
echo.

echo ========================================
echo   启动完成！
echo   后端: http://localhost:8000/docs
echo   前端: http://localhost:5173
echo ========================================
echo.
echo 按任意键关闭此窗口...
pause >nul
