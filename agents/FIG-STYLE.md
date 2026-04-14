# 图表样式规范

学术科研数据分析项目的 matplotlib/seaborn 图表样式偏好。

## 图形尺寸

| 用途 | figsize |
|------|---------|
| 单列图（正文嵌入） | `(6, 4)` |
| 双列宽图 | `(12, 4)` |
| 正方形图 | `(5, 5)` |
| 多子图（2行×3列） | `(14, 8)` |

## 分辨率与导出

- 屏幕预览：`dpi=100`
- 保存输出：`dpi=300`
- 保存格式：优先 `.pdf`（矢量），需嵌入时用 `.png`
- 保存路径：`outputs/figures/`
- `bbox_inches='tight'`，`pad_inches=0.05`

## 配色方案

- **首选调色板**：NPG（Nature Publishing Group）风格配色，适合学术图表
- **备选调色板**：`seaborn.color_palette("colorblind")`（色盲友好，色种不够时使用）
- **连续色图**：`viridis`（顺序），`RdBu_r`（发散）
- **分类色图**：最多 8 种颜色；超过 8 组时改用线型区分

### NPG 配色

来自 Nature Publishing Group 期刊的标准配色，共 10 色：

```python
NPG_COLORS = [
    "#E64B35", "#4DBBD5", "#00A087", "#3C5488", "#F39B7F",
    "#8491B4", "#91D1C2", "#DC0000", "#7E6148", "#B09C85",
]
```

也可通过 `pypalettes` 包直接获取：

```python
from pypalettes import load_cmap
cmap = load_cmap("npg")               # 连续色图
palette = cmap.colors[:n]             # 取前 n 种颜色
```

## 字体

- **字体族**：`sans-serif`（优先 `Helvetica Neue` 或 `Arial`）
- **标题**：`fontsize=14`, `fontweight='bold'`
- **坐标轴标签**：`fontsize=12`
- **刻度标签**：`fontsize=10`
- **图例文字**：`fontsize=10`
- **标注文字**：`fontsize=9`

## 坐标轴与网格

- 隐藏上边框和右边框（`ax.spines[['top','right']].set_visible(False)`）
- 主网格：`linestyle='--'`, `alpha=0.4`, `color='gray'`，仅显示 y 轴网格
- 不显示次网格

## 图例

- 默认位置：`loc='best'`
- 边框：去掉（`frameon=False`）或保留细边框（`framealpha=0.8`）
- 列数：多条目时 `ncol=2`

## 快速初始化代码

```python
import matplotlib.pyplot as plt
import seaborn as sns

def apply_fig_style():
    sns.set_theme(style="ticks", palette="colorblind")
    plt.rcParams.update({
        "figure.dpi": 100,
        "savefig.dpi": 300,
        "font.family": "sans-serif",
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "axes.labelsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "legend.fontsize": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.linestyle": "--",
        "grid.alpha": 0.4,
    })
```
