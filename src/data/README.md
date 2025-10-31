# 数据文件目录

这个目录用于存放项目相关的数据文件。

## 目录结构建议

```
src/data/
├── raw/           # 原始数据文件（不修改）
├── processed/     # 处理后的数据文件
├── external/      # 外部数据源文件
├── interim/       # 中间处理结果
└── final/         # 最终数据集
```

## 文件组织建议

### raw/
- 存放从外部获取的原始数据
- 这些文件不应该被修改
- 例如：`raw/dataset.csv`, `raw/api_data.json`

### processed/
- 存放经过清洗和处理的数据
- 这些文件是分析的主要数据源
- 例如：`processed/clean_data.csv`, `processed/feature_engineered_data.parquet`

### external/
- 存放从外部API或数据库获取的数据
- 例如：`external/weather_data.csv`, `external/stock_prices.csv`

### interim/
- 存放中间处理结果
- 用于调试和验证处理步骤
- 例如：`interim/step1_output.csv`, `interim/step2_output.csv`

### final/
- 存放最终的数据集
- 用于报告和展示
- 例如：`final/final_dataset.csv`, `final/summary_statistics.csv`

## 数据文件命名规范

- 使用小写字母和下划线
- 包含日期或版本信息
- 例如：`sales_data_2024_01_15.csv`, `user_behavior_v2.parquet`

## 注意事项

- 大型数据文件应该添加到 `.gitignore` 中
- 考虑使用数据版本控制工具（如DVC）来管理大型数据集
- 敏感数据不应该提交到版本控制中
- 在 `.env` 文件中配置数据路径
