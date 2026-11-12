# Протокол PostgreSQL
Две новые отдельные БД временного кластера; исходная БД не подключалась.

## task_tracker_study_first: schema.sql
```text
BEGIN
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE INDEX
COMMENT
COMMENT
COMMENT
COMMIT

```
## task_tracker_study_first: seed.sql
```text
BEGIN
INSERT 0 6
 setval 
--------
      6
(1 row)

INSERT 0 4
 setval 
--------
      4
(1 row)

INSERT 0 16
 setval 
--------
     16
(1 row)

INSERT 0 60
 setval 
--------
     60
(1 row)

COMMIT

```
## task_tracker_study_first: checks.sql
```text
BEGIN
DO
 invalid_project_column_count 
------------------------------
                            0
(1 row)

ROLLBACK
psql:/Users/shibaboy/Desktop/файлы/MISIS/4 Year/task-tracker-db/sql/checks.sql:42: NOTICE:  PASS: tasks_assignee_fk (SQLSTATE 23503)
psql:/Users/shibaboy/Desktop/файлы/MISIS/4 Year/task-tracker-db/sql/checks.sql:42: NOTICE:  PASS: tasks_project_column_fk (SQLSTATE 23503)
psql:/Users/shibaboy/Desktop/файлы/MISIS/4 Year/task-tracker-db/sql/checks.sql:42: NOTICE:  PASS: tasks_priority_check (SQLSTATE 23514)
psql:/Users/shibaboy/Desktop/файлы/MISIS/4 Year/task-tracker-db/sql/checks.sql:42: NOTICE:  PASS: tasks_project_number_unique (SQLSTATE 23505)

```
## task_tracker_study_first: queries.sql
```text
 project_id |     project_name      | task_count 
------------+-----------------------+------------
          1 | Учебный каталог       |         20
          2 | Планирование семестра |         20
          3 | Архив материалов      |         20
          4 | Пустой проект         |          0
(4 rows)

 position |    stage     | task_count 
----------+--------------+------------
        0 | К выполнению |         15
        1 | В работе     |         15
        2 | Проверка     |         15
        3 | Завершено    |         15
(4 rows)

 assignee_id |  username  | active_count 
-------------+------------+--------------
           1 | Участник 1 |            7
           2 | Участник 2 |            8
           3 | Участник 3 |            8
           4 | Участник 4 |            8
           5 | Участник 5 |            8
           6 | Участник 6 |            0
(6 rows)

 id | project_id | task_number |        title        | assignee_id |  due_date  | overdue_days 
----+------------+-------------+---------------------+-------------+------------+--------------
 17 |          1 |          17 | Учебная задача 1-17 |           2 | 2026-11-04 |            8
 51 |          3 |          11 | Учебная задача 3-11 |           1 | 2026-11-04 |            8
  1 |          1 |           1 | Учебная задача 1-1  |           1 | 2026-11-05 |            7
 18 |          1 |          18 | Учебная задача 1-18 |           3 | 2026-11-05 |            7
 52 |          3 |          12 | Учебная задача 3-12 |           2 | 2026-11-05 |            7
  2 |          1 |           2 | Учебная задача 1-2  |           2 | 2026-11-06 |            6
 36 |          2 |          16 | Учебная задача 2-16 |           1 | 2026-11-06 |            6
 37 |          2 |          17 | Учебная задача 2-17 |           2 | 2026-11-07 |            5
 54 |          3 |          14 | Учебная задача 3-14 |           4 | 2026-11-07 |            5
  4 |          1 |           4 | Учебная задача 1-4  |           4 | 2026-11-08 |            4
 21 |          2 |           1 | Учебная задача 2-1  |             | 2026-11-08 |            4
 39 |          2 |          19 | Учебная задача 2-19 |           4 | 2026-11-09 |            3
 56 |          3 |          16 | Учебная задача 3-16 |             | 2026-11-09 |            3
  6 |          1 |           6 | Учебная задача 1-6  |           1 | 2026-11-10 |            2
 23 |          2 |           3 | Учебная задача 2-3  |           3 | 2026-11-10 |            2
 24 |          2 |           4 | Учебная задача 2-4  |           4 | 2026-11-11 |            1
 58 |          3 |          18 | Учебная задача 3-18 |           3 | 2026-11-11 |            1
(17 rows)

 project_id |     project_name      | task_count | high_count | high_pct 
------------+-----------------------+------------+------------+----------
          1 | Учебный каталог       |         20 |          7 |    35.00
          2 | Планирование семестра |         20 |          7 |    35.00
          3 | Архив материалов      |         20 |          7 |    35.00
          4 | Пустой проект         |          0 |          0 |         
(4 rows)

 project_id |     project_name      | task_count | estimated_count | mean_planned_days 
------------+-----------------------+------------+-----------------+-------------------
          1 | Учебный каталог       |         20 |              19 |             10.32
          2 | Планирование семестра |         20 |              18 |              9.50
          3 | Архив материалов      |         20 |              18 |              9.33
          4 | Пустой проект         |          0 |               0 |                  
(4 rows)

 project_id |     project_name      | task_count | done_count | completion_pct | completion_rank 
------------+-----------------------+------------+------------+----------------+-----------------
          1 | Учебный каталог       |         20 |          5 |          25.00 |               1
          2 | Планирование семестра |         20 |          5 |          25.00 |               1
          3 | Архив материалов      |         20 |          5 |          25.00 |               1
          4 | Пустой проект         |          0 |          0 |                |                
(4 rows)

 project_id |     project_name      | unassigned_count | active_unassigned_count 
------------+-----------------------+------------------+-------------------------
          1 | Учебный каталог       |                2 |                       1
          2 | Планирование семестра |                3 |                       3
          3 | Архив материалов      |                3 |                       2
(3 rows)


```
## task_tracker_study_repeat: schema.sql
```text
BEGIN
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
CREATE INDEX
COMMENT
COMMENT
COMMENT
COMMIT

```
## task_tracker_study_repeat: seed.sql
```text
BEGIN
INSERT 0 6
 setval 
--------
      6
(1 row)

INSERT 0 4
 setval 
--------
      4
(1 row)

INSERT 0 16
 setval 
--------
     16
(1 row)

INSERT 0 60
 setval 
--------
     60
(1 row)

COMMIT

```
## task_tracker_study_repeat: checks.sql
```text
BEGIN
DO
 invalid_project_column_count 
------------------------------
                            0
(1 row)

ROLLBACK
psql:/Users/shibaboy/Desktop/файлы/MISIS/4 Year/task-tracker-db/sql/checks.sql:42: NOTICE:  PASS: tasks_assignee_fk (SQLSTATE 23503)
psql:/Users/shibaboy/Desktop/файлы/MISIS/4 Year/task-tracker-db/sql/checks.sql:42: NOTICE:  PASS: tasks_project_column_fk (SQLSTATE 23503)
psql:/Users/shibaboy/Desktop/файлы/MISIS/4 Year/task-tracker-db/sql/checks.sql:42: NOTICE:  PASS: tasks_priority_check (SQLSTATE 23514)
psql:/Users/shibaboy/Desktop/файлы/MISIS/4 Year/task-tracker-db/sql/checks.sql:42: NOTICE:  PASS: tasks_project_number_unique (SQLSTATE 23505)

```
## task_tracker_study_repeat: queries.sql
```text
 project_id |     project_name      | task_count 
------------+-----------------------+------------
          1 | Учебный каталог       |         20
          2 | Планирование семестра |         20
          3 | Архив материалов      |         20
          4 | Пустой проект         |          0
(4 rows)

 position |    stage     | task_count 
----------+--------------+------------
        0 | К выполнению |         15
        1 | В работе     |         15
        2 | Проверка     |         15
        3 | Завершено    |         15
(4 rows)

 assignee_id |  username  | active_count 
-------------+------------+--------------
           1 | Участник 1 |            7
           2 | Участник 2 |            8
           3 | Участник 3 |            8
           4 | Участник 4 |            8
           5 | Участник 5 |            8
           6 | Участник 6 |            0
(6 rows)

 id | project_id | task_number |        title        | assignee_id |  due_date  | overdue_days 
----+------------+-------------+---------------------+-------------+------------+--------------
 17 |          1 |          17 | Учебная задача 1-17 |           2 | 2026-11-04 |            8
 51 |          3 |          11 | Учебная задача 3-11 |           1 | 2026-11-04 |            8
  1 |          1 |           1 | Учебная задача 1-1  |           1 | 2026-11-05 |            7
 18 |          1 |          18 | Учебная задача 1-18 |           3 | 2026-11-05 |            7
 52 |          3 |          12 | Учебная задача 3-12 |           2 | 2026-11-05 |            7
  2 |          1 |           2 | Учебная задача 1-2  |           2 | 2026-11-06 |            6
 36 |          2 |          16 | Учебная задача 2-16 |           1 | 2026-11-06 |            6
 37 |          2 |          17 | Учебная задача 2-17 |           2 | 2026-11-07 |            5
 54 |          3 |          14 | Учебная задача 3-14 |           4 | 2026-11-07 |            5
  4 |          1 |           4 | Учебная задача 1-4  |           4 | 2026-11-08 |            4
 21 |          2 |           1 | Учебная задача 2-1  |             | 2026-11-08 |            4
 39 |          2 |          19 | Учебная задача 2-19 |           4 | 2026-11-09 |            3
 56 |          3 |          16 | Учебная задача 3-16 |             | 2026-11-09 |            3
  6 |          1 |           6 | Учебная задача 1-6  |           1 | 2026-11-10 |            2
 23 |          2 |           3 | Учебная задача 2-3  |           3 | 2026-11-10 |            2
 24 |          2 |           4 | Учебная задача 2-4  |           4 | 2026-11-11 |            1
 58 |          3 |          18 | Учебная задача 3-18 |           3 | 2026-11-11 |            1
(17 rows)

 project_id |     project_name      | task_count | high_count | high_pct 
------------+-----------------------+------------+------------+----------
          1 | Учебный каталог       |         20 |          7 |    35.00
          2 | Планирование семестра |         20 |          7 |    35.00
          3 | Архив материалов      |         20 |          7 |    35.00
          4 | Пустой проект         |          0 |          0 |         
(4 rows)

 project_id |     project_name      | task_count | estimated_count | mean_planned_days 
------------+-----------------------+------------+-----------------+-------------------
          1 | Учебный каталог       |         20 |              19 |             10.32
          2 | Планирование семестра |         20 |              18 |              9.50
          3 | Архив материалов      |         20 |              18 |              9.33
          4 | Пустой проект         |          0 |               0 |                  
(4 rows)

 project_id |     project_name      | task_count | done_count | completion_pct | completion_rank 
------------+-----------------------+------------+------------+----------------+-----------------
          1 | Учебный каталог       |         20 |          5 |          25.00 |               1
          2 | Планирование семестра |         20 |          5 |          25.00 |               1
          3 | Архив материалов      |         20 |          5 |          25.00 |               1
          4 | Пустой проект         |          0 |          0 |                |                
(4 rows)

 project_id |     project_name      | unassigned_count | active_unassigned_count 
------------+-----------------------+------------------+-------------------------
          1 | Учебный каталог       |                2 |                       1
          2 | Планирование семестра |                3 |                       3
          3 | Архив материалов      |                3 |                       2
(3 rows)


```
