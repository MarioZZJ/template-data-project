# 研究执行

## 从阶段授权到成果

研究计划说明科学依赖和证据标准；Multica 父任务说明阶段授权，子任务承载可检验成果及执行依赖。源码编号提供阅读顺序，不能替代平台任务。后继保留在 `backlog`，输入齐备并处于授权范围内才启动；`stage` 完成通知本身不证明输入存在。

一个任务包含完整范围的实施、自检、结果解释和交付。长计算不拆成需要人手接力的“提交”和“等待”任务。普通任务自检，阶段预先指定的关键成果才需要独立复核。

## 八个入口

在仓库根运行 `python scripts/research.py --help`，各子命令也支持 `--help`。全局 `--repo PATH` 可显式指定仓库，`--assets-home PATH` 用于已决定的本机资产根布局；通常使用默认的 `~/ResearchAssets`。

### `setup`：本机映射与环境

```text
python scripts/research.py setup --harness v4 --service-socket <absolute-socket-path> --project-id <project-uuid>
python scripts/research.py setup --project-name <readable-alias>
python scripts/research.py setup --extra mssql
```

默认使用 `uv.lock` 准备外部稳定环境；MSSQL 为可选依赖。v4 的本机映射登记服务 socket、项目身份和执行成员白名单；`RESEARCHD_SOCKET` 可覆盖已登记 socket。服务能力探测失败会明确列出未就绪项，不能据此启动正式长作业。`setup` 检查平台执行能力，不开展研究计算，也不自行创建 Multica 任务。无第三方依赖的流程演示可显式用 `--stdlib`，不能用它绕过真实研究依赖。

交付发布器也由部署者在 Agent 任务外单独登记，不能从任务正文、评论或环境变量挑选程序。部署者核验已验证服务 release 中的独立 `publish_delivery.py`，再提供实际绝对路径及 SHA256；本模板不包含第二份发布实现，也不预填任何机器路径或哈希：

```text
python scripts/research.py setup --harness v4 --service-socket <registered-absolute-socket> --project-id <project-uuid> --multica-cwd <authorized-cli-directory> --publisher-helper <verified-release-helper-absolute-path> --publisher-sha256 <verified-helper-sha256>
```

这会将 `delivery_publisher` 的协议、路径及哈希存入本机 `projects.json` 项目映射。helper 必须位于临时研究检出之外；修改 release 后必须重新核验并登记新哈希。当前任务令牌环境不能登记发布器。映射是部署配置，Agent 不自行改写；这不是同一操作系统用户之间的安全隔离。登记成功也不代表真实发布验收，尚未登记的项目不能使用 `publish`。

### `context`：读取当前事实

```text
python scripts/research.py context --issue-id <issue-uuid> --source-run-id <current-task-uuid>
```

优先使用登记服务；服务不可用或未返回平台合同原文时，回退原生 Multica CLI 的只读查询，读取当前 issue、父级合同、全部线程及编辑后的意见、活跃执行和研究计划入口。使用 `--multica-cwd` 或 `MULTICA_CLI_CWD` 指定本机允许的 CLI 目录。执行者列表只取登记的研究成员白名单，不返回运维成员或运行时凭据。

输出来源和未取得项，不把不完整上下文称为有效授权。派生快照不能代替必要原文；新意见与编辑内容均按当前数据读取，不仅依据 created_at 增量。

在真实来源执行中读取服务上下文会返回 `context_ref`，固定当时的父级合同、相关计划和政策版本。正式交付引用本来源执行的这个回执；服务不可用时的 CLI 回退只提供事实，不伪造回执。父级决定或计划改变后须重新读懂当前要求再形成新交付，不能在发布时只抓最新版本冒充此前已读。

### `checkpoint`：保存明确范围

```text
python scripts/research.py checkpoint --file src/030-main_analysis.py --file experiments/main/README.md
python scripts/research.py checkpoint --file src/030-main_analysis.py --commit --message-file <reviewed-message-file>
```

默认只保存具备路径、哈希和基线的不可变 patch 记录，并明确 `committed=false`；它不是已批准代码快照，不能用来绕过 run 的固定代码要求。`--commit` 是显式本地提交动作：先读取本机唯一署名规则，核对用户身份与消息中的实际模型和 Agent 署名，仅提交指定已被 Git 跟踪的文件，保留其他暂存及未暂存内容。新文件先由执行者显式 `git add -- <exact-path>`，不使用 `git add -A`。消息不得猜测实际模型标识；权限或签名失败不能绕过，也不把 patch 称为 commit。此命令从不 push。

### `run`：固定代码并持久执行

```text
python scripts/research.py run --issue-id <issue-uuid> --entry <registered-entry> --request-key <stable-intent-key> --parameters-json <parameters-json> -- python src/030-main_analysis.py
```

这是命令结构示例，路径、issue UUID 和脚本都需替换成真实任务内容。`--input` 登记固定文件；数据集使用带版本及校验信息的清单，不把目录当作已核验输入。要求本次实际改动已提交且工作树干净。v4 把提交意图交给已登记外置服务，由服务固定代码并调用系统托管；服务不可用就拒绝正式运行。运行入口不会替执行者提交代码。唯一例外是根 `AGENTS.md` 中由 Multica 写入、具有精确边界标记的未暂存运行上下文：剥离该块后正文必须与已提交版本一致，其他文件、暂存区、权限或链接类型有改动仍会拒绝启动。该自动块无需提交，运行记录保留排除证据，代码快照仍取已提交版本。提交边界不清楚时先整理本任务版本，不丢弃已有修改，也不导出遗漏本次改动的旧 `HEAD`。

- 输入映射、完整命令、代码版本、环境和运行编号写入 `run.json`；`DATA_ROOT`、`RUN_DIR`、`OUTPUT_ROOT` 每次独立注入。
- 脚本从固定输入读取，中间数据写 `RUN_DIR/data`，候选图表写 `OUTPUT_ROOT`；不写主检出的共享输出位置。
- 环境不能指向临时工作树中的 editable 安装。Multica 清理工作树后，代码导入、子进程和日志仍须正常。
- 用 `--deadline`、`--attempt-limit` 记录相应限制；`--budget-json` 保存资源预算元数据，实际费用上限需由研究命令或服务端限制落实。所有额度来自阶段授权，不能因重启重置。
- v4 首版由已验证的 Linux 外置服务托管，受理回执明确 `accepted`、`job_id`、代码位置、输出根和绝对截止。同一 `request_key` 返回原作业，内容冲突拒绝；通知失败不能改 key 重提。服务白名单入口与参数必须一致，不能提交任意宿主命令。
- 原生运行器保留 Linux systemd、macOS launchd、Windows 任务计划程序适配，供明确选择 legacy 的兼容项目及基础设施验收；v4 项目禁止 `--foreground` 绕过登记服务。平台支持以对应机器的实际验收为准。

退出模型会话后由系统继续计算，外置服务处理完成事件。程序返回成功只表明运行完成，不能直接关闭研究任务。

### `status`：检查运行与生成平台快照

```text
python scripts/research.py status <run-id>
python scripts/research.py status --dashboard-from <multica-snapshot.json> --dashboard DASHBOARD.md
```

默认 `status` 只读取实际作业及产物记录。已证明本机托管作业中断时，可显式使用 `status <run-id> --reconcile` 补记失败证据；该操作不会重新提交计算，系统查询不确定时不推断任务失败。

看板输入由配套桥接的 `snapshot` 从 Multica 导出，包含 `source`（也接受 `source_url`）、`generated_at` 和 `issues`；每个任务含 `identifier`、`title`、`status`、`url`。可选 `phases`、`decisions`、`artifacts` 提供阶段、待决事项和成果，缺少时显示未提供。仅替换 `BEGIN/END MULTICA STATUS` 标记区域，保留区域外文字和原始采集时间；不从本地运行成功推断任务完成。看板在阶段交付或需要查看时生成，不要求每次运行提交一次快照。

### `deliver`：准备与登记交付

无计算任务可以省略 `--run-id`，仍需产物、实际检查和研究影响。只有确实完成全量范围才能写 `--scope-complete`；命令记录声明，不替执行者作科学判断。临时工作树内的产物会复制到资产根的稳定交付目录，已有稳定运行产物保留原位置，避免会话结束后文件失效。

实际完整交付者完成自检并解释研究影响；局部准备、试跑和分工报告不等于全任务完成。全任务具备交付条件后，由它在属于原 issue 的执行中按以下顺序发布：

1. 当前 issue 内执行先处理完其他需要上传的附件，将任务置为 `in_review` 且不启动新运行，再读取当前 issue 版本 `R`。读取后只新增一份最终交付 JSON 附件和一条交付评论。
2. 准备交付，`--issue-revision` 填写 `R + 2`：上传这一份新 JSON 附件增加一次版本，创建评论再增加一次版本。此计算只适用于读取 `R` 后恰好新增一份附件的默认流程。

```text
python scripts/research.py deliver --issue-id <issue-uuid> --context-ref <context-receipt> --run-id <run-id> --artifact <artifact-path> --check <completed-check> --research-impact <explanation> --scope-complete --issue-revision <R-plus-two>
```

3. 已登记发布器的 v4 项目使用下节 `publish`，由当前任务执行身份附加生成的完整 `research-delivery-*.json` 并登记。其他项目继续按已有人工发布与登记流程；均不缩写、重建或在正文再复制一份记录。
4. 核对创建评论后的实际 issue 版本确为 `R + 2`（`publish` 的登记 helper 会回读校验）；如有新评论、额外附件或其他竞争，读取新要求并重新交付，不能只改旧记录版本或放宽版本校验。未使用 `publish` 的 v4 流程使用下方 `--submit-comment-id` 登记已经发布的来源评论，再结束来源执行，不再修改此 issue；来源执行完成本身不增加 issue 版本。创建评论接口没有版本条件参数，不能假设评论本身已锁住并发。

未给 `--issue-revision` 的记录只用于本地准备，不能自动关闭任务。交付文件采用 `research-delivery/v1`，不可变地保存在资产根 `deliveries/`；运行 `deliver` 本身不会发布评论或改变平台状态。

v4 生成记录时还要求实际代码已保存，写入 `code_ref`，并用 `--context-ref` 引用本来源执行实际读取合同的回执。以下两个互斥动作只调用登记服务，不创建第二份交付，也不代写 Agent 来源评论：

```text
python scripts/research.py deliver --issue-id <issue-uuid> --submit-comment-id <already-posted-comment-uuid>
python scripts/research.py deliver --issue-id <issue-uuid> --consume-event <event-id> --source-run-id <current-task-uuid> --evidence-path <stable-note> --judgment <research-judgment> --next-action <next-action>
```

登记返回候选不等于 `done`，服务等待来源执行结束再校验。结果消费在最终交付前单独登记；稳定说明须在本项目资产根内，包含真实 event ID、job ID、完整判断和下一动作。收到通知、消费结果、最终交付和科学验收是不同事实。`status` 始终保留只读语义。

预先指定了独立复核时，使用两步流程固定同一交付与产物：

```text
python scripts/research.py deliver --draft --review-required --issue-id <issue-uuid> --context-ref <context-receipt> --run-id <run-id> --artifact <artifact-path> --check <completed-check> --research-impact <explanation> --scope-complete
```

草稿 `*.draft.json` 的状态是 `awaiting_review`，不能用于关闭任务。独立复核者检查固定产物后，发布 `research-review/v1` 记录，保留草稿的同一 `delivery_id` 和完整 `artifacts` 数组，给出是否通过；等待该复核来源执行完成。复核未通过时先修正、建立并复核新草稿，不把旧复核套用到改变后的产物。

通过复核后，由实际交付者回到原 issue 的执行先处理完其他附件，按上述方式进入 `in_review` 并读取 `R`。之后只新增一份最终 JSON 附件及交付评论，以 `R + 2` 为版本锚，并将复核评论 UUID 用于最终记录：

```text
python scripts/research.py deliver --finalize <draft-path> --issue-id <issue-uuid> --context-ref <current-source-context-receipt> --review-evidence <review-comment-uuid> --issue-revision <R-plus-two>
```

`--finalize` 不重新传入产物、自检或范围参数；它核验产物哈希未变，保留同一交付编号和产物，生成一次最终文件，不覆盖草稿或已有最终记录。随后按普通交付步骤上传最终 JSON 附件并核对版本。桥接独立核验复核者身份、复核来源执行和证据，命令成功不代替平台复核验证。

服务只处理已登记可自动完成的范围，核验完整范围、实际产物、自检、必要复核、已完成且属于该 issue 的来源执行和最新交付，再按版本条件更新 `done`。`human` 不自动收尾；阶段是否自动完成由登记政策和下一阶段授权决定。原生 `run_only` 回调的独立会话不能冒充该 issue 的来源执行。

### `publish`：原样发布完整交付并登记

```text
python scripts/research.py publish --record <delivery_path-from-deliver> --issue-id <current-issue-uuid> --summary <finding-and-next-action>
```

这是显式平台写操作；`deliver` 默认仍只准备不可变本地文件。先完成上节的 `in_review`、真实版本锚及 `context_ref` 步骤，再将 `deliver` 返回的原始文件路径交给 `publish`，包括独立复核后生成的最终文件。不要手工重建 JSON，也不单独重传其中部分字段。评论触发的执行按平台要求添加 `--parent <actual-trigger-comment-uuid>`。摘要限 300 字符，不含 mention 或代码围栏；研究发现、依据及限制留在完整成果附件中。

入口仅使用本机登记的 helper、socket 和 CLI 目录，不接受任务提供的 helper 或解释器，也不使用 `RESEARCHD_SOCKET`、`MULTICA_CLI_CWD` 覆盖发布目的地。它核验 helper 哈希，用当前 Python 隔离模式调用同一已验证发布器，并要求当前 `MULTICA_TASK_ID`、`MULTICA_AGENT_ID` 和任务范围令牌；令牌只通过现有进程环境继承，不写入命令或交付。原始记录必须位于本项目 `deliveries/`，始终作为完整附件发送。

来源是否属于该 issue 且仍在执行、当前归属与 `in_review`、附件和评论后的真实 revision、原始记录完整性及服务登记回读，由同一个 helper 校验；合同 `context_ref`、必要复核及自动收尾仍由登记服务独立检查。入口不更改旧记录的版本、不补造上下文、不自行把任务置为 `done`。`human` 登记回执仍是待人审，不代表通过完整交付或科学验收。

发布结果不明时保留原记录和同名 `*.publication.json` 意图日志，先核对原评论及服务记录；入口不会自动重发，不换文件、摘要或来源身份绕过原意图。发布器找不到确认过的原评论时会停止，而不是再发一条。只有服务回读确认同一完整记录后才返回已登记，来源结束后的自动收尾另行核验。

此连接使用 POSIX 文件锁与 Unix socket，当前真实验收以 Linux 部署为准；Windows 不支持 `publish`，macOS 的真实服务链路尚需当地验证。其余本地入口继续兼容 Python 3.10–3.13 和原有平台；安装模板不会部署发布器或迁移已有项目。

### `export`：选择正式图表

```text
python scripts/research.py export --run-id <run-id> --file <relative-output> --kind figures --accepted-by <acceptance-reference>
```

`--file` 相对于该运行的输出目录，`--kind` 为 `figures` 或 `tables`。只导出已选定成果，写入 `outputs/provenance.json`，保留输入、参数、命令、代码、运行及验收来源。实验和手稿引用正式图表，不复制第二份文件。

## 脚本与科学检查

研究脚本说明 `Purpose`、`Inputs`、`Outputs`、`Run`。固定随机种子或记录随机性，对关键样本量、唯一键、缺失、范围与完整性作检查，失败返回非零状态并给出可定位证据。完整命令和参数进入运行记录，不再复制到多个 README。

执行者解释结果对研究问题、样本、识别条件、论文呈现和下游任务的影响；零结果与相反结果保留并继续既定设计。试算、单一诊断或模型共识不替代全量证据。

## 完成事件、暂停与恢复

外置服务由工作区管理员固定版本并交给系统托管，逐项目登记入口、阶段、资产根、资源范围、执行者及政策。`setup` 不替代服务部署，不能自行扩大白名单。既有项目仍使用原生执行器与旧桥接时，继续按其登记政策处理，不因模板更新自动迁移。

v4 完成或异常事件直接评论回原 issue 的实际执行者。事件台账分别核对投递、关联运行和本作业被消费的证据；排队、HTTP 200 或一句“收到”不代表研究接续完成。同轮合并多个事件时逐项核对；会话无法恢复时按当前合同及持久记录重建，不重算。

通知重试与重新计算分开。用户暂停、human 等待和终止任务收到迟到结果时保留证据，不自动重开；预算、次数和截止跨重启保留。服务凭据独立保管，不使用会话结束即失效的任务令牌。一个登记范围只允许一个通知及收尾写入者。

只在隔离项目验收持久执行、工作树删除、重复请求、通知不明、暂停和恢复；两现有研究项目的治理指令单独交付，不在本模板初始化时执行迁移。未实测平台及能力明确标注。
