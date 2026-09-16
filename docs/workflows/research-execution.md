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

这是命令结构示例，路径、issue UUID 和脚本都需替换成真实任务内容。`--input` 登记固定文件；数据集使用带版本及校验信息的清单，不把目录当作已核验输入。默认要求本次实际改动已提交且工作树干净，再复制固定代码并调用系统托管；运行入口不会替执行者提交代码。唯一例外是根 `AGENTS.md` 中由 Multica 写入、具有精确边界标记的未暂存运行上下文：剥离该块后正文必须与已提交版本一致，其他文件、暂存区、权限或链接类型有改动仍会拒绝启动。该自动块无需提交，运行记录保留排除证据，代码快照仍取已提交版本。提交边界不清楚时先整理本任务版本，不丢弃已有修改，也不导出遗漏本次改动的旧 `HEAD`。

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

默认 `status` 只读取实际作业及产物记录。已证明本机托管作业中断时，可显式使用 `status <run-id> --reconcile` 补记失败证据；该操作不会重新提交计算，系统查询不确定时不推断任务失败。

看板输入由配套桥接的 `snapshot` 从 Multica 导出，包含 `source`（也接受 `source_url`）、`generated_at` 和 `issues`；每个任务含 `identifier`、`title`、`status`、`url`。可选 `phases`、`decisions`、`artifacts` 提供阶段、待决事项和成果，缺少时显示未提供。仅替换 `BEGIN/END MULTICA STATUS` 标记区域，保留区域外文字和原始采集时间；不从本地运行成功推断任务完成。看板在阶段交付或需要查看时生成，不要求每次运行提交一次快照。

### `deliver`：准备与发布交付

无计算任务可以省略 `--run-id`，仍需产物、实际检查和研究影响。只有确实完成全量范围才能写 `--scope-complete`；命令记录声明，不替执行者作科学判断。临时工作树内的产物会复制到资产根的稳定交付目录，已有稳定运行产物保留原位置，避免会话结束后文件失效。

普通自检交付先完成检查，再按以下顺序发布：

1. 当前 issue 内执行先处理完其他需要上传的附件，将任务置为 `in_review` 且不启动新运行，再读取当前 issue 版本 `R`。读取后只新增一份最终交付 JSON 附件和一条交付评论。
2. 准备交付，`--issue-revision` 填写 `R + 2`：上传这一份新 JSON 附件增加一次版本，创建评论再增加一次版本。此计算只适用于读取 `R` 后恰好新增一份附件的默认流程。

```text
python scripts/research.py deliver --issue-id <issue-uuid> --run-id <run-id> --artifact <artifact-path> --check <completed-check> --research-impact <explanation> --scope-complete --issue-revision <R-plus-two>
```

3. 通过当前任务执行身份发一条短交付评论，附生成的 `research-delivery-*.json`。不要同时在评论正文再复制一份相同记录。
4. 核对创建评论响应的 issue 版本确为 `R + 2`；如有新评论、额外附件或其他竞争，读取新要求并重新交付，不能只改旧记录版本或放宽版本校验。随后结束来源执行，不再修改此 issue；来源执行完成本身不增加 issue 版本。创建评论接口没有版本条件参数，不能假设评论本身已锁住并发。

未给 `--issue-revision` 的记录只用于本地准备，不能自动关闭任务。交付文件采用 `research-delivery/v1`，不可变地保存在资产根 `deliveries/`；运行 `deliver` 本身不会发布评论或改变平台状态。

预先指定了独立复核时，使用两步流程固定同一交付与产物：

```text
python scripts/research.py deliver --draft --review-required --issue-id <issue-uuid> --run-id <run-id> --artifact <artifact-path> --check <completed-check> --research-impact <explanation> --scope-complete
```

草稿 `*.draft.json` 的状态是 `awaiting_review`，不能用于关闭任务。独立复核者检查固定产物后，发布 `research-review/v1` 记录，保留草稿的同一 `delivery_id` 和完整 `artifacts` 数组，给出是否通过；等待该复核来源执行完成。复核未通过时先修正、建立并复核新草稿，不把旧复核套用到改变后的产物。

通过复核后，回到原 issue 的执行先处理完其他附件，按上述方式进入 `in_review` 并读取 `R`。之后只新增一份最终 JSON 附件及交付评论，以 `R + 2` 为版本锚，并将复核评论 UUID 用于最终记录：

```text
python scripts/research.py deliver --finalize <draft-path> --issue-id <issue-uuid> --review-evidence <review-comment-uuid> --issue-revision <R-plus-two>
```

`--finalize` 不重新传入产物、自检或范围参数；它核验产物哈希未变，保留同一交付编号和产物，生成一次最终文件，不覆盖草稿或已有最终记录。随后按普通交付步骤上传最终 JSON 附件并核对版本。桥接独立核验复核者身份、复核来源执行和证据，命令成功不代替平台复核验证。

桥接只处理已登记可自动完成的子任务，核验完整范围、实际产物、自检、必要复核、已完成且属于该 issue 的来源执行和最新交付，再按版本条件更新 `done`。原生 `run_only` 回调的独立会话不能冒充该 issue 的来源执行。父任务保持人工验收。

### `export`：选择正式图表

```text
python scripts/research.py export --run-id <run-id> --file <relative-output> --kind figures --accepted-by <acceptance-reference>
```

`--file` 相对于该运行的输出目录，`--kind` 为 `figures` 或 `tables`。只导出已选定成果，写入 `outputs/provenance.json`，保留输入、参数、命令、代码、运行及验收来源。实验和手稿引用正式图表，不复制第二份文件。

## 脚本与科学检查

研究脚本说明 `Purpose`、`Inputs`、`Outputs`、`Run`。固定随机种子或记录随机性，对关键样本量、唯一键、缺失、范围与完整性作检查，失败返回非零状态并给出可定位证据。完整命令和参数进入运行记录，不再复制到多个 README。

执行者解释结果对研究问题、样本、识别条件、论文呈现和下游任务的影响；零结果与相反结果保留并继续既定设计。试算、单一诊断或模型共识不替代全量证据。

## 完成事件、暂停与恢复

桥接程序须先由工作区管理员部署为持续运行的系统服务，并按受保护策略登记本项目、阶段、子任务、资产根及原生 `run_only` webhook。模板 `setup` 不替代服务部署；未登记任务默认手动、未授权。接入步骤见初始化清单，实际配置与密钥保留在本机受保护位置。

桥接与模板共用运行记录，负责完成通知、交付检查和父任务接续，不另建研究任务调度平台。状态不变时不唤醒模型。结果先到 `run_only` 接收者，再由它核验原 issue 并发一次带事件标记的负责人唤醒评论；真实研究交付由随后属于原 issue 的执行完成。通知受理、独立接收会话完成、原 issue 真正接续是三个不同证据，必须核对最后一步。未交接事件保留并去重恢复。

通知重试与重新计算分开。运行时离线后恢复通知，不重复提交付费计算；用户暂停继续保持，预算、次数和截止时间跨重启保留。桥接凭据独立保管，不使用会话结束即失效的任务令牌。

在实际平台分别验证持久执行、工作树删除、重复事件和暂停恢复。没有对应系统实测的适配只能标为未验收。
