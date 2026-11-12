-- Все данные синтетические. Фиксированный срез: 2026-11-12.

-- query: 01_project_counts
-- Вопрос: Сколько задач в каждом проекте, включая пустые? Количество, шт.
SELECT p.id AS project_id, p.name AS project_name, count(t.id) AS task_count
FROM projects p LEFT JOIN tasks t ON t.project_id=p.id
GROUP BY p.id, p.name ORDER BY p.id;

-- query: 02_stage_distribution
-- Вопрос: Как задачи распределены по этапам? Количество, шт.; нулевые этапы сохранены.
SELECT c.position, c.name AS stage, count(t.id) AS task_count
FROM columns c LEFT JOIN tasks t ON (t.project_id,t.column_id)=(c.project_id,c.id)
GROUP BY c.position,c.name ORDER BY c.position,c.name;

-- query: 03_active_assignees
-- Вопрос: Сколько незавершённых задач назначено каждому пользователю? Все пользователи, включая нулевые.
SELECT u.id AS assignee_id,u.username,
 count(t.id) FILTER (WHERE NOT c.is_done) AS active_count
FROM users u LEFT JOIN tasks t ON t.assignee_id=u.id
LEFT JOIN columns c ON (c.project_id,c.id)=(t.project_id,t.column_id)
GROUP BY u.id,u.username ORDER BY u.id;

-- query: 04_overdue
-- Вопрос: Какие незавершённые задачи имеют известный срок раньше 2026-11-12? День среза ещё не просрочен.
WITH snapshot AS (SELECT DATE '2026-11-12' AS as_of)
SELECT t.id,t.project_id,t.task_number,t.title,t.assignee_id,t.due_date,
 s.as_of-t.due_date AS overdue_days
FROM tasks t JOIN columns c ON (c.project_id,c.id)=(t.project_id,t.column_id)
CROSS JOIN snapshot s
WHERE NOT c.is_done AND t.due_date < s.as_of
ORDER BY t.due_date,t.id;

-- query: 05_high_priority
-- Вопрос: Какова доля high среди всех задач проекта? Проценты; NULL для пустого проекта.
SELECT p.id AS project_id,p.name AS project_name,count(t.id) AS task_count,
 count(t.id) FILTER (WHERE t.priority='high') AS high_count,
 round(100.0*count(t.id) FILTER (WHERE t.priority='high')/NULLIF(count(t.id),0),2) AS high_pct
FROM projects p LEFT JOIN tasks t ON t.project_id=p.id
GROUP BY p.id,p.name ORDER BY p.id;

-- query: 06_average_duration
-- Вопрос: Какова средняя известная плановая длительность? Календарные дни; неизвестные исключены, покрытие показано.
SELECT p.id AS project_id,p.name AS project_name,count(t.id) AS task_count,
 count(t.planned_duration_days) AS estimated_count,
 round(avg(t.planned_duration_days),2) AS mean_planned_days
FROM projects p LEFT JOIN tasks t ON t.project_id=p.id
GROUP BY p.id,p.name ORDER BY p.id;

-- query: 07_completion_ranking
-- Вопрос: Как проекты ранжируются по доле завершения? Проценты; пустой проект без доли и ранга.
WITH metrics AS (
 SELECT p.id AS project_id,p.name AS project_name,count(t.id) AS task_count,
 count(t.id) FILTER (WHERE c.is_done) AS done_count,
 count(t.id) FILTER (WHERE c.is_done)::numeric/NULLIF(count(t.id),0) AS fraction
 FROM projects p LEFT JOIN tasks t ON t.project_id=p.id
 LEFT JOIN columns c ON (c.project_id,c.id)=(t.project_id,t.column_id)
 GROUP BY p.id,p.name
), ranked AS (
 SELECT project_id,dense_rank() OVER (ORDER BY fraction DESC) AS completion_rank
 FROM metrics WHERE task_count>0
)
SELECT m.project_id,m.project_name,m.task_count,m.done_count,
 round(100*m.fraction,2) AS completion_pct,r.completion_rank
FROM metrics m LEFT JOIN ranked r USING(project_id)
ORDER BY r.completion_rank NULLS LAST,m.project_id;

-- query: 08_unassigned
-- Вопрос: В каких проектах есть неназначенные задачи и сколько? HAVING исключает нулевые группы; из них сколько активных?
SELECT p.id AS project_id,p.name AS project_name,
 sum(CASE WHEN t.assignee_id IS NULL THEN 1 ELSE 0 END) AS unassigned_count,
 sum(CASE WHEN t.assignee_id IS NULL AND NOT c.is_done THEN 1 ELSE 0 END) AS active_unassigned_count
FROM projects p JOIN tasks t ON t.project_id=p.id
JOIN columns c ON (c.project_id,c.id)=(t.project_id,t.column_id)
WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.id=t.assignee_id)
GROUP BY p.id,p.name HAVING count(*)>0 ORDER BY p.id;
