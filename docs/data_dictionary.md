# Словарь учебной БД
Точная исполняемая схема: [schema.sql](../sql/schema.sql). Все id — integer identity BY DEFAULT, PK, NOT NULL.

| Таблица | Поле | Тип / NULL | Назначение и ограничения |
|---|---|---|---|
| users | id | integer, нет | PK |
| users | username | varchar(50), нет | Уникальное непустое имя синтетического участника, не логин авторизации |
| projects | id | integer, нет | PK |
| projects | name | text, нет | Непустое название |
| columns | id | integer, нет | PK |
| columns | project_id | integer, нет | FK projects, RESTRICT; совместно с id UNIQUE |
| columns | name | varchar(100), нет | Непустое название статуса |
| columns | position | integer, нет | Порядок от 0; UNIQUE(project_id,position) |
| columns | is_done | boolean, нет | Завершённый этап; default false |
| tasks | id | integer, нет | PK |
| tasks | project_id | integer, нет | FK projects, RESTRICT |
| tasks | column_id | integer, нет | Составной FK (project_id,column_id) → columns(project_id,id), RESTRICT |
| tasks | user_id | integer, нет | Создатель, FK users, RESTRICT |
| tasks | assignee_id | integer, да | Исполнитель, FK users, SET NULL |
| tasks | task_number | integer, нет | >0; UNIQUE(project_id,task_number) |
| tasks | title | varchar(100), нет | Непустой заголовок |
| tasks | text | text, нет | Описание, default пустая строка |
| tasks | priority | varchar(6), нет | low/medium/high, default medium |
| tasks | due_date | date, да | Последний допустимый день; NULL — неизвестен |
| tasks | planned_duration_days | integer, да | >0 календарных дней; NULL — нет оценки |

Обязательность статуса обеспечена NOT NULL column_id и FK. Разрешено несколько конечных колонок.
Ключи, UNIQUE и CHECK проверяются немедленно. Ключи создают индексы автоматически;
дополнительные индексы: tasks_project_column_idx, tasks_assignee_idx, tasks_author_idx,
tasks_due_date_idx (только известные сроки).
