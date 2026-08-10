# Titanic 原始竞赛数据

## 来源与许可

- Kaggle competition slug：`titanic`。
- 使用前必须登录 Kaggle，并先在 competition 页面接受规则。
- 数据许可与可用范围以用户接受的 competition rules 为准。

## 预期文件

| 文件 | 角色 | 大小（字节） | SHA-256 | 状态 |
|---|---|---:|---|---|
| `train.csv` | 含 `Survived` 标签的主要分析数据 | 待下载 | 待下载 | 尚未获取 |
| `test.csv` | 无标签结构兼容性数据，不用于主要分析或交叉验证 | 待下载 | 待下载 | 尚未获取 |

## 获取方式

认证可使用 `kaggle auth login`、`KAGGLE_API_TOKEN`、`~/.kaggle/access_token` 或 legacy `~/.kaggle/kaggle.json`。
不要把 token 写进本文件或任何 Git 记录。

计划命令：

```bash
kaggle competitions files titanic
kaggle competitions download titanic -f train.csv -p data/raw/titanic
kaggle competitions download titanic -f test.csv -p data/raw/titanic
```

实际研究入口将由 `src/001-download_titanic_data.sh` 提供，并在文件已存在时拒绝无条件覆盖。

## 版本控制

`train.csv`、`test.csv`、下载压缩包及其他竞赛原始文件不得提交。
获取后使用 `git check-ignore` 与 `git ls-files` 双重验证。
