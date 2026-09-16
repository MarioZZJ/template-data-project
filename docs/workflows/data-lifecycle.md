# 数据生命周期

## 外部资产与固定输入

研究数据不放在 Git 工作树。默认资产根为 Linux/macOS 的 `~/ResearchAssets/<仓库名>/`，Windows 的 `%USERPROFILE%\ResearchAssets\<仓库名>\`。`setup` 根据 `origin` 建立映射，独立工作树共享映射；无远端时指定项目名。同名不同来源采用可读别名，仓库更名不自动移动资产，仅使用用户明确选择的其他磁盘替代默认位置。

- `inputs/<来源>/<版本>/`：原始提取、外部资料或已固定的分析输入，不原地修改或覆盖。
- `runs/<运行编号>/data/`：该次运行的样本构造与其他中间数据。
- `runs/<运行编号>/outputs/`：候选图表、诊断和结果摘要。
- `runs/<运行编号>/logs/`、`run.json`：执行证据；不能替代实验解释。
- `envs/`：稳定依赖环境；`deliveries/`：交付记录。

每次运行单独注入 `DATA_ROOT`、`RUN_DIR`、`OUTPUT_ROOT`；共享配置不保存某次运行目录。后续分析引用明确的输入版本或前次运行产物，不引用漂移的 `latest`，不把研究数据复制回工作树以解决路径问题。

数据大小、SHA-256、许可、提取日期及分析用途统一登记到 [数据来源](../data-sources.md)；大量文件可使用可提交的轻量清单并在登记中链接。跨机器共享和备份由项目另行约定，模板不自动同步资产。

## 获取与转换

1. 获取前核对目标系统、许可、已有文件和已授权资源范围；新固定版本使用新目录。
2. 非显然转换记录固定输入、实际命令、参数及输出。检查样本量、键、缺失和取值边界。
3. 从已登记输入和已提交源码生成中间及分析数据；实际命令与版本进入运行记录。
4. 中间数据、候选图和诊断不提交 Git；小型人工映射或来源元数据可按敏感性和复现用途保留，但不含访问密钥。
5. 选定论文图表才使用 `export`，保存来源索引并检查实验和正文引用。

## 环境与凭据

系统环境和资产根下的本机 `.env` 提供本机配置，模板 `.env.example` 只给必要示例。不要依赖主检出里被忽略的 `.env` 自动出现在工作树中。凭据不写入项目映射、命令参数、运行记录或日志；资产目录若另行共享，必须排除本机凭据。

### BigQuery

使用外部 `gcloud`/`bq` 登录状态。仅实际使用此来源时配置 `BQ_PROJECT_ID`、`BQ_LOCATION`、`BQ_MAXIMUM_BYTES_BILLED`。查询先 dry run，真实执行设置最大计费字节限制；这些操作在现有阶段授权内连续完成。

以下是 Bash 命令示意，实际 SQL 路径由项目提供；模板不创建假查询文件。

```bash
bq --project_id="$BQ_PROJECT_ID" --location="$BQ_LOCATION" query \
  --use_legacy_sql=false --dry_run < src/001-example_query.sql
bq --project_id="$BQ_PROJECT_ID" --location="$BQ_LOCATION" query \
  --use_legacy_sql=false --maximum_bytes_billed="$BQ_MAXIMUM_BYTES_BILLED" \
  < src/001-example_query.sql
```

运行记录保留查询版本、project、location、dataset、table、提取时间和实际资源用量；不要把 dry run 当成已完成取数。

### MSSQL / SQL Server

只在需要时启用 `setup --extra mssql`，并在操作系统安装匹配的 ODBC 驱动。本机配置键包括 `MSSQL_HOST`、`MSSQL_PORT`、`MSSQL_DATABASE`、`MSSQL_USERNAME`、`MSSQL_PASSWORD`、`MSSQL_DRIVER`、`MSSQL_ENCRYPT`、`MSSQL_TRUST_SERVER_CERTIFICATE` 和 `MSSQL_CONNECTION_TIMEOUT`。

默认 `Encrypt=yes`、`TrustServerCertificate=no`；只有已有明确决定才改变证书验证。来源登记记录 database、schema、table 及提取时间；可公开文档不暴露内部连接信息，更不保存密码。

### Kaggle 与其他下载

遵守适用的数据集许可和竞赛规则，使用受支持的用户认证方式或本机凭据。下载检查目标路径、已有文件、文件大小和校验值，不能把登录或请求受理视作完整下载。认证信息不写入项目文档、日志和提交。

## 交付检查

- 用 `git status --short` 和 `git ls-files` 确认研究数据与凭据未进入 Git。
- 数据版本、提取方法或校验值变化时更新来源登记；影响样本或口径时同时更新实验解释和相关计划决定。
- 文件存在不足以证明完整；按实际格式检查可读取性、记录数、文件尾和关键字段，并保留失败证据。
