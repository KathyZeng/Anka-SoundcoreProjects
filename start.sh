#!/bin/bash
# 工作负载分析系统启动脚本

echo "=========================================="
echo "  工作负载饱和度分析系统"
echo "  v2.0.0"
echo "=========================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python 3"
    echo "请先安装 Python 3.8 或更高版本"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"
echo ""

# 检查依赖
echo "🔍 检查依赖包..."
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "⚠️  未安装依赖包,开始安装..."
    pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖已安装"
fi

echo ""
echo "🚀 启动应用..."
echo "📍 访问地址: http://localhost:8501"
echo ""
echo "💡 提示:"
echo "   - 按 Ctrl+C 停止应用"
echo "   - 浏览器将自动打开应用页面"
echo ""

# 启动Streamlit应用
python3 -m streamlit run app.py --server.port 8501 --server.headless false

echo ""
echo "👋 应用已停止"
