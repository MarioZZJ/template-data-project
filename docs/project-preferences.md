# 项目偏好

本文件记录会影响研究执行的环境、资源、审批和协作选择。
初始化时填写实际配置；未知项明确标为“待确认”。

<!-- PROJECT-INIT: 初始化时填写并删除本注释 -->

## 计算环境

| 项目 | 当前选择 | 备注 |
|---|---|---|
| Python | `uv`，版本待确认 | 使用 `uv sync` 和 `uv run` |
| SQL | 待确认 | 登记实际 BigQuery、MSSQL 或其他系统 |
| TeX | CTAN `elsarticle`，Harvard author-year | 主文件为 `docs/writing/manuscript/main.tex` |
| 远程计算 | 待确认 | 记录主机、调度器和资源边界，不记录凭据 |

## 数据访问与凭据

- 凭据只保存在未跟踪的 `.env`、用户凭据目录或外部密钥系统。
- BigQuery 使用外部 `gcloud`/`bq` 登录状态，先 dry run，再带最大计费字节限制执行。
- MSSQL 默认 `Encrypt=yes`、`TrustServerCertificate=no`；只有用户明确接受自签名证书风险时才改变。
- Kaggle 使用 OAuth、环境 token 或用户目录 token 文件；不把 token 粘贴到文档和日志。

## 运行与资源边界

- 研究步骤按根 README 逐项运行，不提供总控入口。
- 原始数据不覆盖；较重计算、付费查询或远程写入前确认资源与影响。
- 正式图表进入 `outputs/`，临时产物留在被忽略路径。

## Git 与论文协作

- 默认分支、功能分支和 PR 方式：待确认。
- 批注使用 Issue 加固定 commit permalink；实际正文改写使用小 PR 和 PR review。
- 不 force push，不提交凭据或大型原始数据。

## 需要事先确认的操作

- 待确认。
