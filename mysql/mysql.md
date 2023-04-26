# 1. Mysql

## 1.1. content

- [1. Mysql](#1-mysql)
  - [1.1. content](#11-content)
  - [1.2. start and shutdown](#12-start-and-shutdown)
  - [1.3. commands](#13-commands)
  - [1.4. partition](#14-partition)


## 1.2. start and shutdown

```shell
# start service
service mysqld start
# shutdown service
service mysqld shutdown

```

## 1.3. commands

```shell
# 1 连接数据库
## syntax
## mysql -h <host> -P <port> -u <user> -p<password>
mysql -h 172.0.0.1 -P 3307 -u user -ppassword

# 2 查看进程
show processlist;
```

## 1.4. partition

查看分区表数据量，替换`table_name`

```sql
USE information_schema;

SELECT PARTITION_NAME,TABLE_ROWS FROM INFORMATION_SCHEMA.PARTITIONS WHERE TABLE_NAME = 'table_name';
```

创建时间分区，替换`table_name`和`date_column`

```sql
ALTER TABLE
    table_name PARTITION BY RANGE (TO_DAYS(date_column)) (
        PARTITION p202301
        VALUES
            LESS THAN (TO_DAYS('20230201')),
            PARTITION p202302
        VALUES
            LESS THAN (TO_DAYS('20230301')),
            PARTITION p202303
        VALUES
            LESS THAN (TO_DAYS('20230401')),
            PARTITION p202304
        VALUES
            LESS THAN (TO_DAYS('20230501')),
            PARTITION p202305
        VALUES
            LESS THAN (TO_DAYS('20230601')),
            PARTITION p202306
        VALUES
            LESS THAN (TO_DAYS('20230701')),
            PARTITION p202307
        VALUES
            LESS THAN (TO_DAYS('20230801')),
            PARTITION p202308
        VALUES
            LESS THAN (TO_DAYS('20230901')),
            PARTITION p202309
        VALUES
            LESS THAN (TO_DAYS('20231001')),
            PARTITION p202310
        VALUES
            LESS THAN (TO_DAYS('20231101')),
            PARTITION p202311
        VALUES
            LESS THAN (TO_DAYS('20231201')),
            PARTITION p202312
        VALUES
            LESS THAN (TO_DAYS('20240101'))
    );
```

添加分区，替换`table_name`

```sql
ALTER TABLE
    t_r_ec_extension_city_forecast_sunriseset
ADD
    PARTITION (
        PARTITION p202401
        VALUES
            LESS THAN (TO_DAYS('20240201')),
            PARTITION p202402
        VALUES
            LESS THAN (TO_DAYS('20240301')),
            PARTITION p202403
        VALUES
            LESS THAN (TO_DAYS('20240401')),
            PARTITION p202404
        VALUES
            LESS THAN (TO_DAYS('20240501')),
            PARTITION p202405
        VALUES
            LESS THAN (TO_DAYS('20240601')),
            PARTITION p202406
        VALUES
            LESS THAN (TO_DAYS('20240701')),
            PARTITION p202407
        VALUES
            LESS THAN (TO_DAYS('20240801')),
            PARTITION p202408
        VALUES
            LESS THAN (TO_DAYS('20240901')),
            PARTITION p202409
        VALUES
            LESS THAN (TO_DAYS('20241001')),
            PARTITION p202410
        VALUES
            LESS THAN (TO_DAYS('20241101')),
            PARTITION p202411
        VALUES
            LESS THAN (TO_DAYS('20241201')),
            PARTITION p202412
        VALUES
            LESS THAN (TO_DAYS('20250101'))
    );
```
