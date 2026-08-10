# Titanic 数据来源登记

| ID | 系统 | 资源/表 | 访问方式 | 版本或提取日期 | 本地落点 | 提取脚本 | 备注 |
|---|---|---|---|---|---|---|---|
| `TITANIC-TRAIN` | Kaggle competition | `titanic/train.csv` | Kaggle CLI 2.2.4 + OAuth；受限网络使用官方签名地址的 TLS 主机回退 | 上游创建 2019-12-11；提取 2026-08-10T09:54:02Z | `data/raw/titanic/train.csv` | `src/001-download_titanic_data.sh` | 61,194 字节；SHA-256 `7d118f…010e9f6f`；含标签，用于主要分析与交叉验证 |
| `TITANIC-TEST` | Kaggle competition | `titanic/test.csv` | Kaggle CLI 2.2.4 + OAuth；受限网络使用官方签名地址的 TLS 主机回退 | 上游创建 2019-12-11；提取 2026-08-10T09:54:02Z | `data/raw/titanic/test.csv` | `src/001-download_titanic_data.sh` | 28,629 字节；SHA-256 `56023b…dd7dd52b2`；无标签，仅检查结构兼容性 |

## 访问与版本规则

- competition slug 固定为 `titanic`。
- UTC 下载时间、文件大小和 SHA-256 同步记录在本文件与 `data/raw/titanic/README.md`。
- 原始文件和下载压缩包由 `.gitignore` 排除，只有来源 README 被跟踪。
- 认证只来自外部登录状态、环境变量或用户目录 token 文件。
- 不向 Kaggle 提交预测文件。
