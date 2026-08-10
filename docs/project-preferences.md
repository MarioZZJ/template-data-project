# Titanic 项目偏好

## 计算环境

| 项目 | 当前选择 | 备注 |
|---|---|---|
| Python | Python 3.12，`uv 0.9.15` | 使用 `uv sync` 与 `uv run`，不作为 package 安装 |
| 数据获取 | 外部 Kaggle CLI | 版本与认证在首次下载时记录 |
| SQL | 不使用 | 本项目只使用官方 CSV |
| TeX | 用户级 TinyTeX 2026，CTAN `elsarticle` | 主文件为 `docs/writing/manuscript/main.tex` |
| 远程计算 | 不使用 | 本地 CPU 足以完成示例分析 |

## 数据访问与凭据

- 必须先在 Kaggle 页面接受 Titanic competition 规则。
- 认证使用 `kaggle auth login`、`KAGGLE_API_TOKEN`、`~/.kaggle/access_token` 或 legacy `~/.kaggle/kaggle.json`。
- token 不进入仓库文件、日志或命令输出。
- `train.csv`、`test.csv`、压缩包和其他竞赛原始文件不提交。

## 分析与复现

- 固定随机种子为 `20260810`。
- 按根 README 的编号命令逐项执行，不增加总控 harness。
- 原始文件不覆盖；需要重新下载时由用户显式传入覆盖选项。
- 处理后数据默认不提交，正式图表由 Git 跟踪。

## Git 与论文协作

- 示例分支为 `example/titanic`，从模板基点分出。
- 初始化、分析和过程汇报分别形成独立提交。
- 写作批注使用 Issue 与固定 permalink，正文改动使用小 PR review。

## 需要事先确认的操作

- 覆盖已有原始 Titanic 文件。
- 向 Kaggle 或任何外部系统上传文件；本项目不计划提交预测。
- 改变研究问题、主要模型式或年龄缺失处理策略。
