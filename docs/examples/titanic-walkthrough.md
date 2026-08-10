# Titanic 三阶段示例

本示例记录模板如何从固定基点依次完成项目初始化、可复现分析和轻量过程汇报。
它是 `example/titanic` 分支上的外部参考历史，不是新项目开发分支；新项目不应 merge 或 cherry-pick 整个示例，而应根据实际研究问题、数据、方法、环境和协作方式逐项适配。
以下快照均使用完整 commit ID，避免分支移动后内容变化；链接方式见 GitHub 的[永久链接说明](https://docs.github.com/en/repositories/working-with-files/using-files/getting-permanent-links-to-files)。

## 模板基点

- 提交：`bd4d49c1c105d0912de2d4987af6f28fe8640fab`
- [查看模板基点快照](https://github.com/MarioZZJ/template-data-project/tree/bd4d49c1c105d0912de2d4987af6f28fe8640fab)

该快照只包含通用目录骨架、长期 README 契约、一次性初始化清单、人工维护的研究执行顺序，以及 TeX/Elsevier 工具。
此时仍保留 `INITIALIZE_PROJECT.md` 和各目录的 `PROJECT-INIT` 占位提示，不包含 Titanic 项目事实、研究源码或正式结果。

## 初始化阶段

- 提交：`311e66c1030fe02d9a2e9f2ef007b8c5b27c542d`
- [查看初始化快照](https://github.com/MarioZZJ/template-data-project/tree/311e66c1030fe02d9a2e9f2ef007b8c5b27c542d)
- [比较模板基点与初始化阶段](https://github.com/MarioZZJ/template-data-project/compare/bd4d49c1c105d0912de2d4987af6f28fe8640fab...311e66c1030fe02d9a2e9f2ef007b8c5b27c542d)

重点查看：

- `README.md`：项目名称、研究问题、边界和计划执行顺序；
- `DASHBOARD.md`：第一组可执行任务及其真实状态；
- `docs/plans/research-plan.md`、`docs/project-preferences.md`、`docs/data-sources.md`：研究设计、环境边界和数据来源；
- 各长期目录的 `README.md`：已经填写的“当前项目配置”；
- `data/raw/titanic/README.md`：官方文件、竞赛规则、认证和忽略边界；
- `experiments/001-survival-associations/README.md`：研究问题、变量、计划分析和当时仍未知的结果；
- `pyproject.toml` 与 `uv.lock`：按后续分析需要规划的 Python 环境。

这一提交只做项目初始化：填写项目事实、删除全部 `PROJECT-INIT` 注释，并在最后删除 `INITIALIZE_PROJECT.md`。
它没有创建虚假编号脚本，没有下载或提交原始数据，也没有写入实质分析结果。

不可机械复制的内容包括 Titanic 研究问题、乘客分析单位、变量、Logistic 回归设计、Kaggle 获取方式、依赖和输出名称。
新项目应使用自己的来源、许可、方法和证据标准重新完成初始化清单。

## 分析阶段

- 提交：`a519b7be5a543906991f5d68b69535d25c0b87e9`
- [查看分析快照](https://github.com/MarioZZJ/template-data-project/tree/a519b7be5a543906991f5d68b69535d25c0b87e9)
- [比较初始化与分析阶段](https://github.com/MarioZZJ/template-data-project/compare/311e66c1030fe02d9a2e9f2ef007b8c5b27c542d...a519b7be5a543906991f5d68b69535d25c0b87e9)

重点查看：

- `src/001-download_titanic_data.sh` 至 `src/060-make_tables.py`：从官方获取、样本构造、描述统计、Logistic 回归、诊断到正式图表的编号过程；
- 根 `README.md`：逐项可执行的命令、输入、输出和依赖关系；
- `data/raw/titanic/README.md` 与 `docs/data-sources.md`：本地原始快照的大小、SHA-256、访问限制和可追溯来源；
- `experiments/001-survival-associations/README.md`：预设问题、实际观察和研究边界；
- `outputs/figures/` 与 `outputs/tables/`：由编号源码生成并被 Git 跟踪的唯一正式输出；
- `DASHBOARD.md`：数据、样本构造和分析任务的完成证据。

这一阶段展示的协同关系是：原始 CSV 只保存在被忽略的 `data/raw/`，可重建数据进入被忽略的数据层，稳定正式图表进入中央 `outputs/`，实验 README 解释研究决策，`DASHBOARD.md` 记录状态证据，根 README 保持完整人工执行顺序。
分析只使用带标签的 `train.csv` 进行关联分析和内部交叉验证，`test.csv` 只用于确认官方获取和结构兼容性；没有生成或上传 Kaggle submission。

## 汇报阶段

- 提交：`9dfcc0f405d41e66dc6d5f5a3d2d187a5a4b42f5`
- [查看汇报快照](https://github.com/MarioZZJ/template-data-project/tree/9dfcc0f405d41e66dc6d5f5a3d2d187a5a4b42f5)
- [比较分析与汇报阶段](https://github.com/MarioZZJ/template-data-project/compare/a519b7be5a543906991f5d68b69535d25c0b87e9...9dfcc0f405d41e66dc6d5f5a3d2d187a5a4b42f5)

重点查看：

- `docs/writing/manuscript/main.tex`：研究问题、数据限制、样本、方法、初步结果、诊断、局限和下一步；
- `outputs/figures/` 与 `outputs/tables/`：手稿通过相对路径直接引用的正式真源；
- `scripts/check-tex-sentence-lines.py`：兼容统计小数和文件名的一行一句检查；
- `DASHBOARD.md` 与写作 README：过程汇报完成状态和维护边界。

手稿目录不保存第二份正式图表。
`make manuscript` 在被忽略的 `build/` 中生成 PDF，`make prepare-elsevier-submission` 才把中央输出复制到被忽略的独立投稿 bundle；生成目录不进入提交。

## GitHub 模板仓库行为

GitHub 的[模板仓库说明](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template)指出，从模板创建新仓库时默认只复制默认分支的目录和文件。
只有主动选择 **Include all branches** 才会复制其他分支；即使如此，新仓库中由模板生成的各分支也具有彼此无关的历史，不能在这些分支之间直接建立 pull request 或 merge。

因此，`example/titanic` 始终只用于阅读固定快照和比较设计决策。
新项目应从默认分支运行 `INITIALIZE_PROJECT.md`，不能把示例分支当成开发起点，也不应整体 merge 或 cherry-pick 示例历史。
