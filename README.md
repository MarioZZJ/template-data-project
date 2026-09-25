# Multica 定量研究项目模板

本模板支持“研究计划 → Multica 阶段与任务 → 持久执行 → 研究解释 → 论文交付”。研究设计与证据保存在仓库，任务状态和阶段授权由 Multica 管理，数据与中间产物保存在用户目录下的可见资产目录。

## 当前项目

<!-- PROJECT-INIT: 初始化时填写并删除本注释 -->

- 项目名称：待初始化。
- 研究问题：待初始化。
- 研究对象与分析单位：待初始化。
- 项目边界：待初始化。
- 正式交付：待初始化。
- Multica 项目入口：待接入。

## 开始使用

从明确的模板发布或候选提交创建独立项目、核实独立 origin 后，执行 `INITIALIZE_PROJECT.md`。先写清全部研究阶段的目标和依赖，再把当前获准阶段细化为可验收的任务，完成资产、环境、平台绑定及一次演示后删除该清单。初始化不要求逐个填写目录说明。

需要 Python 3.10 及以上、Git、`uv` 和本机持久执行能力。v4 外置服务首版面向已验证的 Linux 主机；原生兼容运行器保留 systemd、launchd 和任务计划程序适配。命令已实现与真实平台验收分别记录，服务不可用时不能回退为正式后台运行。

```text
python scripts/research.py setup --harness v4 --service-socket <absolute-socket-path> --project-id <project-uuid>
python scripts/research.py context --issue-id <issue-uuid>
python scripts/research.py checkpoint --file <explicit-project-file>
python scripts/research.py run --issue-id <issue-uuid> --entry <registered-entry> --request-key <stable-intent-key> -- <command> <arguments>
python scripts/research.py status <run-id>
python scripts/research.py deliver --issue-id <issue-uuid> --context-ref <context-receipt> --artifact <path> --check <check-name> --research-impact <text> --scope-complete
python scripts/research.py export --run-id <run-id> --file <relative-output> --kind figures --accepted-by <acceptance-reference>
```

已登记 v4 发布器的项目在完整记录准备好后，显式使用 `publish --record <delivery_path> --issue-id <current-issue-uuid> --summary <finding-and-next-action>` 原样发布并登记；先按执行文档取得实际版本锚与上下文回执。部署者单独登记发布器路径和哈希，模板不会自动部署或启用发布。

尖括号内容须替换为本任务的真实值。参数、环境和无计算交付的示例见 [研究执行](docs/workflows/research-execution.md)；`--help` 提供当前命令语法。源码编号便于阅读，实际执行依赖以 Multica 任务为准，不维护根 README 命令总表。

## 目录与信息归属

| 位置 | 内容 |
|---|---|
| [AGENTS.md](AGENTS.md) | 执行者必读路线和研究边界 |
| [docs/plans/research-plan.md](docs/plans/research-plan.md) | 科学问题、研究设计、阶段成果和证据标准 |
| [docs/project-preferences.md](docs/project-preferences.md) | 稳定环境、资源默认值和协作偏好 |
| [docs/data-sources.md](docs/data-sources.md) | 数据来源、版本、许可与校验信息 |
| [DASHBOARD.md](DASHBOARD.md) | 来自 Multica 的阶段、待决事项与成果快照 |
| [src/](src/README.md) | 编号研究脚本或实质研究模块；保持 `package=false` |
| [experiments/](experiments/README.md) | 科学问题、观察、解释边界、决策及下游影响 |
| [outputs/](outputs/README.md) | 选入论文并由 Git 跟踪的图表与来源索引 |
| [scripts/](scripts/README.md) | 运行入口、TeX 检查及投稿工具 |
| [docs/](docs/README.md) | 数据、执行、协作、写作约定和手稿 |
| [.agents/](.agents/README.md) | 项目独有且已验证可复用的技能 |

默认资产位置为 Linux/macOS 的 `~/ResearchAssets/<仓库名>/`，Windows 的 `%USERPROFILE%\ResearchAssets\<仓库名>\`。仓库名来自 `origin`；多个工作树共用同一映射，而不是各自创建数据副本。

```text
ResearchAssets/<仓库名>/
  inputs/                 固定版本输入
  envs/                   稳定依赖环境
  runs/<运行编号>/
    code/                 已提交代码的固定快照
    data/                 本次中间数据
    outputs/              候选图表及其他运行产物
    logs/
    run.json
  deliveries/             不可变交付记录，支持无计算任务
  checkpoints/            明确文件范围的不可变 patch 记录
```

凭据不写入映射和运行记录。资产映射、数据边界及共享输入规则见 [数据生命周期](docs/workflows/data-lifecycle.md)。模板不提供跨机器资产同步。

## 论文工具

```bash
make init-tex
make check-tex-style
make manuscript
make manuscript-diff
make prepare-elsevier-submission
```

默认使用 CTAN `elsarticle` 和 Harvard author-year 样式，正文一行一句。手稿直接引用 Git 中选定的正式图表，干净检出不依赖外部研究资产即可编译。构建和投稿目录不提交。

以上论文工具依赖 Bash、Make 及 TeX；Windows 需另行准备相应环境。研究运行入口的三平台适配不代表论文工具均已原生跨平台。各平台持久执行须在对应系统实测，未实测的环境不算通过验收。详情见 [手稿工作流](docs/workflows/manuscript.md)。

## 历史示例

[Titanic 三阶段导读](docs/examples/titanic-walkthrough.md)保留旧人工流程的固定提交，用于理解研究证据和论文衔接。导读提供与本版 Multica 流程的对应关系；不要整体合并、拣选或照搬示例分支的数据路径和看板规则。

## License

MIT
