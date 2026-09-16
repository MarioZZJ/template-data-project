# TeX 手稿工作流

## 手稿结构与研究依据

- 主文件为 `docs/writing/manuscript/main.tex`，参考文献为同目录 `references.bib`。
- 默认 CTAN `elsarticle`、Harvard author-year，先维护一个主文件，正文一行一句、段落间空行。正文显著增长且协作确有需要时再拆章节。
- 初始化时在项目偏好登记文稿阶段、语言、作者与投稿目标，不额外填写两份写作 README。
- 文献只登记已核实来源，结论以实验解释及选定图表为依据，不虚构参考文献、统计结果或许可。

## 正式图表与来源

手稿通过相对路径引用 `outputs/figures/` 和 `outputs/tables/`，不维护第二份正式图表。候选图表保存在外部运行目录，验收选择后使用 `export` 复制到仓库，并写 `outputs/provenance.json`。

论文编译只依赖 Git 中的手稿和选定图表，不能要求 CI 访问本机 `ResearchAssets`。来源索引用于追溯生成代码、输入版本、命令和参数；实验记录解释图表所支持的判断、限制及下游影响。

Titanic [汇报阶段](../examples/titanic-walkthrough.md#汇报阶段)仍可参考中央图表引用；其人工状态和仓库内数据规则属于旧历史。

## 本地工具与平台条件

```bash
make init-tex
make check-tex-style
make manuscript
make manuscript-diff
make prepare-elsevier-submission
```

这些工具使用 Bash、Make、TeX/latexmk，差异 PDF 还需要 git-latexdiff。Linux 或具备相关命令的 macOS 可按环境检查结果使用；Windows 需另外准备兼容运行环境。研究初始化和持久作业的三平台接口不代表现有论文 shell 工具都已原生跨平台。

`build/` 和 `submission/` 是手稿目录下的生成目录，不提交。构建后检查 PDF 非空；投稿打包由 `scripts/prepare-elsevier-submission.sh` 将实际使用的图表复制到独立 bundle 并调整路径，随后核对期刊文件清单、格式与许可。

## GitHub 自动化

涉及手稿 TeX、正式图表、来源索引、workflow 或相关论文工具的 PR 触发手稿检查及差异 PDF 构建。diff 使用 PR base 与 head；GitHub Release 发布时编译并附加阅读版 `main.pdf`。实际触发规则以 `.github/workflows/manuscript.yml` 为准。

自动构建成功不替代统计结果、引用与投稿内容的审查。首次接入或修改引用方式后，用干净检出验证论文编译；未在本机具备 TeX 的环境验证时明确说明，不把单纯风格检查报告成论文构建通过。

参见 [写作与图表](writing-and-figures.md)、[协作约定](collaboration.md)、[正式输出](../../outputs/README.md)。
