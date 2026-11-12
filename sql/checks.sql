-- Только после seed.sql. Каждое ожидаемое нарушение проверяется по SQLSTATE и имени ограничения.
BEGIN;
DO $checks$
DECLARE caught_name text; base tasks%ROWTYPE; invalid_user integer; other_column integer;
BEGIN
 SELECT * INTO STRICT base FROM tasks WHERE id=1;
 SELECT max(id)+1 INTO invalid_user FROM users;
 SELECT id INTO STRICT other_column FROM columns WHERE project_id<>base.project_id ORDER BY id LIMIT 1;
 BEGIN
  INSERT INTO tasks (id,project_id,column_id,user_id,assignee_id,task_number,title,priority) VALUES (-1,base.project_id,base.column_id,base.user_id,invalid_user,999901,base.title,base.priority);
  RAISE EXCEPTION 'Ограничение tasks_assignee_fk не сработало';
 EXCEPTION WHEN SQLSTATE '23503' THEN
  GET STACKED DIAGNOSTICS caught_name = CONSTRAINT_NAME;
  IF caught_name <> 'tasks_assignee_fk' THEN RAISE; END IF;
  RAISE NOTICE 'PASS: tasks_assignee_fk (SQLSTATE 23503)';
 END;
 BEGIN
  INSERT INTO tasks (id,project_id,column_id,user_id,assignee_id,task_number,title,priority) VALUES (-1,base.project_id,other_column,base.user_id,base.assignee_id,999902,base.title,base.priority);
  RAISE EXCEPTION 'Ограничение tasks_project_column_fk не сработало';
 EXCEPTION WHEN SQLSTATE '23503' THEN
  GET STACKED DIAGNOSTICS caught_name = CONSTRAINT_NAME;
  IF caught_name <> 'tasks_project_column_fk' THEN RAISE; END IF;
  RAISE NOTICE 'PASS: tasks_project_column_fk (SQLSTATE 23503)';
 END;
 BEGIN
  INSERT INTO tasks (id,project_id,column_id,user_id,assignee_id,task_number,title,priority) VALUES (-1,base.project_id,base.column_id,base.user_id,base.assignee_id,999903,base.title,'urgent');
  RAISE EXCEPTION 'Ограничение tasks_priority_check не сработало';
 EXCEPTION WHEN SQLSTATE '23514' THEN
  GET STACKED DIAGNOSTICS caught_name = CONSTRAINT_NAME;
  IF caught_name <> 'tasks_priority_check' THEN RAISE; END IF;
  RAISE NOTICE 'PASS: tasks_priority_check (SQLSTATE 23514)';
 END;
 BEGIN
  INSERT INTO tasks (id,project_id,column_id,user_id,assignee_id,task_number,title,priority) VALUES (-1,base.project_id,base.column_id,base.user_id,base.assignee_id,base.task_number,base.title,base.priority);
  RAISE EXCEPTION 'Ограничение tasks_project_number_unique не сработало';
 EXCEPTION WHEN SQLSTATE '23505' THEN
  GET STACKED DIAGNOSTICS caught_name = CONSTRAINT_NAME;
  IF caught_name <> 'tasks_project_number_unique' THEN RAISE; END IF;
  RAISE NOTICE 'PASS: tasks_project_number_unique (SQLSTATE 23505)';
 END;
END;
$checks$;
-- Контроль связей должен вернуть 0.
SELECT count(*) AS invalid_project_column_count FROM tasks t
LEFT JOIN columns c ON (c.project_id,c.id)=(t.project_id,t.column_id) WHERE c.id IS NULL;
ROLLBACK;
