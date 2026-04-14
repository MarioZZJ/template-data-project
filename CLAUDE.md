# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Python 学术科研数据分析项目。主要工作流：Python 脚本数据处理 + 连接外部数据源（数据库/API）+ 生成可视化报告。

## 包管理

用 `uv`，不用 `pip`：

```bash
uv add <package>              # 添加生产依赖
uv add --group dev <package>  # 添加开发依赖
uv remove <package>           # 移除依赖
uv tree                       # 查看依赖树
```

## 环境初始化

```bash
./scripts/setup_env.sh        # 首次初始化（创建 .venv、安装基础包、复制 .env）
source .venv/bin/activate     # 激活虚拟环境
jupyter lab                   # 启动 Jupyter Lab
```

## 代码格式

- 格式化工具：autopep8，`--max-line-length=120 --aggressive`
- 行宽 120（非默认的 79），不要硬截 120 以内的行

## 项目结构

```
data/           # 数据文件（原始/处理后/外部）
  raw/          # 原始数据，不修改
  processed/    # 处理后数据
  external/     # 外部来源数据
outputs/        # 输出结果
  figures/      # 图表
  tables/       # 表格
docs/           # 过程文档（分析思路、方法记录）
agents/         # Agent 提示词、参考文档、功能定义
src/
  utils/        # 可复用工具函数
scripts/        # 项目脚本
```

## 环境变量

凭据和配置（数据库连接串、API Key 等）放 `.env`（从 `.env.example` 复制，不提交到 git）。

```python
from dotenv import load_dotenv
import os
load_dotenv()
value = os.getenv('KEY')
```

## 测试

无测试框架，不要自动生成测试文件。

## 图表样式

生成图表时遵循项目样式规范：

@agents/FIG-STYLE.md

## Git

commit message 用中文，简洁描述变更。
