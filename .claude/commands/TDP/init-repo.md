---
description: 交互式初始化项目仓库：收集项目信息、更新元数据文件、配置环境、可选设置 GitHub 远程仓库。
---

这是一个交互式项目初始化向导。按以下步骤执行：

## 步骤 1：收集项目信息

使用 AskUserQuestion 一次性收集所有必要信息（最多 4 个问题分组）：

**问题组 1：基本信息**
- 项目显示名称（示例：Citation Network Analysis）
- Python 包名（自动建议：小写+连字符，示例：citation-network-analysis）
- 项目描述（一句话）
- 版本号（默认 0.1.0）

**问题组 2：作者信息**
- 作者姓名
- 作者邮箱

**问题组 3：可选配置**
- 是否需要设置 GitHub 远程仓库？（需要已用 `gh auth login` 登录）
- 是否现在运行 `./scripts/setup_env.sh` 安装依赖（需要终端支持）？

## 步骤 2：更新元数据文件

根据收集到的信息，更新以下文件：

### pyproject.toml
将以下占位符替换为实际值：
- `name = "python-data-analysis-template"` → 用户的包名
- `version = "0.1.0"` → 用户的版本号
- `description = "Python数据分析项目模板"` → 用户的描述
- `{name = "Your Name", email = "your.email@example.com"}` → 用户的作者信息

### src/__init__.py
更新三个变量：
- `__version__`
- `__author__`
- `__email__`

### .env
如果 `.env` 不存在，先从 `.env.example` 复制：
```bash
cp .env.example .env
```
然后更新：
- `PROJECT_NAME` → 包名
- `PROJECT_VERSION` → 版本号

### README.md
在文件顶部将标题 `# Python数据分析项目模板` 替换为 `# {项目显示名称}`，并在标题下方添加描述。

## 步骤 3：环境初始化（按用户选择）

如果用户选择现在安装依赖，运行：
```bash
source .venv/bin/activate 2>/dev/null || true
uv venv 2>/dev/null || true
source .venv/bin/activate
uv add pandas numpy matplotlib seaborn jupyterlab ipykernel python-dotenv
uv add --group dev jupyter notebook
python -m ipykernel install --user --name="{包名}" --display-name="Python ({项目显示名称})"
```

如果用户选择跳过，告知命令：`./scripts/setup_env.sh`（会重新询问项目信息并覆盖，建议跳过重新询问的步骤）或手动运行上述命令。

## 步骤 4：GitHub 仓库设置（按用户选择）

如果用户选择设置 GitHub 仓库：

1. 检查是否已有 git 仓库：
   ```bash
   git status
   ```

2. 如果没有初始化，先 init：
   ```bash
   git init && git add . && git commit -m "初始化项目"
   ```

3. 用 gh 创建远程仓库并推送（询问用户：public 还是 private）：
   ```bash
   gh repo create {包名} --{public|private} --source=. --remote=origin --push
   ```

4. 告知用户仓库地址。

## 步骤 5：完成提示

输出初始化摘要：
- 列出更新了哪些文件
- 环境状态（已安装/待安装）
- GitHub 状态（已创建/跳过）
- 后续命令提示：
  ```
  source .venv/bin/activate   # 激活虚拟环境
  jupyter lab                 # 启动 Jupyter Lab
  /TDP:verify                 # 验证环境配置
  ```
