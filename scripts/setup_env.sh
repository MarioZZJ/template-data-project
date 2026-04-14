#!/bin/bash

# Python数据分析项目初始化脚本
# 交互式收集项目信息，配置环境

set -e

echo "=============================="
echo "  Python 数据分析项目初始化"
echo "=============================="
echo ""

# ─── 收集项目信息 ────────────────────────────────────────────────────────────

read -rp "项目显示名称 [My Data Analysis Project]: " PROJECT_DISPLAY_NAME
PROJECT_DISPLAY_NAME=${PROJECT_DISPLAY_NAME:-"My Data Analysis Project"}

# 自动生成 Python 包名（小写，非字母数字换成连字符）
DEFAULT_PACKAGE_NAME=$(echo "$PROJECT_DISPLAY_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/-\+/-/g' | sed 's/^-\|-$//g')
read -rp "Python 包名 [$DEFAULT_PACKAGE_NAME]: " PACKAGE_NAME
PACKAGE_NAME=${PACKAGE_NAME:-$DEFAULT_PACKAGE_NAME}

read -rp "项目描述 [Python数据分析项目]: " PROJECT_DESC
PROJECT_DESC=${PROJECT_DESC:-"Python数据分析项目"}

read -rp "作者姓名 [Your Name]: " AUTHOR_NAME
AUTHOR_NAME=${AUTHOR_NAME:-"Your Name"}

read -rp "作者邮箱 [your.email@example.com]: " AUTHOR_EMAIL
AUTHOR_EMAIL=${AUTHOR_EMAIL:-"your.email@example.com"}

read -rp "版本号 [0.1.0]: " PROJECT_VERSION
PROJECT_VERSION=${PROJECT_VERSION:-"0.1.0"}

echo ""
echo "📋 确认项目信息："
echo "  显示名称: $PROJECT_DISPLAY_NAME"
echo "  包名:     $PACKAGE_NAME"
echo "  描述:     $PROJECT_DESC"
echo "  作者:     $AUTHOR_NAME <$AUTHOR_EMAIL>"
echo "  版本:     $PROJECT_VERSION"
echo ""
read -rp "确认继续? [Y/n]: " CONFIRM
CONFIRM=${CONFIRM:-Y}
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "已取消"
    exit 0
fi

# ─── 更新项目元数据 ────────────────────────────────────────────────────────────

echo ""
echo "📝 更新 pyproject.toml..."
sed -i "s|name = \"python-data-analysis-template\"|name = \"$PACKAGE_NAME\"|" pyproject.toml
sed -i "s|version = \"0.1.0\"|version = \"$PROJECT_VERSION\"|" pyproject.toml
sed -i "s|description = \"Python数据分析项目模板\"|description = \"$PROJECT_DESC\"|" pyproject.toml
sed -i "s|Your Name|$AUTHOR_NAME|g" pyproject.toml
sed -i "s|your.email@example.com|$AUTHOR_EMAIL|g" pyproject.toml

echo "📝 更新 src/__init__.py..."
sed -i "s|__version__ = \"0.1.0\"|__version__ = \"$PROJECT_VERSION\"|" src/__init__.py
sed -i "s|__author__ = \"Your Name\"|__author__ = \"$AUTHOR_NAME\"|" src/__init__.py
sed -i "s|__email__ = \"your.email@example.com\"|__email__ = \"$AUTHOR_EMAIL\"|" src/__init__.py

echo "📝 准备 .env 文件..."
if [ ! -f ".env" ]; then
    cp .env.example .env
fi
sed -i "s|PROJECT_NAME=python-data-analysis-template|PROJECT_NAME=$PACKAGE_NAME|" .env
sed -i "s|PROJECT_VERSION=0.1.0|PROJECT_VERSION=$PROJECT_VERSION|" .env

# ─── 配置虚拟环境 ─────────────────────────────────────────────────────────────

if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source ~/.bashrc
    echo "✅ uv 安装完成"
fi

if [ ! -d ".venv" ]; then
    echo "📦 创建虚拟环境..."
    uv venv
else
    echo "📦 虚拟环境已存在，跳过创建"
fi

source .venv/bin/activate

echo "📚 安装基础依赖..."
uv add pandas numpy matplotlib seaborn jupyterlab ipykernel python-dotenv

echo "🛠️  安装开发依赖..."
uv add --group dev jupyter notebook

echo "🔗 注册 Jupyter 内核..."
python -m ipykernel install --user --name="$PACKAGE_NAME" --display-name="Python ($PROJECT_DISPLAY_NAME)"

# ─── 完成 ──────────────────────────────────────────────────────────────────────

echo ""
echo "✅ 初始化完成！"
echo ""
echo "🎯 快速开始："
echo "  source .venv/bin/activate   # 激活虚拟环境"
echo "  jupyter lab                 # 启动 Jupyter Lab"
echo "  uv add <package>            # 添加依赖"
echo ""
echo "📁 项目结构："
echo "├── data/         原始/处理后/外部数据"
echo "├── outputs/      图表和表格输出"
echo "├── docs/         过程文档"
echo "├── agents/       Agent 提示词和参考文档"
echo "├── src/utils/    工具函数"
echo "├── scripts/      脚本文件"
echo "└── .env          环境变量（勿提交）"
