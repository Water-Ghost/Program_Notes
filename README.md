# 1. Program Notes

# 2. Contents

- [1. Program Notes](#1-program-notes)
- [2. Contents](#2-contents)
- [3. Python](#3-python)
  - [3.1. Self-define colormap](#31-self-define-colormap)
  - [3.2. Clip data with shp, and save it to npz](#32-clip-data-with-shp-and-save-it-to-npz)
  - [3.3. Get all files of a folder with os.walk](#33-get-all-files-of-a-folder-with-oswalk)
  - [3.4. Tests with pkgutils.get_data()](#34-tests-with-pkgutilsget_data)
    - [3.4.1. Package](#341-package)
    - [3.4.2. Codes](#342-codes)
    - [3.4.3. Output](#343-output)
    - [3.4.4. Discussions](#344-discussions)
  - [3.5. Get abs path of package](#35-get-abs-path-of-package)
    - [3.5.1. Dingding Robot with requests](#351-dingding-robot-with-requests)
- [4. Shell](#4-shell)
  - [4.1. Create list with fixed digits](#41-create-list-with-fixed-digits)
  - [4.2. lrzsz install](#42-lrzsz-install)
  - [4.3. shebang usage in python](#43-shebang-usage-in-python)
  - [4.4. Built-in Exceptions](#44-built-in-exceptions)
- [5. Meteorology](#5-meteorology)
  - [5.1. Turn grib2 to nc with wgrib2](#51-turn-grib2-to-nc-with-wgrib2)
  - [5.2. Cal frequencies of 16 wind directions](#52-cal-frequencies-of-16-wind-directions)
- [6. DataBase](#6-database)
  - [6.1. Sqlite](#61-sqlite)
    - [6.1.1. Create table unique in multuple columns](#611-create-table-unique-in-multuple-columns)
- [7. Docker](#7-docker)
  - [7.1. tldr docker](#71-tldr-docker)
  - [7.2. Common cmd](#72-common-cmd)
  - [7.3. Working with docker file](#73-working-with-docker-file)
- [8. Airflow](#8-airflow)
  - [8.1. CMD](#81-cmd)

# 3. Python

## 3.1. Self-define colormap

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

## 3.2. Clip data with shp, and save it to npz

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

## 3.3. Get all files of a folder with os.walk

```python
import os

def get_files_of_dir(folder):
    '''
    Get all files of specified folder.

    Parameters
    ----------
    folder : str.

    Returns
    -------
    file_list : list of str, list of filepath.
    '''
    file_list = []
    for root, _dir, files in os.walk(folder):
        for file in files:
            file_list.append(os.path.join(root, file))
    return file_list

folder = '/your/folder'
file_list = _files_of_dir(folder)
```

## 3.4. Tests with pkgutils.get_data()

根据官方文档、《python3标准库》、《python cookbook》和网上资料，测试发现均不能正确出结果，随自行测试`pkgutils.get_data`函数的使用方法。

### 3.4.1. Package

Package structures are as follows: 

```shell
pk
├── __init__.py
├── data
│   ├── __init__.py
│   ├── base.html
│   └── t1
│       └── test.csv
├── spam.py
├── test.py
├── test2.csv
└── test_.py
```

### 3.4.2. Codes

- spam.py

```python
import pandas as pd
import pkgutil
import io

def test1():
    # 正确返回结果
    print('-' * 20, 'Test 1', '-' * 20)
    base = pkgutil.get_data('data', 'base.html')
    print(base.decode('utf-8'))

def test2():
    # 正确返回结果
    print('-' * 20, 'Test 2', '-' * 20)
    csv = pkgutil.get_data('data', 't1/test.csv')
    print(csv.decode('utf-8'))
    print("\nRead data with pandas >>>")
    df = pd.read_csv(io.BytesIO(csv))
    print(df)

def test3():
    # 返回None
    print('-' * 20, 'Test 3', '-' * 20)
    csv = pkgutil.get_data('data.t1', 'test.csv')
    print(csv)

def test4():
    # 返回None
    print('-' * 20, 'Test 4', '-' * 20)
    csv2 = pkgutil.get_data('pk', 'test2.csv')
    print(csv2)  

def test5():
    # 正确返回结果
    print('-' * 20, 'Test 5', '-' * 20)
    csv3 = pkgutil.get_data('spam', 'test2.csv')
    print(csv3.decode('utf-8'))

def test6():
    # 正确返回结果
    print('-' * 20, 'Test 6', '-' * 20)
    csv4 = pkgutil.get_data('test', 'test2.csv')
    print(csv4.decode('utf-8'))

def test7():
    # 正确返回结果
    print('-' * 20, 'Test 7', '-' * 20)
    csv5 = pkgutil.get_data('test_', 'test2.csv')
    print(csv5.decode('utf-8'))

test1()
test2()
test3()
test4()
test5()
test6()
test7()

```

- test.py

```
print("This is test")

```

- test_.py (emtpy)

### 3.4.3. Output

```html
$ python spam.py 
-------------------- Test 1 --------------------
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    
</body>
</html>
-------------------- Test 2 --------------------
name, age
jack, 1444
kim, 20

Read data with pandas >>>
   name   age
0  jack  1444
1   kim    20
-------------------- Test 3 --------------------
None
-------------------- Test 4 --------------------
None
-------------------- Test 5 --------------------
-------------------- Test 1 --------------------
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    
</body>
</html>
-------------------- Test 2 --------------------
name, age
jack, 1444
kim, 20

Read data with pandas >>>
   name   age
0  jack  1444
1   kim    20
-------------------- Test 3 --------------------
None
-------------------- Test 4 --------------------
None
-------------------- Test 5 --------------------
key, value
name, jacks
age, 23
-------------------- Test 6 --------------------
This is test
key, value
name, jacks
age, 23
-------------------- Test 7 --------------------
key, value
name, jacks
age, 23
key, value
name, jacks
age, 23
-------------------- Test 6 --------------------
key, value
name, jacks
age, 23
-------------------- Test 7 --------------------
key, value
name, jacks
age, 23
```

### 3.4.4. Discussions

From the output, when run to `test5()`, the code restart run from `test1()` to `test7()`. And "This is test" should not be shown here, it was the result of `test.py`. Finally, the results of `test5()`, `test6()` and `test7()` was shown last.

Because, in `test5()` and `test6()`, when using `pkgutil.get_data()` they refered to `spam.py` and `test.py`. They are files not dirctory, and are not empty. 

The best solution is put your data to a sub dirctory, with a `__init__.py` in it. And we can see, the outer directory name, `pk`, is irrelevant.

## 3.5. Get abs path of package

```python
import os
import numpy as np

abs_dir = os.path.dirname(np.__file__)

```

### 3.5.1. Dingding Robot with requests

Auto sent message to Dingding Group, robot are secured with signature.

```python
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests
import json

# Generate timestamp and sign
timestamp = str(round(time.time() * 1000))
secret = 'Your secret key'
secret_enc = secret.encode('utf-8')
string_to_sign = '{}\n{}'.format(timestamp, secret)
string_to_sign_enc = string_to_sign.encode('utf-8')
hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

# Define headers
headers = {
    'Content-Type': 'application/json',
}
# Define parameters
params = (
    ('access_token', 'your token'),
    ('timestamp', f'{timestamp}'),
    ('sign', sign),
)
# Define msg and jsonify the msg
msg = "我就是我, 是不一样的烟火123"
data = {"msgtype": "text", "text": {'content': msg}}
data = json.dumps(data)

# Send msg
response = requests.post('https://oapi.dingtalk.com/robot/send', 
                         headers=headers, 
                         params=params,
                         data=data)
print(response.text)
```



# 4. Shell

## 4.1. Create list with fixed digits

```shell
#!/bin/bash

for i in `seq 0 1 24`
do
    echo `printf "%03d" "$i"`
done
```

## 4.2. lrzsz install

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

## 4.3. shebang usage in python

"shebang" has two kinds of usages.  
First,  
`#!/usr/bin/python3`  # use this interpreter  
Second,  
`#!/usr/bin/env python3` # use the first found python3 interpreter  

## 4.4. Built-in Exceptions

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


# 5. Meteorology

## 5.1. Turn grib2 to nc with wgrib2

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

## 5.2. Cal frequencies of 16 wind directions

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

# 6. DataBase

## 6.1. Sqlite
### 6.1.1. Create table unique in multuple columns
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

# 7. Docker

## 7.1. tldr docker

- List currently running docker containers:
    - `docker ps`

- List all docker containers (running and stopped):
    - `docker ps -a`

- Start a container from an image, with a custom name:
    - `docker run --name container_name image`

- Start or stop an existing container:
    - `docker start|stop container_name`

- Pull an image from a docker registry:
    - `docker pull image`

- Open a shell inside of an already running container:
    - `docker exec -it container_name sh`

- Remove a stopped container:
    - `docker rm container_name`

- Fetch and follow the logs of a container:
    - `docker logs -f container_name`


## 7.2. Common cmd

```shell
# Create a container
$ docker run -i -t ubuntu /bin/bash
# -i 保证容器的STDIN是开启的，-t 告诉Docker为容器分配一个伪tty终端

# Name a container
$ docker run --name container_name -i -t ubuntu /bin/bash

# update and install vim
$ apt-get update && apt-get install vim

# Restart a stoped container
$ docker start container_name/id

# Delete a container
$ docker rm --force contain_name/id

# Delete a contianer and its volume
$ docker rm -v contain_name

# Attach to a container
$ docker attach container_name/id

# Create a daemonized container
$ docker run --name daemon_dave -d ubuntu /bin/sh -c "while true; do echo hello world; sleep 1; done"
# -d Docker会将容器放到后台运行

# Check the log
$ docker logs daemon_dave
$ docker logs -f daemon_dave  # 跟踪日志
$ docker logs -ft daemon_dave  # 跟踪日志，并添加时间戳

# Statistics
$ docker top daemon_dave
$ docker stats daemon_dave <others> ...

# Execute tasks
$ docker exec -d daemon_dave touch /etc/new_config_file
# -d 表明需要运行一个后台进程

# Execute a interactive cmd in a container
$ docker exec -i -t daemon_dave /bin/bash

# Stop a daemonized container
$ docker stop daemon_dave/id

# Check the last x container
$ docker ps -n x

# Create a auto start container
$ docker run --restart=always --name daemon_dave -d ubuntu /bin/sh -c "while true; do echo hello world; sleep 1; done"

# Inspect 
$ docker inspect daemon_dave

# List the images
$ docker images

# Pull a image
$ docker pull ubuntu:14.04

# Create a container with a tag
$ docker run -t -i --name new_container ubuntu:14:04 /bin/bash

# Delete images, you can delete it if only the correspond container not exists.
$ docker rmi container_name/id

# Search images
$ docker search puppet

# Pull a image
$ docker pull ansible/centos7-ansible

# Create a container
$ docker run -i -t ansible/centos7-ansible /bin/bash

# Create a container with nginx
$ docker run -d --name web container_nginx nginx -g "daemon off;"
# container_nginx 是带有nginx的容器

```


## 7.3. Working with docker file

* Dockerfile

```docker
# Version: 0.0.1
FROM ubuntu:14.04
LABEL maintainer="zyz" mail='test@test.com'
VOLUME [ "/data" ]
RUN mkdir /work
WORKDIR /work
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && apt-get install -y wget

# Download miniconda.sh and install
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    -O /work/miniconda.sh
RUN /bin/bash /work/miniconda.sh -b -p /work/miniconda && rm /work/miniconda.sh
RUN echo "export PATH=/work/miniconda/bin:$PATH" >> ~/.bashrc
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```

# 8. Airflow

## 8.1. CMD

- Command Line Metadata Validation

```bash
# print the list of active DAGs
airflow list_dags

# prints the list of tasks the "tutorial" dag_id
airflow list_tasks tutorial

# prints the hierarchy of tasks in the tutorial DAG
airflow list_tasks tutorial --tree
```

- Testing

```python
# command layout: command subcommand dag_id task_id date

# testing print_date
airflow test tutorial print_date 2015-06-01

# testing sleep
airflow test tutorial sleep 2015-06-01
```

- Backfill

```python
# optional, start a web server in debug mode in the background
# airflow webserver --debug &

# start your backfill on a date range
airflow backfill tutorial -s 2015-06-01 -e 2015-06-07

```

