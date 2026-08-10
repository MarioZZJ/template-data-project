# 数据

## 本目录职责

`data/` 保存研究数据的本地分层位置：`raw/` 是不可覆盖的原始文件或远程系统固定快照，`interim/` 是可重建中间数据，`processed/` 是可直接分析的数据，`external/` 是外部固定资料或第三方交付数据。

## 初始化时需要判断

- 每个数据源的来源、许可、访问限制、版本和提取日期。
- 本地文件与远程系统表之间的落点和对应关系。
- 哪些小型元数据、人工映射、校验值或正式汇总文件应由 Git 跟踪。
- 数据是否包含敏感信息，以及共享、备份和删除边界。

## 推荐建立的项目文件

- `data/<layer>/<source>/README.md`：记录来源、文件清单、许可和校验值。
- `metadata.*` 或 `checksums.*`：记录可提交的来源元数据或校验信息。
- 只有真实数据进入时再建立来源子目录。

## 当前项目配置

本项目使用 Kaggle Titanic competition 的 `train.csv` 和 `test.csv`。
原始文件位于 `data/raw/titanic/`，可重建分析数据写入 `data/processed/titanic-analysis.csv`；`interim/` 保存数据质量、描述统计、模型和诊断汇总，`external/` 当前不使用。
原始 CSV、压缩包、中间数据和处理后数据不提交，来源 README 与校验信息由 Git 跟踪。

## 维护规则

- 不覆盖或原地修改 `raw/` 文件。
- 中间和处理后数据必须能够从已记录输入与源码重建。
- 数据来源、版本或提取方式变化时更新 `docs/data-sources.md`。
- 凭据不进入数据目录、文档、日志或 Git。

## 相关文档

- `AGENTS.md`
- `README.md`
- `DASHBOARD.md`
- `docs/data-sources.md`
- `docs/workflows/data-lifecycle.md`
