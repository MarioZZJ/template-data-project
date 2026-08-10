# GitHub 论文协作

## 批注与修改

对当前正文提出意见时使用 Issue，并附上指向具体 commit 和行范围的 GitHub permalink。
Issue 说明问题背景、建议方向和是否需要作者确认，不为没有正文改动的问题创建空 PR。

实际改写正文时使用小 PR。
一个 PR 尽量只处理一个段落、论证点、图注、术语统一或一组紧密相关的图表变化，并说明对应 Issue、数据或实验影响和本地检查。

## Review 边界

PR review 审查本次改动。
对未改正文的大段新意见回到 Issue，并引用固定正文位置。
不通过无意义空白变化制造 diff。

## PDF 产物

PR workflow 使用 `git-latexdiff` 对比 base 与 head，生成供审阅的 `manuscript-diff.pdf` artifact。
Release workflow 编译并附加阅读版 `main.pdf`。
这些 PDF 是沟通或发布产物，TeX 源和正式中央图表仍是事实来源。

## 本地检查

```bash
make check-tex-style
make manuscript
make manuscript-diff
```

需要指定 diff 范围时：

```bash
BASE_REF=origin/master HEAD_REF=HEAD make manuscript-diff
```

提交前确认正文结论与 `DASHBOARD.md`、实验记录和 `outputs/` 中的实际证据一致。
