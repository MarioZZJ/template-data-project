# 仓库工具

这里保存跨研究内容的运行与交付入口，以及 TeX、论文差异和投稿工具。具体取数、样本构造、分析和图表步骤属于 `src/`。

## 研究运行入口

`research.py` 提供 `setup / context / checkpoint / run / status / deliver / export`，由 Python 3.10 及以上执行；完整命令和边界见 [研究执行](../docs/workflows/research-execution.md)。Makefile 是便捷别名，研究入口在 Windows 不要求 Make。

入口管理本机映射、只读上下文、明确范围的代码保存、固定代码与环境、服务提交、交付记录和正式产物导出。v4 正式作业只经登记服务；原生兼容适配不会在服务失效时自动接管。阶段授权与任务依赖保留在 Multica，完成事件和已授权收尾由配套桥接程序处理，不在仓库另建任务调度服务或一键执行全部研究的隐式授权入口。

## 论文工具

- `init-tex-env.sh`：TeX 环境检查。
- `check-tex-sentence-lines.py`：TeX 一行一句检查。
- `build-manuscript-diff.sh`：PR 范围的差异 PDF。
- `prepare-elsevier-submission.sh`：从手稿和正式图表生成投稿包。

论文工具依赖 Bash、Make 和相应 TeX 命令，Windows 需单独准备这些运行条件。它们的跨平台情况与研究持久作业适配分别验收。

## 修改检查

按受影响行为验证：运行接口检查真实输入输出、进程托管与恢复；shell 脚本至少 `bash -n` 并执行其直接路径；论文工具检查产物非空和干净检出的引用。生成目录及临时文件不提交。

参见 [手稿工作流](../docs/workflows/manuscript.md)、[协作约定](../docs/workflows/collaboration.md)。
