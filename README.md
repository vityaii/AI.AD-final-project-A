# Task Tracker DB — итоговая работа, трек A

Автор: Никитин Виктор. Группа: КультИИ АД Мод 3 1.3.
Реляционная БД учёта задач проектов на PostgreSQL. Все данные синтетические:
8 пользователей, 4 проекта, 16 этапов, 120 задач.

## Проверка преподавателем

Начните с [инструкции по распаковке и проверке](START_HERE.md).
Нужны PostgreSQL 17+ и Python 3.11+. После установки Python-зависимостей:

```sh
python -m pip install -r python/requirements.txt
python python/verify_project.py --host localhost --port 5432 --user postgres
```

Скрипт запросит пароль, создаст новую учебную БД, выполнит SQL, проверит данные
и построит графики. Итог — `verification/summary.md` со статусом PASS.
Эталонная папка `results` не изменяется. SQL также можно выполнить вручную в pgAdmin.

## Структура

- [sql/schema.sql](sql/schema.sql) — четыре таблицы, ограничения и индексы.
- [sql/seed.sql](sql/seed.sql), [data](data/) — одинаковые данные в SQL и CSV.
- [sql/checks.sql](sql/checks.sql) — проверки ограничений с откатом.
- [sql/queries.sql](sql/queries.sql) — восемь аналитических вопросов.
- [python/verify_project.py](python/verify_project.py) — полный запуск и проверка.
- [python/export_results.py](python/export_results.py) — выгрузка результатов из БД.
- [python/visualize.py](python/visualize.py) — графики по CSV.
- [python/generate_seed.py](python/generate_seed.py) — воспроизводимое создание синтетических данных.
- [diagrams/er.svg](diagrams/er.svg) — ER-диаграмма.
- [docs/report_draft.md](docs/report_draft.md) — отчёт и выводы.
- [docs/data_dictionary.md](docs/data_dictionary.md) — словарь полей.
- [docs/model_decisions.md](docs/model_decisions.md) — решения и определения метрик.
- [docs/source_schema_audit.md](docs/source_schema_audit.md) — аудит исходной модели.
- [results](results/) — готовые результаты запросов, графики и протокол проверки.

## Метрики

Завершение определяется columns.is_done. Просрочены незавершённые задачи со сроком
раньше 12.11.2026. Неизвестный срок не означает отсутствие просрочки.
Доля завершения пустого проекта — NULL. Средняя длительность учитывает только известные оценки.
Количество назначений не измеряет производительность сотрудников.
Без истории изменений нельзя определить скорость и своевременность завершения.

Репозиторий: https://github.com/vityaii/AI.AD-final-project-A (приватный).
