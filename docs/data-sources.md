# Titanic 数据来源登记

| ID | 系统 | 资源/表 | 访问方式 | 版本或提取日期 | 本地落点 | 提取脚本 | 备注 |
|---|---|---|---|---|---|---|---|
| `TITANIC-TRAIN` | Kaggle competition | `titanic/train.csv` | Kaggle CLI；需先接受竞赛规则并认证 | 待下载 | `data/raw/titanic/train.csv` | `src/001-download_titanic_data.sh`（待建立） | 含 `Survived`，用于主要关联分析与交叉验证 |
| `TITANIC-TEST` | Kaggle competition | `titanic/test.csv` | Kaggle CLI；需先接受竞赛规则并认证 | 待下载 | `data/raw/titanic/test.csv` | `src/001-download_titanic_data.sh`（待建立） | 无 `Survived`，仅检查结构兼容性，不用于评价 |

## 访问与版本规则

- competition slug 固定为 `titanic`。
- 首次成功下载后，把 UTC 下载时间、文件大小和 SHA-256 写入本文件与 `data/raw/titanic/README.md`。
- 原始文件和下载压缩包由 `.gitignore` 排除，只有来源 README 被跟踪。
- 认证只来自外部登录状态、环境变量或用户目录 token 文件。
- 不向 Kaggle 提交预测文件。
