#!/bin/bash

echo "🚀 启动万能视频下载器..."
echo ""

# 启动后端
echo "📦 启动后端服务..."
cd backend
python -m app.main &
BACKEND_PID=$!
echo "✅ 后端已启动 (PID: $BACKEND_PID) - http://localhost:8000"
cd ..

# 等待后端启动
sleep 3

# 启动前端
echo "🎨 启动前端服务..."
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ 前端已启动 (PID: $FRONTEND_PID) - http://localhost:5173"
cd ..

echo ""
echo "🎉 服务已全部启动！"
echo "   - 前端: http://localhost:5173"
echo "   - 后端: http://localhost:8000"
echo "   - API 文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo ''; echo '🛑 正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID; exit 0" INT

wait
