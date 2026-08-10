# TeX 手稿工作流

## 默认约定

- 主文件：`docs/writing/manuscript/main.tex`。
- 模板：CTAN `elsarticle`，Harvard author-year 样式。
- 默认只维护一个主 TeX 文件，不在模板阶段拆章节。
- 正文一行一句，段落之间空一行。
- 参考文献只登记已核实来源，不保留虚构占位文献。

Titanic 汇报阶段如何直接引用中央正式输出，见 `docs/examples/titanic-walkthrough.md`。

## 中央输出

手稿通过相对路径直接引用 `outputs/figures/` 和 `outputs/tables/`。
手稿目录不维护第二份正式图表。
投稿打包时，`scripts/prepare-elsevier-submission.sh` 才把使用中的中央输出复制到独立 bundle 并调整路径。

## 常用命令

```bash
make init-tex
make check-tex-style
make manuscript
make manuscript-diff
make prepare-elsevier-submission
```

`build/` 和 `submission/` 都是生成目录，不提交。
编译完成后检查 PDF 非空；投稿 bundle 还需人工核对期刊要求、文件清单和许可。

## GitHub 自动化

涉及 TeX 源、中央正式图表、workflow 或 diff 脚本的 PR 会触发手稿检查与 diff PDF 构建。
GitHub Release 会编译并附加 `main.pdf`。
自动构建成功不替代对统计结果、引用、许可和投稿格式的人工审查。
