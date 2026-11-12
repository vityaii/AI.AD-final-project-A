# Task Tracker DB — итоговая работа, трек A
Самостоятельный учебный проект PostgreSQL, без приложения и авторизации.
Данные полностью синтетические: 6 пользователей, 4 проекта, 16 этапов, 60 задач.
Дата аналитического среза: **2026-11-12**. Автор, группа и облачная ссылка: не указаны.

## Структура
- [sql/schema.sql](sql/schema.sql) — четыре таблицы, ограничения и индексы.
- [sql/seed.sql](sql/seed.sql), [data/](data/) — одинаковые записи в SQL и CSV.
- [sql/queries.sql](sql/queries.sql) — 8 аналитических вопросов и запросов.
- [sql/checks.sql](sql/checks.sql) — проверки ожидаемых нарушений, откат.
- [diagrams/er.mmd](diagrams/er.mmd), [diagrams/er.svg](diagrams/er.svg) — ER-модель.
- [python/](python/) — выгрузка из PostgreSQL и три графика по результатам SQL.
- [results/](results/) — фактические CSV, версия сервера, графики, протокол проверки.
- [docs/source_schema_audit.md](docs/source_schema_audit.md) — аудит исходников.
- [docs/model_decisions.md](docs/model_decisions.md) — изменения и метрики.
- [docs/data_dictionary.md](docs/data_dictionary.md) — словарь полей.
- [docs/report_draft.md](docs/report_draft.md) — черновик отчёта.

## Зависимости и запуск
PostgreSQL 17+ и psql/createdb, Python 3.11+, pip, зависимости из python/requirements.txt.
Полный набор фактически установленных версий сохранён в `python/requirements-lock.txt`; для точного повторения окружения установите его вместо requirements.txt.
Установка системных служб не требуется. Git нужен для локального репозитория.
На этой машине PostgreSQL установлен в `/Library/PostgreSQL/17/bin`; при необходимости добавьте
`export PATH="/Library/PostgreSQL/17/bin:$PATH"` в текущий терминал.
Команды выполняются из корня нового проекта. Не используйте реквизиты БД приложения.

1. На отдельном учебном сервере создайте **новую** БД с уникальным именем:
   `createdb task_tracker_study_20261112`. Если имя занято, выберите другое; ничего не удаляйте.
2. Задайте `DATABASE_URL` в текущем терминале для этой БД. Пример без пароля:
   `export DATABASE_URL='postgresql:///task_tracker_study_20261112'`.
   Для защищённого сервера передайте пароль безопасно через окружение; не сохраняйте в проект.
3. До создания таблиц проверьте назначение и пустоту:
   `psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -c 'SELECT current_database(), current_user;' -c '\dt'`.
   Если это не новая пустая учебная БД — остановитесь. Скрипты ничего не очищают.
4. Выполните последовательно:

```sh
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f sql/schema.sql
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f sql/seed.sql
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f sql/checks.sql
psql "$DATABASE_URL" -X -v ON_ERROR_STOP=1 -f sql/queries.sql
python3 -m venv .venv
.venv/bin/python -m pip install -r python/requirements.txt
.venv/bin/python python/export_results.py
.venv/bin/python python/visualize.py
```

Проверки ловят только ожидаемый SQLSTATE с нужным именем ограничения, иные ошибки прерывают запуск.
ROLLBACK сохраняет строки. Проверки используют явный отрицательный id, не расходуя identity-последовательность.
seed.sql — одноразовый, транзакционный; повторный запуск даст конфликт PK, а не дублирование/очистку.
В CSV пустые nullable-ячейки — NULL. Не загружайте CSV поверх уже выполненного seed.sql.
Экспорт — одна read-only repeatable-read транзакция; manifest фиксирует хеши SQL и CSV.
Графики требуют фактического экспорта и проверяют хеши входных CSV.

Для повторной проверки создайте вторую новую БД с другим именем и повторите шаги 2–4.
Не выполняйте DROP и не перезаписывайте существующую БД.

## Метрики и ограничения
Завершение определяется columns.is_done; активные — все остальные задачи.
Просрочены незавершённые задачи с due_date < 2026-11-12; NULL означает неизвестный срок,
а не подтверждённое отсутствие просрочки. Доля завершения пустого проекта — NULL.
Средняя длительность включает только известные оценки, в календарных днях.
Количество задач не измеряет производительность или фактическую нагрузку.
Нет истории/дат завершения: скорость и своевременность завершённых задач не вычисляются.
Исходный planned_date означал начало; due_date — явно выбранный новый учебный дедлайн.

Репозиторий локальный, без импортированной истории и remote. Коммит не создаётся автоматически.
Открыть отдельным окном: `code --new-window .` или VS Code → File → New Window → Open Folder.
Фактический статус проверки приведён в [results/validation.md](results/validation.md).
