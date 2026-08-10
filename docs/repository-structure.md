# 仓库结构

## 根级真源

- `AGENTS.md`：简洁的全局规则与文档路由入口。
- `README.md`：项目定位、边界和权威研究执行顺序。
- `DASHBOARD.md`：项目状态唯一真源。
- `INITIALIZE_PROJECT.md`：模板生成后的唯一一次性文档，初始化提交前删除。
- `pyproject.toml`、`uv.lock`：Python 环境与锁定依赖。
- `Makefile`：Python/TeX 环境和手稿工具入口，不编排研究全流程。

## 长期目录

```text
data/
├── README.md
├── raw/
├── interim/
├── processed/
└── external/
src/
└── README.md
experiments/
└── README.md
outputs/
├── README.md
├── figures/
└── tables/
scripts/
└── README.md
docs/
├── README.md
├── repository-structure.md
├── data-sources.md
├── project-preferences.md
├── plans/
├── workflows/
├── examples/
└── writing/
.agents/
├── README.md
└── skills/example-skill/SKILL.md
```

README 是所在目录的局部事实来源，初始化后继续保留。
只有可能为空的数据和正式输出叶子目录使用 `.gitkeep`。

## 按需增加目录

真实项目出现明确需求后，可以增加测试、模型、查询或配置等目录，并就近补写职责与运行说明。
模板不提前创建空骨架，也不预设 Agent 运行时、工作流引擎或研究总控 harness。

## 路径变更

移动权威文件、研究源码或正式输出时，同时检查 `AGENTS.md`、根 README、`DASHBOARD.md`、实验 README、TeX 引用、脚本和 GitHub workflow。
