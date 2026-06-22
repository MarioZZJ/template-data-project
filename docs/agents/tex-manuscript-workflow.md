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
- `make check-tex-style`：检查明显的一行多句问题。
- `make prepare-elsevier-submission`：准备提交目录。

## 写作规则

- 正文一行一句。
- 段落之间空一行。
- 手稿图放在 `docs/writing/manuscript/figures/`。
- 手稿表放在 `docs/writing/manuscript/tables/`。
