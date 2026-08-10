# Titanic 原始竞赛数据

## 来源与许可

- Kaggle competition slug：`titanic`。
- 使用前必须登录 Kaggle，并先在 competition 页面接受规则。
- 数据许可与可用范围以用户接受的 competition rules 为准。

## 预期文件

| 文件 | 角色 | 大小（字节） | SHA-256 | 状态 |
|---|---|---:|---|---|
| `train.csv` | 含 `Survived` 标签的主要分析数据 | 61,194 | `7d118fef8b6ccf7f81111877bc388536f7b1e498a655e3d649d19aaa010e9f6f` | 2026-08-10 获取并核验 |
| `test.csv` | 无标签结构兼容性数据，不用于主要分析或交叉验证 | 28,629 | `56023b9948236f3c7a1c9448fcf418b283e109ef177fa8c7e069158dd7dd52b2` | 2026-08-10 获取并核验 |

## 获取方式

认证可使用 `kaggle auth login`、`KAGGLE_API_TOKEN`、`~/.kaggle/access_token` 或 legacy `~/.kaggle/kaggle.json`。
不要把 token 写进本文件或任何 Git 记录。

计划命令：

```bash
kaggle competitions files titanic
kaggle competitions download titanic -f train.csv -p data/raw/titanic
kaggle competitions download titanic -f test.csv -p data/raw/titanic
```

实际研究入口是 `src/001-download_titanic_data.sh`，并在文件已存在时拒绝无条件覆盖。
本次使用 Kaggle CLI 2.2.4；当前透明代理会重置 `storage.googleapis.com`，因此脚本先执行官方 CLI，再通过同一官方 OAuth API 获取签名地址，并使用 `storage.cloud.google.com` 建立 TLS、保留 `Host: storage.googleapis.com` 完成字节相同的下载。
该回退只有显式设置 `KAGGLE_STORAGE_TLS_HOST=storage.cloud.google.com` 时启用，不记录 token 或签名地址。

获取时间：`2026-08-10T09:54:02Z`。

## 版本控制

`train.csv`、`test.csv`、下载压缩包及其他竞赛原始文件不得提交。
获取后使用 `git check-ignore` 与 `git ls-files` 双重验证。
