# Jupyter笔记本目录

这个目录用于存放Jupyter笔记本文件，用于数据探索、分析和可视化。

## 笔记本命名规范

建议使用以下命名规范：

```
[编号]_[主题]_[描述].ipynb
```

例如：
- `01_data_exploration.ipynb`
- `02_data_cleaning.ipynb`
- `03_feature_engineering.ipynb`
- `04_statistical_analysis.ipynb`
- `05_machine_learning.ipynb`
- `06_visualization.ipynb`

## 推荐的笔记本结构

### 1. 数据探索笔记本
- 数据概览
- 缺失值分析
- 数据分布分析
- 相关性分析

### 2. 数据清洗笔记本
- 数据类型转换
- 缺失值处理
- 异常值处理
- 重复值处理

### 3. 特征工程笔记本
- 特征创建
- 特征选择
- 特征转换
- 特征缩放

### 4. 统计分析笔记本
- 描述性统计
- 假设检验
- 相关性分析
- 回归分析

### 5. 机器学习笔记本
- 模型训练
- 模型评估
- 超参数调优
- 模型比较

### 6. 可视化笔记本
- 数据可视化
- 结果展示
- 交互式图表
- 报告生成

## 笔记本最佳实践

1. **导入库**
   ```python
   import pandas as pd
   import numpy as np
   import matplotlib.pyplot as plt
   import seaborn as sns
   ```

2. **设置路径**
   ```python
   import sys
   import os
   sys.path.append('../src')
   from utils.data_loader import load_data
   ```

3. **加载环境变量**
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   data_path = os.getenv('DATA_PATH')
   ```

4. **使用相对路径**
   ```python
   data_path = '../data/processed/clean_data.csv'
   ```

5. **保存结果**
   ```python
   # 保存处理后的数据
   processed_data.to_csv('../data/processed/step1_output.csv', index=False)
   
   # 保存图表
   plt.savefig('../outputs/figures/exploration_plot.png')
   ```

## 注意事项

- 笔记本文件应该保持清晰的结构
- 避免在笔记本中运行过长时间的代码
- 将可重用的函数移到 `src/utils/` 目录
- 定期清理笔记本输出，保持文件大小合理
- 使用版本控制时，注意 `.ipynb_checkpoints` 文件夹
