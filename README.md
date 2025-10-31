# Python数据分析项目模板

这是一个用于Python数据分析项目的模板文件夹，提供了基本的项目结构和配置文件。

## 项目结构

```
.
├── README.md                    # 项目说明文档
├── .gitignore                   # Git忽略文件配置
├── .vscode/                     # VSCode配置文件夹
│   ├── settings.json            # VSCode设置
│   └── extensions.json          # 推荐扩展
├── scripts/                     # 脚本文件夹
│   └── setup_env.sh             # 虚拟环境初始化脚本
├── src/                         # 源代码文件夹
│   ├── __init__.py              # Python包初始化
│   ├── data/                    # 数据文件夹
│   ├── notebooks/               # Jupyter笔记本
│   └── utils/                   # 工具函数
├── pyproject.toml              # 项目配置文件
└── .env.example                # 环境变量示例文件
```

## 快速开始

### 1. 初始化虚拟环境

```bash
# 运行初始化脚本
chmod +x scripts/setup_env.sh
./scripts/setup_env.sh
```

或者手动创建：

```bash
# 使用uv创建虚拟环境
uv venv

# 激活虚拟环境
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 安装基础依赖（可选）
uv add pandas numpy matplotlib seaborn jupyterlab ipykernel python-dotenv
```

### 2. 安装依赖

在 `pyproject.toml` 中配置您的项目依赖，然后运行：

```bash
# 安装生产依赖
uv add <package_name>

# 安装开发依赖
uv add --group dev <package_name>

# 查看依赖树
uv tree

# 移除依赖
uv remove <package_name>
```

### 3. 配置环境变量

仓库内提供 `.env.example` 模板，初始化脚本会在首次运行时自动复制为 `.env`。如果需要手动配置：

```bash
# 复制示例配置
cp .env.example .env

# 编辑 .env 文件，添加您的环境变量
# 例如：
# API_KEY=your_api_key_here
# DATABASE_URL=your_database_url
# DATA_PATH=./src/data
```

### 4. 开始开发

- 在 `src/notebooks/` 中创建Jupyter笔记本进行数据分析
- 在 `src/utils/` 中添加可重用的工具函数
- 在 `src/data/` 中存放数据文件

## 环境变量说明

`.env` 文件用于存储项目的环境变量配置，这些变量通常包含：

- **API密钥**：第三方服务的访问密钥
- **数据库连接字符串**：数据库的连接信息
- **文件路径**：数据文件、输出目录的路径配置
- **应用配置**：调试模式、日志级别等应用设置

### 使用方法

在Python代码中，可以使用 `python-dotenv` 库加载环境变量：

```python
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

# 使用环境变量
api_key = os.getenv('API_KEY')
data_path = os.getenv('DATA_PATH', './src/data')  # 提供默认值
```

### 注意事项

- `.env` 文件包含敏感信息，应该添加到 `.gitignore` 中
- 不要将包含真实密钥的 `.env` 文件提交到版本控制
- 在生产环境中，应该通过环境变量或配置管理服务来管理这些配置

## 推荐的VSCode扩展

项目已配置推荐扩展，包括：
- Python
- Jupyter
- Pylance
- autopep8
- GitLens

## Git使用

项目已配置 `.gitignore` 文件，可以直接初始化Git仓库：

```bash
git init
git add .
git commit -m "Initial commit"
```

## 注意事项

- 请根据实际项目需求修改 `pyproject.toml` 中的配置
- 环境变量请在 `.env` 文件中配置
- 数据文件请放在 `src/data/` 目录中
