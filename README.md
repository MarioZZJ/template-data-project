# 定量科学研究项目模板

这是面向单篇数据驱动、过程密集型定量科学研究的 Agent 友好型项目模板。
模板提供可见的目录骨架、局部 README 契约、人工维护的执行顺序、统一正式输出和 TeX/Elsevier 写作流程，但不预设具体研究路线或运行时配置。

## 当前项目

<!-- PROJECT-INIT: 初始化时填写并删除本注释 -->

- 项目名称：待初始化。
- 研究问题：待初始化。
- 研究对象与分析单位：待初始化。
- 项目边界：待初始化。
- 正式交付：待初始化。

## 初始化

从模板创建新项目后，先执行 `INITIALIZE_PROJECT.md`。
初始化会填写研究计划、数据来源、项目偏好、各目录 README 和第一项可执行任务，并在独立提交中删除该一次性清单。

Python 环境使用 `uv`：

```bash
make init-python
```

TeX 环境可独立检查：

```bash
make init-tex
```

## 研究执行顺序

本表是完整运行命令、输入、输出和依赖关系的权威说明。
源码编号提供视觉顺序，但不能替代本表；新增、删除或重排步骤时，同步更新本表、`DASHBOARD.md` 和相关实验 README。

| 顺序 | 状态 | 命令 | 输入 | 输出 | 说明 |
|---:|---|---|---|---|---|
| — | `待初始化` | 待填写 | 待填写 | 待填写 | 初始化时删除本占位行，不创建虚假脚本 |

不提供一键运行全部研究的入口。
研究者按表中顺序逐项运行和核验。

## 目录结构

- `data/`：原始、中间、分析就绪和外部数据分层。
- `src/`：直接参与研究过程的编号源码或实质性研究模块。
- `experiments/`：围绕研究假设、方法比较或稳健性问题的记录。
- `outputs/figures/`、`outputs/tables/`：正式图件和表格的唯一真源。
- `scripts/`：跨研究内容的仓库工具，主要服务 TeX 和投稿。
- `docs/`：研究计划、长期事实、工作流、示例和手稿。
- `.agents/`：真实项目按需沉淀的少量稳定 skill；模板只含格式示例。

完整结构见 `docs/repository-structure.md`。

## 状态与正式输出

`DASHBOARD.md` 是项目状态的唯一真源。
正式图件和表格只保存在 `outputs/`，实验目录和手稿目录不维护第二份副本。

## TeX 与 Elsevier

```bash
make check-tex-style
make manuscript
make manuscript-diff
make prepare-elsevier-submission
```

默认手稿使用 CTAN `elsarticle` 和 Harvard author-year 样式，正文保持一行一句。
构建和投稿目录是生成产物，不提交到 Git。

## Titanic 三阶段示例

`example/titanic` 分支展示初始化、分析和轻量过程汇报三个阶段。
固定提交链接、阶段差异和 GitHub 模板仓库的分支行为见 `docs/examples/titanic-walkthrough.md`；该示例用于阅读，不是新项目开发分支。

## License

MIT
