# TeX 手稿流程

## 默认模板

- 使用 `docs/writing/manuscript/main.tex`。
- 使用 CTAN `elsarticle`。
- 默认采用 Harvard author-year 参考文献样式。
- 默认只维护一个主 TeX 文件。
- 模板阶段不拆分章节文件。

## 常用命令

- `make init-tex`：检查本机 TeX 工具链。
- `make manuscript`：编译手稿。
- `make manuscript-diff`：生成 base ref 到当前 head 的修订痕迹 PDF。
- `make check-tex-style`：检查明显的一行多句问题。
- `make prepare-elsevier-submission`：准备提交目录。

## 写作规则

- 正文一行一句。
- 段落之间空一行。
- 手稿图放在 `docs/writing/manuscript/figures/`。
- 手稿表放在 `docs/writing/manuscript/tables/`。

## GitHub 协作

- 批注用 Issue，并贴到正文具体行或行范围的 GitHub permalink。
- 实际改写正文用小 PR，并通过 PR review 审查。
- pull request 自动上传 `manuscript-diff.pdf`，并在 PR 中更新下载评论。
- GitHub Release 自动编译并附加 `main.pdf`。
- 详细规则见 @docs/agents/paper-collaboration-workflow.md。
