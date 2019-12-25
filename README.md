# 1. Python Notes

## 1.1. Contents

- [1. Python Notes](#1-python-notes)
  - [1.1. Contents](#11-contents)
  - [1.2. Matplotlib](#12-matplotlib)
    - [1.2.1. Self-define colormap](#121-self-define-colormap)
  - [1.3. Others](#13-others)
  - [1.4. Others](#14-others)

## 1.2. Matplotlib

### 1.2.1. Self-define colormap

有时候，你需要自定义colormap，自定义代码如下：  

```python
# -*- coding: utf-8 -*-
"""
@author: Ghost
"""
import matplotlib.colors as col
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
from matplotlib.ticker import MaxNLocator


norm = col.Normalize(0, 1)
colors_ = [[norm(0), "#FFFFFF"],  # 白色
           [norm(0.02), "#E0FFFF"],  # 淡青色
           [norm(0.04), "#98FB98"],  # 弱绿色
           [norm(0.08), "#008000"],  # 纯绿色
           [norm(0.12), "#00FF00"],  # 闪光绿
           [norm(0.16), "#00BFFF"],  # 深天蓝
           [norm(0.2), "#000080"],  # 海军蓝
           [norm(0.4), "#FF1493"],  # 深粉红
           [norm(1), "#FF8C00"]]  # 深橙色

# 创建名称为“rain_fall”的colormap
_cmap = col.LinearSegmentedColormap.from_list("rain_fall", colors_)
_cmap.set_over('#8B0000')  # 深红色
_cmap.set_under("#FFFFFF")  # 白色
# 注册“rain_fall”到matplotlib.cm，然后绘图就可以指定cmap=“rain_fall”
cm.register_cmap(cmap=_cmap)

#levels = MaxNLocator(nbins=50).tick_values(0, 50)
```

## 1.3. Others


## 1.4. Others