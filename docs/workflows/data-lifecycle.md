# 数据生命周期

## 数据分层

- `data/raw/`：原始文件或远程系统提取的固定快照，只读且不覆盖。
- `data/interim/`：能够从已记录输入重建的中间数据。
- `data/processed/`：能够直接进入统计分析、模型或正式输出的数据。
- `data/external/`：外部固定资料或第三方交付数据。

每个来源在 `docs/data-sources.md` 登记系统标识、资源、访问方式、版本或提取日期、本地落点和负责源码。
相应数据子目录 README 记录许可、文件清单、大小和校验值。

## 转换规则

1. 数据获取脚本只写入约定落点，不无条件覆盖已有原始文件。
2. 每个非显然转换记录输入、输出、运行命令和关键参数。
3. 分析和实验引用固定版本或可验证快照。
4. 中间和处理后数据默认不提交，但必须可以由源码重建。
5. 小型人工映射、来源元数据和正式汇总是否提交，根据角色、敏感性和可复现价值判断。

## BigQuery

BigQuery 使用外部 `gcloud`/`bq` 登录状态，不在仓库提供 SDK 包装器。
查询前先加载未跟踪的环境配置，并执行 dry run：

```bash
set -a
source .env
set +a

bq \
  --project_id="$BQ_PROJECT_ID" \
  --location="$BQ_LOCATION" \
  query \
  --use_legacy_sql=false \
  --dry_run \
  < src/001-example_query.sql
```

真实执行必须设置成本保护：

```bash
bq \
  --project_id="$BQ_PROJECT_ID" \
  --location="$BQ_LOCATION" \
  query \
  --use_legacy_sql=false \
  --maximum_bytes_billed="$BQ_MAXIMUM_BYTES_BILLED" \
  < src/001-example_query.sql
```

`src/001-example_query.sql` 只是路径格式示例，模板不创建该文件。
实际项目记录 project、location、dataset、table、提取时间和查询脚本。

## MSSQL / SQL Server

`.env` 中使用 `MSSQL_HOST`、`MSSQL_PORT`、`MSSQL_DATABASE`、`MSSQL_USERNAME`、`MSSQL_PASSWORD`、`MSSQL_DRIVER`、`MSSQL_ENCRYPT`、`MSSQL_TRUST_SERVER_CERTIFICATE` 和 `MSSQL_CONNECTION_TIMEOUT`。
`MSSQL_HOST` 可以是局域网 IP 或主机名。
默认 `Encrypt=yes`、`TrustServerCertificate=no`；使用自签名证书且用户明确接受证书验证风险时，才改变信任设置。
文档记录 database、schema、table 和提取时间，不记录连接密码。

## Kaggle

使用数据前先接受适用的数据集许可或竞赛规则。
认证优先使用 `kaggle auth login`、`KAGGLE_API_TOKEN`、`~/.kaggle/access_token` 或 legacy `~/.kaggle/kaggle.json`。
不要求用户把 token 粘贴进项目文档、日志或提交记录。
下载脚本检查命令、目标路径、已有文件、结果大小和 SHA-256，并用 `.gitignore` 与 `git check-ignore` 验证原始数据不会被跟踪。

## 安全检查

- 执行查询或下载前确认目标系统、成本、许可和覆盖行为。
- 命令输出不得包含 token、密码或完整连接字符串。
- 用 `git status --short` 和 `git ls-files` 确认原始数据及凭据未进入版本控制。
- 来源或校验值变化时更新 `docs/data-sources.md` 与数据子目录 README。
