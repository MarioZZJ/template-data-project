# 脚本

`scripts/` 存放集成化项目脚本。

合适的脚本通常用于：

- 初始化或检查项目环境。
- 运行一段完整研究流程。
- 按固定顺序调用多个 `src/` 模块。
- 准备手稿或提交产物。

没有真实项目上下文前，不要添加一次性 harness 脚本。

现有手稿脚本：

- `build-manuscript-diff.sh`：用 `git-latexdiff` 生成修订痕迹 PDF；直接调用时传入输出 PDF 路径，并设置 `BASE_SHA` 和 `HEAD_SHA`。
