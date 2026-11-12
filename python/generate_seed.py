"""Детерминированный учебный набор: CSV и seed.sql из одного источника."""
import csv
from datetime import date, timedelta
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]


def main():
    rng = random.Random(20261112)
    tables = {}
    for table in ("users", "projects", "columns", "tasks"):
        with (ROOT / "data" / (table + ".csv")).open(encoding="utf-8", newline="") as stream:
            reader = csv.DictReader(stream)
            tables[table] = (reader.fieldnames, list(reader))
    tables["users"] = (tables["users"][0], [
        {"id": str(i), "username": f"Участник {i}"} for i in range(1, 9)
    ])
    topics = {
        1: ["Импорт карточек", "Поиск по названию", "Фильтр по категории", "Проверка ISBN",
            "Обложки изданий", "Карточка автора", "Удаление дублей", "Сортировка выдачи",
            "Валидация формы", "Пагинация каталога", "Экспорт списка", "Доступность интерфейса",
            "Индексы поиска", "Пустая выдача", "Обработка ошибок", "Документация API",
            "Тестирование импорта", "Кеширование справочника"],
        2: ["Расписание занятий", "Конфликты аудиторий", "Календарь зачётов", "Импорт учебного плана",
            "Проверка дат", "Список преподавателей", "Учёт каникул", "Перенос занятия",
            "Экспорт расписания", "Уведомления об изменениях", "Фильтр по группе",
            "Шаблон семестра", "Проверка нагрузки"],
        3: ["Оцифровка материалов", "Поиск дубликатов", "Проверка ссылок", "Метки документов",
            "Права на чтение", "Архивирование версии", "Полнотекстовый поиск", "Резервная копия",
            "Восстановление файла", "Описание форматов"]}
    phases = ["реализация", "проверка граничных случаев", "исправления после ревью"]
    # Каталог активно развивается, семестр в работе, архив близок к завершению.
    stage_counts = {1: [18, 16, 7, 13], 2: [6, 14, 5, 13], 3: [2, 3, 3, 20]}
    teams = {1: [1, 2, 3, 7], 2: [2, 4, 5, 7], 3: [1, 5, 6]}
    tasks = []
    for project, counts in stage_counts.items():
        stages = [stage for stage, count in enumerate(counts) for _ in range(count)]
        rng.shuffle(stages)
        for number, stage in enumerate(stages, 1):
            # Первые 60 id сохраняют исходные пары проект/номер; новые id — 61–120.
            task_id = (project - 1) * 20 + number if number <= 20 else (
                60 + sum(sum(stage_counts[p]) - 20 for p in range(1, project)) + number - 20)
            topic = topics[project][(number - 1) % len(topics[project])]
            phase = phases[(number - 1) // len(topics[project])]
            unassigned = rng.random() < (0.38 if stage == 0 else 0.035)
            assignee = "" if unassigned else str(rng.choices(
                teams[project], weights=[4, 3, 2, 1] if project != 3 else [2, 3, 1])[0])
            missing_due = rng.random() < (0.32 if stage == 0 else 0.06)
            offset = rng.randint(-40, -2) if stage == 3 else rng.randint(
                -4 if stage == 0 else -12, 35 if stage == 0 else 14)
            tasks.append(dict(zip(tables["tasks"][0], [
                str(task_id), str(project), str((project - 1) * 4 + stage + 1),
                str(rng.choice(teams[project])), assignee, str(number), f"{topic}: {phase}",
                f"Синтетическая задача. {topic}; этап работ: {phase}. Проверить основной сценарий и ошибки ввода.",
                rng.choices(["low", "medium", "high"], weights=[20, 60, 20] if stage != 0 else [40, 50, 10])[0],
                "" if missing_due else str(date(2026, 11, 12) + timedelta(days=offset)),
                "" if rng.random() < (0.3 if stage == 0 else 0.05) else str(
                    rng.choices([1, 2, 3, 5, 8, 13], weights=[15, 25, 25, 20, 10, 5])[0])
            ])))
    tasks.sort(key=lambda row: int(row["id"]))
    tables["tasks"] = (tables["tasks"][0], tasks)
    assert len(tasks) == 120 and {int(t["id"]) for t in tasks} == set(range(1, 121))
    assert len({(t["project_id"], t["task_number"]) for t in tasks}) == 120
    sql = ["-- Искусственные данные: 8 пользователей, 4 проекта, 16 колонок, 120 задач.", "BEGIN;"]
    numeric = {"id", "project_id", "column_id", "user_id", "assignee_id", "task_number", "position", "planned_duration_days"}
    for table, (fields, rows) in tables.items():
        with (ROOT / "data" / (table + ".csv")).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        values = []
        for row in rows:
            encoded = []
            for field in fields:
                value = row[field]
                encoded.append("NULL" if value == "" else value if field in numeric else
                               value.upper() if field == "is_done" else "'" + value.replace("'", "''") + "'")
            values.append("(" + ", ".join(encoded) + ")")
        sql.append(f"INSERT INTO {table} ({', '.join(fields)}) VALUES\n" + ",\n".join(values) + ";")
        sql.append(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), (SELECT max(id) FROM {table}), true);")
    sql.append("COMMIT;")
    (ROOT / "sql/seed.sql").write_text("\n".join(sql) + "\n", encoding="utf-8")
    print("Сформированы CSV и seed.sql: 8 пользователей, 120 задач")


if __name__ == "__main__":
    main()
