#!/bin/bash

# Python数据分析项目虚拟环境初始化脚本
# 使用uv创建和管理虚拟环境

set -e  # 遇到错误时退出

echo "🚀 开始初始化Python数据分析项目环境..."

# 检查uv是否安装
if ! command -v uv &> /dev/null; then
    echo "❌ uv未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc  # 重新加载配置文件
    echo "✅ uv安装完成"
fi

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    uv venv
    echo "✅ 虚拟环境创建完成"
else
    echo "📦 虚拟环境已存在，跳过创建"
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source .venv/bin/activate

# 安装基础数据分析包
echo "📚 安装基础数据分析包..."
uv add pandas numpy matplotlib seaborn jupyterlab ipykernel

# 安装开发工具包
echo "🛠️  安装开发工具包..."
uv add python-dotenv

# 准备环境变量文件
if [ -f ".env.example" ]; then
    if [ ! -f ".env" ]; then
        echo "📝  复制环境变量模板..."
        cp .env.example .env
        echo "✅ 已创建 .env 文件，请根据需要修改"
    else
        echo "📝  已检测到现有 .env 文件，跳过复制"
    fi
else
    echo "⚠️ 未找到 .env.example，请手动创建 .env 文件"
fi

# 安装Jupyter相关包到开发组
echo "🔧 安装Jupyter开发包..."
uv add --group dev jupyter notebook

# 创建Jupyter内核
echo "🔗 创建Jupyter内核..."
python -m ipykernel install --user --name=$(basename $(pwd)) --display-name="Python ($(basename $(pwd)))"

echo "✅ 环境初始化完成！"
echo ""
echo "🎯 使用说明："
echo "1. 激活虚拟环境: source .venv/bin/activate"
echo "2. 启动Jupyter Lab: jupyter lab"
echo "3. 安装新依赖: uv add <package_name>"
echo "4. 安装开发依赖: uv add --group dev <package_name>"
echo "5. 查看依赖: uv tree"
echo "6. 移除依赖: uv remove <package_name>"
echo ""
echo "📁 项目结构："
echo "├── src/           - 源代码"
echo "│   ├── data/     - 数据文件"
echo "│   ├── notebooks/- Jupyter笔记本"
echo "│   └── utils/    - 工具函数"
echo "├── scripts/       - 脚本文件"
echo "├── .venv/        - 虚拟环境"
echo "└── .env          - 环境变量"
echo ""
echo "🚀 开始您的数据分析之旅吧！"
