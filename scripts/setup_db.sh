#!/usr/bin/env bash
# Создание новой учебной БД и последовательный запуск SQL.
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ "${1:-}" == "--help" ]]; then
    cat <<'HELP'
Использование: bash scripts/setup_db.sh [имя_новой_бд]
По умолчанию: task_tracker_study_YYYYMMDD_HHMMSS
Подключение: PGHOST, PGPORT, PGUSER, PGPASSWORD или ~/.pgpass.
PGMAINTENANCE_DB задаёт служебную БД (по умолчанию postgres).
PG_BIN задаёт каталог с psql и createdb, если они отсутствуют в PATH.
Существующая БД никогда не очищается: при совпадении имени запуск остановится.
HELP
    exit 0
fi
if [[ $# -gt 1 ]]; then
    echo 'Ошибка: укажите только имя новой БД или --help.' >&2
    exit 1
fi

DB_NAME="${1:-task_tracker_study_$(date +%Y%m%d_%H%M%S)}"
if [[ ! "$DB_NAME" =~ ^[a-z][a-z0-9_]{0,62}$ ]]; then
    echo 'Имя БД: 1–63 символа, строчные латинские буквы, цифры и _, начало — буква.' >&2
    exit 1
fi

if [[ -n "${PG_BIN:-}" ]]; then
    export PATH="$PG_BIN:$PATH"
elif ! command -v psql >/dev/null 2>&1 && [[ -x /Library/PostgreSQL/17/bin/psql ]]; then
    export PATH="/Library/PostgreSQL/17/bin:$PATH"
fi
for tool in psql createdb; do
    if ! command -v "$tool" >/dev/null 2>&1; then
        echo "Не найден $tool. Установите PostgreSQL и задайте PG_BIN — каталог его bin." >&2
        exit 1
    fi
done

echo "Создание новой учебной БД: $DB_NAME"
# createdb откажется работать, если БД уже существует. SQL тогда не запускается.
createdb --maintenance-db="${PGMAINTENANCE_DB:-postgres}" -- "$DB_NAME"
export PGDATABASE="$DB_NAME"
psql -X -v ON_ERROR_STOP=1 -c 'SELECT current_database(), current_user;'
for filename in schema.sql seed.sql checks.sql queries.sql; do
    echo "Выполнение: $filename"
    psql -X -v ON_ERROR_STOP=1 -f "$ROOT/sql/$filename"
done

printf '\nГотово. Таблицы созданы, данные загружены, проверки и запросы выполнены.\n'
printf 'Для Python в этом же терминале выполните (сохраните PGHOST/PGPORT/PGUSER):\n'
printf "export DATABASE_URL='dbname=%s'\n" "$DB_NAME"
printf '.venv/bin/python python/export_results.py\n'
printf '.venv/bin/python python/visualize.py\n'
