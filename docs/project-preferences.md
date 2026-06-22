# 项目偏好

这里记录环境、工具、运行方式和操作偏好。
这些内容会随项目演进，不要求初始化时一次性填完。

## 环境

| 项目 | 默认值 | 备注 |
|---|---|---|
| Python 管理 | `uv` | 依赖用 `uv add`，运行用 `uv run` |
| TeX 模板 | `elsarticle` Harvard author-year | 主文档是 `docs/writing/manuscript/main.tex` |
| 数据库 | TBD | schema 文档放在 `docs/agents/dbschema/` |

## 常用命令

```bash
make init
make init-tex
make check-tex-style
make manuscript
```

## 操作偏好

- 原始数据不覆盖。
- 大型生成数据默认不提交。
- 凭据只放 `.env` 或外部密钥系统。
- 运行较重实验前先确认资源和目标。
- 结果文件移动后同步更新 @DASHBOARD.md。
