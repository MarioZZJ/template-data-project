# GitHub 论文协作流程

本文档说明 GitHub 上的论文写作协作规则。
它补充 @docs/agents/tex-manuscript-workflow.md，不替代现有 TeX 手稿入口。

## 不变约束

- 默认手稿入口仍是 @docs/writing/manuscript/main.tex。
- TeX 正文仍保持一句一行。
- 段落之间仍保留空行。
- 普通项目说明不要做成 Codex skill。
- 不为了制造 PR 而提交空改动、无意义空白改动或格式抖动。

## 批注和修改

批注用于对当前正文提出意见。
它不要求立刻改正文，也不需要创建 PR。

修改用于实际改写正文。
它必须通过小 PR 提交，并让协作者用 PR review 审阅改动。

不要混淆这两件事。
Issue 是讨论当前正文的问题。
PR 是审查已经提交的正文改动。

## 批注流程

对现有正文提出意见时，创建 Issue。
Issue 应包含：

- 问题背景。
- GitHub permalink，指向 @docs/writing/manuscript/main.tex 的具体行或行范围。
- 建议方向，必要时给一两句候选改写。
- 是否需要作者确认后再动正文。

GitHub permalink 应指向具体 commit 上的行，而不是浮动的分支行号。
这样正文继续变化时，批注仍能追踪到当时看到的文本。

没有正文改动时，不要强行创建空 PR。
如果只是“这里需要讨论”，用 Issue。

## 修改流程

实际改写正文时，创建小 PR。
每个 PR 应尽量只处理一个明确问题，例如一个段落、一个论证点、一个图注或一个术语统一。

PR 应包含：

- 改了什么。
- 为什么要改。
- 对应 Issue 或正文 permalink。
- 是否影响图表、参考文献、数据或实验结论。
- 本地检查结果。

PR review comments 用于审查本次改动。
不要把对未改动正文的大段新意见塞进 PR review。
那种意见应回到 Issue，并贴正文 permalink。

## 自动 PDF 产物

GitHub Actions 会编译当前 PR 的 `main.pdf`。
PR 事件还会用 `git-latexdiff` 对比 base branch 和 PR head，生成 `manuscript-diff.pdf`。

这两个 PDF 会作为 workflow artifact 上传。
`main.pdf` 用于阅读当前完整稿。
`manuscript-diff.pdf` 用于给非 Git 用户或导师查看带修订痕迹的版本。

`git-latexdiff` PDF 是沟通材料，不是新的事实来源。
正文仍以 TeX 源文件和 PR diff 为准。

## 本地命令

编译当前手稿：

```bash
make manuscript
```

检查一句一行：

```bash
make check-tex-style
```

生成本地修订痕迹 PDF：

```bash
make manuscript-diff
```

默认情况下，`make manuscript-diff` 会用当前分支的上游分支作为 base。
如果没有上游分支，会回退到 `origin/master`。
需要手动指定时：

```bash
BASE_REF=origin/master HEAD_REF=HEAD make manuscript-diff
```
