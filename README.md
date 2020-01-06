# Program Notes

## 1. Contents

- [Program Notes](#program-notes)
  - [1. Contents](#1-contents)
  - [2. Python Notes](#2-python-notes)
    - [2.1.1. Self-define colormap](#211-self-define-colormap)
    - [2.2.1. Clip data with shp, and save it to npz](#221-clip-data-with-shp-and-save-it-to-npz)
  - [3. Shell notes](#3-shell-notes)
    - [3.1. create list with fixed digits](#31-create-list-with-fixed-digits)

## 2. Python Notes

### 2.1.1. Self-define colormap

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

### 2.2.1. Clip data with shp, and save it to npz

```python
# -*- coding: utf-8 -*-
"""
@author: Ghost
"""
import geopandas as gpd
import netCDF4 as nc
import numpy as np
import sys

from datetime import datetime, timedelta


def get_clip_data(boundary, variables):
    """
    Get clip area data(limit by boundary) from variables.
    Args:
        boundary: (minlon, minlat, maxlon, maxlat),
            tyepes:(float, float, float, float);
            clip boundary of data.
        variables: list of np.array, [lon, lat, var1, var2, ...].
    Return:
        variables_cut: list of np.array. [lon_cut, lat_cut, var1_cut, ...]
    """
    lon, lat, *_ = variables
    minlon, minlat, maxlon, maxlat = boundary
    lonmin = minlon // 1 - 1
    lonmax = maxlon // 1 + 1
    latmin = minlat // 1 - 1
    latmax = maxlat // 1 + 1
    limit = np.where((lon > lonmin) &
                     (lon < lonmax) &
                     (lat > latmin) &
                     (lat < latmax))
    len0 = len(set(limit[0]))
    len1 = len(set(limit[1]))
    print(len0, len1)
    variables_cut = [var[limit].reshape(len0, len1) for var in variables]
    return variables_cut


def get_boundary_from_shp(shp_path):
    """Get (minlon, minlat, maxlon, maxlat) from shp_file.

    Parameters:
        shp_path.
    Return:
        tuple: (minlon, minlat, maxlon, maxlat)
    """
    shp_file = '{}.shp'.format(shp_path)
    _df = gpd.GeoDataFrame.from_file(shp_file)
    bounds = _df.bounds
    minlon = bounds.minx.min()
    minlat = bounds.miny.min()
    maxlon = bounds.maxx.max()
    maxlat = bounds.maxy.max()
    return minlon, minlat, maxlon, maxlat


def main(time):
    '''
    Extract met variables, turn them to npy, pkl and csv.

    Args:
        time: datetime object.

    Return:
        No return, files will be saved.
    '''
    # 0 Generate input and output path
    time_str = time.strftime('%Y%m%d%H')
    nc_dir = '/path/of/ncfile_dir'
    nc_path = f'{nc_dir}/{time_str}.nc'
    out_dir = '/path/of/outdir'
    out_path = f'{out_dir}/{time_str}.npy'
    shp_path = './shp/china'
    # 1 Get data
    nc_data = nc.Dataset(nc_path)
    var_names = ['longitude', 'latitude',
                 'UGRD_10maboveground', 'VGRD_10maboveground']
    # you can also add other names.
    var_units = ['°', '°',
                 'm/s', 'm/s',]
    # Corresponding  units.
    variables_ori = [nc_data.variables[var_name][:] for var_name in var_names]
    lon, lat, *met_vars = variables_ori
    lont, latt = np.meshgrid(lon, lat)
    variables = [lont, latt]
    for _ in met_vars:
        variables.append(_[0])
    # clip data.
    boundary = get_boundary_from_shp(shp_path)
    variables_cut = get_clip_data(boundary, variables)
    # lon_cut, lat_cut, *met_vars_cut = variables_cut
    np.savez(out_path,
             data=variables_cut,
             var_names=var_names,
             var_units=var_units
             )


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            print("No args received, current time will be used.")
            time = datetime.now()
            main(time)
        elif len(sys.argv) != 3:
            print("Timestr and num needed, format '%Y%m%d%H' and 'int'.")
        else:
            print(len(sys.argv))
            time = datetime.strptime(sys.argv[1], '%Y%m%d%H')
            num = int(sys.argv[2])
            for i in range(num):
                main(time)
                time += timedelta(hours=+1)
    except (IOError, KeyboardInterrupt):
        raise
```

## 3. Shell notes

### 3.1. create list with fixed digits

```shell
#!/bin/bash

for i in `seq 0 1 24`
do
    echo `printf "%03d" "$i"`
done
```
