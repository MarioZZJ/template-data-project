---
description: 验证项目环境和代码质量：检查 .env、.venv、依赖安装，并对 Python 文件运行 pylint。
---

运行以下检查步骤，逐项报告结果：

## 1. 环境文件

检查 `.env` 是否存在：
```bash
[ -f .env ] && echo "✓ .env 存在" || echo "✗ .env 缺失（运行 cp .env.example .env）"
```

## 2. 虚拟环境

检查 `.venv` 是否存在：
```bash
[ -d .venv ] && echo "✓ .venv 存在" || echo "✗ .venv 缺失（运行 ./scripts/setup_env.sh）"
```

## 3. 依赖安装

检查依赖是否已安装：
```bash
uv tree 2>&1 | head -20
```

如果 uv tree 报错说明依赖未安装，提示用户运行 `uv sync`。

## 4. Python 代码 Lint

对项目中所有 `.py` 文件（排除 `.venv/`）运行 pylint：
```bash
find . -name "*.py" -not -path "./.venv/*" -not -path "./build/*" | head -20 | xargs pylint --max-line-length=120 2>&1 || true
```

如果没有 `.py` 文件，跳过此步骤并说明。

## 输出格式

每一项用 ✓（通过）或 ✗（失败）标注，失败时给出具体修复命令。
