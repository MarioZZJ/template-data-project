# Python 数据分析项目模板

用于学术科研数据分析的 Python 项目模板。开箱即用的目录结构、环境配置和 Claude Code 支持。

## 使用方法

点击右上角 **Use this template** 创建新仓库，然后克隆到本地，运行初始化脚本：

```bash
./scripts/setup_env.sh
```

脚本会交互式询问项目名称、作者等信息，自动更新配置文件并安装基础依赖。

也可以通过 Claude Code 初始化（需要先安装 Claude Code）：

```
/TDP:init-repo
```

## 目录结构

```
├── data/               原始、处理后、外部数据
├── outputs/            图表（figures/）和表格（tables/）
├── docs/               过程文档、方法记录
├── agents/             Agent 提示词、参考文档、共享 skill
├── src/utils/          可复用工具函数
├── scripts/            项目脚本
├── .env.example        环境变量模板
└── pyproject.toml      项目配置
```

## 依赖管理

使用 [uv](https://docs.astral.sh/uv/)：

```bash
uv add <package>               # 添加依赖
uv add --group dev <package>   # 添加开发依赖
uv tree                        # 查看依赖树
```

## Claude Code 支持

项目内置以下 `/TDP:` 命令：

| 命令 | 说明 |
|------|------|
| `/TDP:init-repo` | 交互式初始化（更新元数据、配置环境、可选创建 GitHub 仓库） |
| `/TDP:verify` | 检查环境配置（.env、.venv、依赖、pylint） |

同时支持 Codex：`AGENTS.md` 指向 `CLAUDE.md`，`.codex/skills/` 与 `.claude/` 共享 `agents/skills/` 中的 skill。

## License

MIT
