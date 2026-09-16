# 研究执行

## 从阶段授权到成果

研究计划说明科学依赖和证据标准；Multica 父任务说明阶段授权，子任务承载可检验成果及执行依赖。源码编号提供阅读顺序，不能替代平台任务。后继保留在 `backlog`，输入齐备并处于授权范围内才启动；`stage` 完成通知本身不证明输入存在。

一个任务包含完整范围的实施、自检、结果解释和交付。长计算不拆成需要人手接力的“提交”和“等待”任务。普通任务自检，阶段预先指定的关键成果才需要独立复核。

## 五个入口

在仓库根运行 `python scripts/research.py --help`，各子命令也支持 `--help`。全局 `--repo PATH` 可显式指定仓库，`--assets-home PATH` 用于已决定的本机资产根布局；通常使用默认的 `~/ResearchAssets`。

### `setup`：本机映射与环境

```text
python scripts/research.py setup
python scripts/research.py setup --project-name <readable-alias>
python scripts/research.py setup --extra mssql
```

默认使用 `uv.lock` 准备外部稳定环境；MSSQL 为可选依赖。`setup` 检查平台执行能力，不开展研究计算，也不自行创建 Multica 任务。无第三方依赖的流程演示可显式用 `--stdlib`，不能用它绕过真实研究依赖。

### `run`：固定代码并持久执行

```text
python scripts/research.py run --issue-id <issue-uuid> --input sample=<fixed-input-path> -- python src/030-main_analysis.py
```

这是命令结构示例，路径、issue UUID 和脚本都需替换成真实任务内容。`--input` 登记固定文件；数据集使用带版本及校验信息的清单，不把目录当作已核验输入。默认要求工作树干净且本次实际改动已提交，再复制固定代码并调用系统托管；运行入口不会替执行者提交代码。提交边界不清楚时先整理本任务版本，不丢弃已有修改，也不导出遗漏本次改动的旧 `HEAD`。

- 输入映射、完整命令、代码版本、环境和运行编号写入 `run.json`；`DATA_ROOT`、`RUN_DIR`、`OUTPUT_ROOT` 每次独立注入。
- 脚本从固定输入读取，中间数据写 `RUN_DIR/data`，候选图表写 `OUTPUT_ROOT`；不写主检出的共享输出位置。
- 环境不能指向临时工作树中的 editable 安装。Multica 清理工作树后，代码导入、子进程和日志仍须正常。
- 用 `--deadline`、`--attempt-limit` 记录相应限制；`--budget-json` 保存资源预算元数据，实际费用上限需由研究命令或服务端限制落实。所有额度来自阶段授权，不能因重启重置。
- 默认通过 Linux systemd、macOS launchd、Windows 任务计划程序托管。`--foreground` 仅作同步诊断，不提供会话退出后的存活保证。

退出模型会话后由系统继续计算，桥接程序处理完成事件。程序返回成功只表明运行完成，不能直接关闭研究任务。

### `status`：检查运行与生成平台快照

```text
python scripts/research.py status <run-id>
python scripts/research.py status --dashboard-from <multica-snapshot.json> --dashboard DASHBOARD.md
```

运行状态来自实际作业及产物记录。看板输入是 Multica 导出的 JSON 包装，至少包含 `source_url`、`generated_at` 和 `issues`；每个任务含 `identifier`、`title`、`status`、`url`。保留平台状态和采集时间，不从本地运行成功推断任务完成。看板在阶段交付或需要查看时生成，不要求每次运行提交一次快照。

### `deliver`：形成交付记录

```text
python scripts/research.py deliver --issue-id <issue-uuid> --run-id <run-id> --artifact <artifact-path> --check <completed-check> --research-impact <explanation> --scope-complete
```

无计算任务省略 `--run-id`，仍需产物、实际检查和研究影响。只有确实完成全量范围才能写 `--scope-complete`；存在预定独立复核时附 `--review-required --review-evidence <evidence>`。命令记录声明，不替执行者进行科学判断或实际检查。

交付文件采用 `research-delivery/v1`，不可变地保存在资产根 `deliveries/`。由当前任务执行身份将记录附在简短交付评论中，并把 issue 置为 `in_review`；单独运行 `deliver` 不代表已经发布或关闭任务。

桥接程序只处理已登记可自动完成的子任务，核验完整范围、实际产物、自检、预定复核、平台执行身份和最新交付，再按 issue 版本条件更新 `done`。出现新评论或版本冲突必须重新读取要求，不能只刷新版本重试。父任务保持人工验收。

### `export`：选择正式图表

```text
python scripts/research.py export --run-id <run-id> --file <relative-output> --kind figures --accepted-by <acceptance-reference>
```

`--file` 相对于该运行的输出目录，`--kind` 为 `figures` 或 `tables`。只导出已选定成果，写入 `outputs/provenance.json`，保留输入、参数、命令、代码、运行及验收来源。实验和手稿引用正式图表，不复制第二份文件。

## 脚本与科学检查

研究脚本说明 `Purpose`、`Inputs`、`Outputs`、`Run`。固定随机种子或记录随机性，对关键样本量、唯一键、缺失、范围与完整性作检查，失败返回非零状态并给出可定位证据。完整命令和参数进入运行记录，不再复制到多个 README。

执行者解释结果对研究问题、样本、识别条件、论文呈现和下游任务的影响；零结果与相反结果保留并继续既定设计。试算、单一诊断或模型共识不替代全量证据。

## 完成事件、暂停与恢复

桥接程序与模板共用运行记录，负责完成通知、交付检查和父任务接续，不另建研究任务调度平台。状态不变时不唤醒模型；通知投递后检查真实接续运行，未交接事件保留并去重恢复。

通知重试与重新计算分开。运行时离线后恢复通知，不重复提交付费计算；用户暂停继续保持，预算、次数和截止时间跨重启保留。桥接凭据独立保管，不使用会话结束即失效的任务令牌。

在实际平台分别验证持久执行、工作树删除、重复事件和暂停恢复。没有对应系统实测的适配只能标为未验收。
