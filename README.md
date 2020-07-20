# 1. Program Notes

## 1.1. Contents

- [1. Program Notes](#1-program-notes)
  - [1.1. Contents](#11-contents)
  - [1.2. Python Notes](#12-python-notes)
    - [1.2.1. Self-define colormap](#121-self-define-colormap)
    - [1.2.2. Clip data with shp, and save it to npz](#122-clip-data-with-shp-and-save-it-to-npz)
  - [1.3. Shell notes](#13-shell-notes)
    - [1.3.1. Create list with fixed digits](#131-create-list-with-fixed-digits)
    - [1.3.2. lrzsz install](#132-lrzsz-install)
    - [1.3.3. shebang usage in python](#133-shebang-usage-in-python)
    - [1.3.4. Built-in Exceptions](#134-built-in-exceptions)
  - [1.4. Meteorology](#14-meteorology)
    - [1.4.1. Turn grib2 to nc with wgrib2](#141-turn-grib2-to-nc-with-wgrib2)
    - [1.4.2. Cal frequencies of 16 wind directions](#142-cal-frequencies-of-16-wind-directions)
  - [1.5. DataBase](#15-database)
    - [1.5.1. Sqlite](#151-sqlite)
      - [1.5.1.1. Create table unique in multuple columns](#1511-create-table-unique-in-multuple-columns)

## 1.2. Python Notes

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

### 1.2.2. Clip data with shp, and save it to npz

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

## 1.3. Shell notes

### 1.3.1. Create list with fixed digits

```shell
#!/bin/bash

for i in `seq 0 1 24`
do
    echo `printf "%03d" "$i"`
done
```

### 1.3.2. lrzsz install

```shell
# If you don't have sudo permission, you cann't "yum -y install epel-release".
# epel include tools: screen, lrzsz, tree, locate, and htop.
# Then, this is what you need.

# 1 get the lrzsz.taz.gz file.
# from "http://freshmeat.sourceforge.net/projects/lrzsz/" or other sources.
tar -zxvf lrzsz-0.12.20.tar.gz
cd lrzsz-0.12.20
./configure --prefix=/your/path/lrzsz
make && make install

# 2 Don't forget to add lrzsz path to PATH.
vi ~/.bashrc
# add the following code to it.
export PATH="/your/path/lrzsz/bin":$PATH
alias rz="lrz"
alias sz="lsz"
```

### 1.3.3. shebang usage in python

"shebang" has two kinds of usages.  
First,  
`#!/usr/bin/python3`  # use this interpreter  
Second,  
`#!/usr/bin/env python3` # use the first found python3 interpreter  

### 1.3.4. Built-in Exceptions

```python
BaseException
 +-- SystemExit
 +-- KeyboardInterrupt
 +-- GeneratorExit
 +-- Exception
      +-- StopIteration
      +-- StopAsyncIteration
      +-- ArithmeticError
      |    +-- FloatingPointError
      |    +-- OverflowError
      |    +-- ZeroDivisionError
      +-- AssertionError
      +-- AttributeError
      +-- BufferError
      +-- EOFError
      +-- ImportError
      |    +-- ModuleNotFoundError
      +-- LookupError
      |    +-- IndexError
      |    +-- KeyError
      +-- MemoryError
      +-- NameError
      |    +-- UnboundLocalError
      +-- OSError
      |    +-- BlockingIOError
      |    +-- ChildProcessError
      |    +-- ConnectionError
      |    |    +-- BrokenPipeError
      |    |    +-- ConnectionAbortedError
      |    |    +-- ConnectionRefusedError
      |    |    +-- ConnectionResetError
      |    +-- FileExistsError
      |    +-- FileNotFoundError
      |    +-- InterruptedError
      |    +-- IsADirectoryError
      |    +-- NotADirectoryError
      |    +-- PermissionError
      |    +-- ProcessLookupError
      |    +-- TimeoutError
      +-- ReferenceError
      +-- RuntimeError
      |    +-- NotImplementedError
      |    +-- RecursionError
      +-- SyntaxError
      |    +-- IndentationError
      |         +-- TabError
      +-- SystemError
      +-- TypeError
      +-- ValueError
      |    +-- UnicodeError
      |         +-- UnicodeDecodeError
      |         +-- UnicodeEncodeError
      |         +-- UnicodeTranslateError
      +-- Warning
           +-- DeprecationWarning
           +-- PendingDeprecationWarning
           +-- RuntimeWarning
           +-- SyntaxWarning
           +-- UserWarning
           +-- FutureWarning
           +-- ImportWarning
           +-- UnicodeWarning
           +-- BytesWarning
           +-- ResourceWarning
```


## 1.4. Meteorology

### 1.4.1. Turn grib2 to nc with wgrib2

```shell
#!/bin/bash
# Assumed that wgrib2 had been installed.

# 1 Generate vars
vars="(:RH:2 m ab|:TMP:2 m ab|:APCP:surface:|:DSWRF:surface|:PRES:surface|:DLWRF:surface|:PEVPR:surface|:HPBL:surface|:UGRD:10 m above|:VGRD:10 m above|:TMP:850 mb|:HGT:850 mb|:UGRD:850 mb|:VGRD:850 mb|:TMP:500 mb|:HGT:500 mb|:RH:850 mb:|:VVEL:0.995 sigma level:)"

# 2 Extract vars and turn to nc
# input
gfs_dir="/gfs/dir"
gfs_name="gfs.t00z.pgrb2.0p25.f040"
# output
out_dir="/out/dir"
nc_name="2019010100"
wgrib2 ${gfs_dir}/${gfs_name}.grb -s | egrep "`echo $vars`" | wgrib2 -i ${gfs_dir}/${gfs_name}.grb -netcdf ${out_dir}/${nc_name}.nc
```

### 1.4.2. Cal frequencies of 16 wind directions

```python
import numpy as np


def cal_wd_freq(wd):
    """
    根据计算角度对风向数据进行16个风向风频统计

    Args:
        wd: np.array, wind angles.
    Return:
        wind_fs: list, frequencies of 16 directions.
    """
    # 1 求各风向个数
    wind_f = [0] * 16  # 初始化风向频率
    for value in wd:
        # 判断数据风向，处于哪个风向，哪个风向频数+1
        if ((value >= 0 and value < 11.25) or
                (value >= 348.75 and value < 360)):
            wind_f[0] += 1
        else:
            for m in range(15):
                if (value >= (m + 1) * 22.5 - 11.25 and
                        value < (m + 1) * 22.5 + 11.25):
                    wind_f[m + 1] += 1
    # 2 求风向频率
    if sum(wind_f) == 0:
        print("Sorry! Data was missed!")
    else:
        wind_fs = [value / sum(wind_f) for value in wind_f]
    return wind_fs
```

## 1.5. DataBase

### 1.5.1. Sqlite
#### 1.5.1.1. Create table unique in multuple columns
```shell
# Open sqlite database
$ .sqlite3 <filename.db>

# check tables
$ .table

# create table, unique in TIME and SITE
$ CREATE TABLE <table_name> (ID interger primary key autoincrement,
                             TIME date NOT NULL,
                             SITE text NOT NULL, VALUE real,
                             UNIQUE(TIME, SITE) ON CONFILICT REPLACE);

# headers on
$ .headers on


```
