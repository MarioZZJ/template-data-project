#!/usr/bin/env bash

# Python数据分析项目初始化脚本
# 交互式收集项目信息，配置环境

set -euo pipefail

sedi() {
    if sed --version >/dev/null 2>&1; then
        sed -i "$@"
    else
        local expr="$1"
        local file="$2"
        sed -i '' "$expr" "$file"
    fi
}

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
sedi "s|name = \"python-data-analysis-template\"|name = \"$PACKAGE_NAME\"|" pyproject.toml
sedi "s|version = \"0.1.0\"|version = \"$PROJECT_VERSION\"|" pyproject.toml
sedi "s|description = \"Python数据分析项目模板\"|description = \"$PROJECT_DESC\"|" pyproject.toml
sedi "s|Your Name|$AUTHOR_NAME|g" pyproject.toml
sedi "s|your.email@example.com|$AUTHOR_EMAIL|g" pyproject.toml

echo "📝 更新 src/__init__.py..."
sedi "s|__version__ = \"0.1.0\"|__version__ = \"$PROJECT_VERSION\"|" src/__init__.py
sedi "s|__author__ = \"Your Name\"|__author__ = \"$AUTHOR_NAME\"|" src/__init__.py
sedi "s|__email__ = \"your.email@example.com\"|__email__ = \"$AUTHOR_EMAIL\"|" src/__init__.py

echo "📝 准备 .env 文件..."
if [ ! -f ".env" ]; then
    cp .env.example .env
fi
sedi "s|PROJECT_NAME=python-data-analysis-template|PROJECT_NAME=$PACKAGE_NAME|" .env
sedi "s|PROJECT_VERSION=0.1.0|PROJECT_VERSION=$PROJECT_VERSION|" .env

# ─── 配置虚拟环境 ─────────────────────────────────────────────────────────────

if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安装。请先安装 uv 后重新运行本脚本。"
    echo "   https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
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
echo "🧭 下一步文档："
echo "  docs/plans/research-plan.md   # 写研究问题、数据来源、初始方法和第一步实验"
echo "  docs/project-preferences.md   # 写环境、工具、数据访问和操作偏好"
echo "  DASHBOARD.md                  # 更新当前可推进的实验状态"
echo ""
echo "📁 项目结构："
echo "├── data/         原始/处理后/外部数据"
echo "├── outputs/      图表和表格输出"
echo "├── docs/plans/   研究计划"
echo "├── docs/agents/  Agent 文档和数据库 schema"
echo "├── docs/writing/ TeX 写作工作区"
echo "├── src/          可复用功能模块"
echo "├── scripts/      集成化项目脚本"
echo "└── .env          环境变量（勿提交）"
