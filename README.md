# Python 数据分析项目模板

用于学术科研数据分析的 Python 项目模板。
它只预留必要结构：数据分层、可复现实验、Codex 入口文档、集成脚本、TeX 手稿和项目初始化文档。

## 项目结构

- `AGENTS.md`：agent 入口规则。
- `DASHBOARD.md`：实验进展看板。
- `docs/plans/research-plan.md`：研究想法和初始计划。
- `docs/project-preferences.md`：环境、工具和操作偏好。
- `docs/agents/`：agent 友好的项目流程文档。
- `docs/agents/dbschema/`：数据库 schema 文档。
- `data/`：原始、中间、处理后和外部数据。
- `src/`：可复用功能模块。
- `scripts/`：集成化项目脚本。
- `outputs/figures/` 和 `outputs/tables/`：通用图表和表格输出。
- `docs/writing/manuscript/`：默认 TeX 手稿工作区。

## 初始化

先配置基础环境：

```bash
make init
```

然后补齐项目上下文：

1. 在 @docs/plans/research-plan.md 写研究问题、数据来源、初始方法和第一步实验。
2. 在 @docs/project-preferences.md 写环境、运行方式、数据访问和协作偏好。
3. 根据计划创建第一个最小实验目录，例如 `experiments/001-baseline/`。
4. 更新 @DASHBOARD.md，让下一次 agent 接手时知道当前能推进什么。

不需要一开始写完所有细节。
模板只要求先形成足够推进第一步实验的计划文档。

## TeX 手稿

检查 TeX 环境：

```bash
make init-tex
```

编译手稿：

```bash
make manuscript
```

检查一行一句的 TeX 正文风格：

```bash
make check-tex-style
```

准备 Elsevier 提交目录：

```bash
make prepare-elsevier-submission
```

## 依赖管理

使用 [uv](https://docs.astral.sh/uv/)。

```bash
uv add <package>
uv add --group dev <package>
uv tree
```

## License

MIT
