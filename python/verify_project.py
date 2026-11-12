"""Создание отдельной учебной БД, выполнение SQL и проверка результатов."""
import argparse
import csv
from datetime import datetime, timezone
import getpass
import os
from pathlib import Path
import sys

import psycopg
from psycopg import sql
from psycopg.conninfo import make_conninfo

import export_results
import visualize

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "verification"


def read_csv(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.reader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=os.environ.get("PGHOST", "localhost"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PGPORT", "5432")))
    parser.add_argument("--user", default=os.environ.get("PGUSER", "postgres"))
    parser.add_argument("--database", default="task_tracker_check_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
                        help="Имя новой БД. Существующая БД не изменяется.")
    parser.add_argument("--maintenance-db", default="postgres", help="Служебная БД для CREATE DATABASE")
    args = parser.parse_args()
    password = os.environ.get("PGPASSWORD")
    if password is None and sys.stdin.isatty():
        password = getpass.getpass(f"Пароль PostgreSQL для {args.user} (Enter — без пароля): ") or None
    connection = dict(host=args.host, port=args.port, user=args.user, password=password, connect_timeout=10)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {"status": "FAIL", "checked_at_utc": datetime.now(timezone.utc).isoformat(), "checks": []}
    log = []

    def passed(message):
        report["checks"].append(message)
        print("[OK] " + message, flush=True)

    try:
        with psycopg.connect(dbname=args.maintenance_db, autocommit=True, **connection) as admin:
            admin.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(args.database)))
        passed("Создана новая БД: " + args.database)
        # Данные загружаются только после успешного CREATE DATABASE.
        with psycopg.connect(dbname=args.database, autocommit=True, **connection) as conn:
            connection_string = make_conninfo(dbname=args.database, **connection)
            conn.add_notice_handler(lambda notice: log.append(notice.message_primary))
            if conn.execute("SELECT count(*) FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema')").fetchone()[0]:
                raise RuntimeError("БД не пустая; выберите другое имя через --database.")
            passed("Подключение к новой пустой PostgreSQL")
            for filename in ("schema.sql", "seed.sql", "checks.sql", "queries.sql"):
                log.append("\n=== " + filename + " ===")
                with conn.cursor() as cursor:
                    cursor.execute((ROOT / "sql" / filename).read_text(encoding="utf-8"), prepare=False)
                    while True:
                        if cursor.description:
                            log.append(" | ".join(col.name for col in cursor.description))
                            log.extend(" | ".join("NULL" if value is None else str(value) for value in row)
                                       for row in cursor.fetchall())
                        if not cursor.nextset():
                            break
                passed(filename + " выполнен")
            notices = [line for line in log if line.startswith("PASS:")]
            if len(notices) != 4:
                raise RuntimeError("Ожидались четыре успешные проверки ограничений")
            passed("Ограничения целостности: 4 проверки")
            for table, count in (("users", 8), ("projects", 4), ("columns", 16), ("tasks", 120)):
                expected = read_csv(ROOT / "data" / (table + ".csv"))
                fields = sql.SQL(", ").join(sql.Identifier(field) for field in expected[0])
                rows = conn.execute(sql.SQL("SELECT {} FROM {} ORDER BY id").format(fields, sql.Identifier(table))).fetchall()
                actual = [["" if value is None else str(value) for value in row] for row in rows]
                if len(rows) != count or actual != expected[1:]:
                    raise RuntimeError("Не совпадают исходный CSV и таблица " + table)
                passed(f"{table}: {count} записей, CSV совпадает с БД")
        export_results.RESULTS = OUTPUT
        visualize.RESULTS = OUTPUT
        # Пароль передаётся только в памяти, не сохраняется в отчёте или файлах.
        export_results.main(connection_string)
        expected_files = sorted((ROOT / "results/queries").glob("*.csv"))
        if len(expected_files) != 8:
            raise RuntimeError("Ожидались восемь эталонных CSV")
        for expected in expected_files:
            if read_csv(expected) != read_csv(OUTPUT / "queries" / expected.name):
                raise RuntimeError("Результат запроса отличается от эталона: " + expected.name)
        passed("Результаты всех 8 SQL-запросов совпадают с эталоном")
        visualize.main()
        for stem in ("stages", "assignees", "completion"):
            for extension in ("png", "svg"):
                path = OUTPUT / "charts" / (stem + "." + extension)
                if not path.is_file() or path.stat().st_size == 0:
                    raise RuntimeError("Не создан график " + path.name)
        passed("Графики: 3 PNG и 3 SVG")
        report["status"] = "PASS"
    except Exception as exc:
        # Реквизиты подключения и исходные сообщения libpq в отчёт не записываем.
        if isinstance(exc, psycopg.errors.DuplicateDatabase):
            message = "БД уже существует. Укажите другое имя через --database; данные не изменены."
        elif isinstance(exc, psycopg.errors.InsufficientPrivilege):
            message = "Недостаточно прав. Для создания учебной БД пользователю нужно право CREATEDB."
        elif isinstance(exc, psycopg.OperationalError):
            message = "Не удалось подключиться. Проверьте, что PostgreSQL запущен, а адрес, порт, пользователь и пароль верны."
        else:
            message = str(exc) if isinstance(exc, RuntimeError) else type(exc).__name__
        report["error"] = message
        print("[FAIL] " + message, file=sys.stderr)
    finally:
        (OUTPUT / "sql_log.txt").write_text("\n".join(log) + "\n", encoding="utf-8")
        lines = ["# Проверка проекта", "", "Итог: **" + report["status"] + "**", "",
                 "Время запуска (UTC): " + report["checked_at_utc"], ""]
        lines.extend("- [OK] " + item for item in report["checks"])
        if "error" in report:
            lines.append("- [FAIL] " + report["error"])
        (OUTPUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if report["status"] != "PASS":
        return 1
    print("\nПроверка завершена успешно. Отчёт: verification/summary.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
