# Аудит исходной схемы
Проверено чтением исходников 2026-11-12. Источник: соседний `diploma`, ветка dev.
Живая БД приложения не подключалась; соответствие кода развёрнутой схеме НЕ проверено.
Незакоммиченные изменения присутствовали до начала работы, включая package.json/package-lock.json,
node_modules и отчёты. Их не исправляли и не включали в новый проект.

## Источники
Пути относительно корня исходного Task Tracker:
- backend-tt/db/ensure-schema.js: строки 4–74 CREATE, 76–131 ALTER и исправления данных, 133–176 индексы; ensureSchema выполняет последовательность без общей транзакции.
- backend-tt/db/models.js: Sequelize-модели; это не подтверждение фактических ограничений сервера.
- backend-tt/routes/task-routes.js: POST /tasks, строки 145–205 — текущий req.auth.userId записывается в user_id.
- backend-tt/services/board-service.js: строки 175–240 — создание карточки пишет user_id; patch существующей задачи его не заменяет.
- backend-tt/utils/task-utils.js: нормализация приоритетов, tags и планирования.
- frontend-tt/task-tracker-frontend/src/pages/gantt/GanttPage.tsx: строки 78–89 — plannedDate используется как start, end=start+durationDays−1; минимум один день — правило отображения.
- frontend-tt/task-tracker-frontend/src/pages/kanban/planning.ts: неделя = 7 дней.

## Определения CREATE
Если не отмечено иначе, nullable разрешён. Все created_at — TIMESTAMP NOT NULL DEFAULT NOW(), без часового пояса.
Все SERIAL id имеют PK. FK по умолчанию ON UPDATE NO ACTION.

| Таблица | Поля и ограничения по DDL |
|---|---|
| users | id SERIAL PK; username VARCHAR(50) UNIQUE NOT NULL; password_hash VARCHAR(255) NOT NULL; created_at |
| projects | id SERIAL PK; name TEXT NOT NULL; theme TEXT NOT NULL DEFAULT ''; created_at |
| columns | id SERIAL PK; name VARCHAR(100) NOT NULL; client_id TEXT; project_id INTEGER FK projects ON DELETE CASCADE; position INTEGER NOT NULL DEFAULT 0; created_at |
| tasks | id SERIAL PK; user_id INTEGER NOT NULL FK users CASCADE; title VARCHAR(100) NOT NULL; text TEXT NOT NULL DEFAULT ''; stat VARCHAR(100) NOT NULL; priority VARCHAR(50) NOT NULL DEFAULT 'normal'; column_id INTEGER FK columns SET NULL; client_id TEXT; project_id INTEGER FK projects CASCADE; task_number INTEGER; customer_name TEXT; assignee_name TEXT; assignee_initials TEXT; planned_date DATE; duration_weeks INTEGER NOT NULL DEFAULT 0; duration_days INTEGER NOT NULL DEFAULT 0; tags JSONB NOT NULL DEFAULT []; position INTEGER NOT NULL DEFAULT 0; created_at; UNIQUE(user_id,id) избыточен при PK(id) |
| board_state | id INTEGER PK (без SERIAL); project_id INTEGER FK projects CASCADE; board JSONB NOT NULL; next_task_number INTEGER NOT NULL; created_at; updated_at TIMESTAMP NOT NULL DEFAULT NOW() |
| activity_log | id SERIAL PK; event_type VARCHAR(64) NOT NULL; actor_user_id INTEGER FK users SET NULL; metadata JSONB NOT NULL DEFAULT {}; created_at |

## Изменения и индексы
ALTER удаляет columns.user_id, добавляет недостающие поля, расширяет tasks.text до TEXT,
заполняет tasks.project_id по колонке, обнуляет несовместимый column_id.
Нормализует normal/неизвестный приоритет в medium, но CHECK допустимых приоритетов в исходном DDL отсутствует.
Проверка tasks_column_requires_project_chk: column_id IS NULL OR project_id IS NOT NULL.
Составной tasks_project_column_fk: (project_id,column_id) → columns(project_id,id), ON DELETE SET NULL
(без списка полей — затрагивает обе ссылки). Ограничения добавляются NOT VALID, затем VALIDATE.
Отдельные FK project_id и column_id остаются. Исторические состояния могут отличаться: CREATE IF NOT EXISTS
не синхронизирует все старые определения, а последовательность не атомарна.

Индексы после успешного ensureSchema:
- UNIQUE columns_project_id_id_idx (project_id,id);
- UNIQUE columns_project_id_client_id_idx (project_id,client_id) WHERE client_id IS NOT NULL;
- columns_project_id_position_idx (project_id,position);
- UNIQUE tasks_project_id_client_id_idx (project_id,client_id) WHERE client_id IS NOT NULL;
- UNIQUE tasks_project_id_task_number_idx (project_id,task_number) WHERE task_number IS NOT NULL;
- tasks_project_id_position_idx (project_id,position);
- UNIQUE board_state_project_id_idx (project_id) WHERE project_id IS NOT NULL;
- activity_log_created_at_idx (created_at DESC,id DESC).
Удаляются прежние индексы columns_user_id_name_idx, columns_user_id_client_id_idx,
columns_client_id_idx, tasks_user_id_client_id_idx, tasks_user_id_task_number_idx;
последние два индекса board_state/activity_log пересоздаются.
PK и username UNIQUE также создают индексы. Nullable project_id оставляет возможность строк вне проекта.

## Семантика и JSONB
user_id подтверждён как пользователь, создавший задачу через приложение, отдельно от текстового assignee_name.
stat дублирует название колонки. planned_date — плановое начало для Ганта, не подтверждённый дедлайн.
Длительность нормализуется как weeks*7+days, остаток дней 0–6; в БД нет CHECK для её неотрицательности.
JSONB tags предполагается массивом строк (код обрезает до 20), board — объект доски,
metadata — метаданные события. В DDL нет JSONB-проверок структуры или GIN-индексов;
DEFAULT не запрещает JSON другой формы. Ни структура живых JSONB, ни данные сервера не исследовались.
Модели Sequelize имеют отличия от DDL: например STRING без длины и default stat='Создана'.
Для аудита ограничений приоритет отдан явному SQL ensure-schema.js, не предположению о sync моделей.
