"""Выгрузка фактических SQL-результатов. DATABASE_URL не печатается и не сохраняется."""
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
import psycopg

ROOT = Path(__file__).resolve().parents[1]

def main():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Задайте DATABASE_URL для отдельной учебной БД")
    source = ROOT / "sql/queries.sql"
    chunks = re.split(r"^-- query: (\w+)\s*$", source.read_text(encoding="utf-8"), flags=re.M)
    target = ROOT / "results/queries"
    target.mkdir(parents=True, exist_ok=True)
    with psycopg.connect(url) as conn:
        conn.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ ONLY")
        version = conn.execute("SELECT version()").fetchone()[0]
        for key, sql in zip(chunks[1::2], chunks[2::2]):
            with conn.cursor() as cur:
                cur.execute(sql)
                with (target / (key + ".csv")).open("w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([col.name for col in cur.description])
                    writer.writerows(cur.fetchall())
    (ROOT / "results/postgresql_version.txt").write_text(version + "\n", encoding="utf-8")
    receipt = {"snapshot": "2026-11-12", "synthetic": True,
               "exported_at_utc": datetime.now(timezone.utc).isoformat(),
               "queries_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
               "csv_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(target.glob("*.csv"))}}
    (ROOT / "results/manifest.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("Выгружено 8 фактических результатов и версия PostgreSQL")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Не выводим детали исключения подключения: они могут содержать реквизиты.
        print(f"Ошибка выгрузки: {type(exc).__name__}; проверьте подключение и схему", file=sys.stderr)
        sys.exit(1)
