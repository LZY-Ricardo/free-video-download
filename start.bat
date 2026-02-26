@echo off
echo 🚀 启动万能视频下载器...
echo.

REM 启动后端
echo 📦 启动后端服务...
cd backend
start "后端服务" python -m app.main
cd ..
echo ✅ 后端已启动 - http://localhost:8000
timeout /t 3 /nobreak >nul

REM 启动前端
echo 🎨 启动前端服务...
cd frontend
start "前端服务" npm run dev
cd ..
echo ✅ 前端已启动 - http://localhost:5173

echo.
echo 🎉 服务已全部启动！
echo    - 前端: http://localhost:5173
echo    - 后端: http://localhost:8000
echo    - API 文档: http://localhost:8000/docs
echo.
echo 按任意键关闭此窗口...
pause >nul
