"""Три графика из CSV, полученных export_results.py. Агрегации здесь отсутствуют."""
import csv
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    source = ROOT / "results/queries" / name
    manifest = json.loads((ROOT / "results/manifest.json").read_text(encoding="utf-8"))
    if hashlib.sha256(source.read_bytes()).hexdigest() != manifest["csv_sha256"][name]:
        raise RuntimeError("CSV изменён после выгрузки: " + name)
    with source.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def main():
    target = ROOT / "results/charts"
    target.mkdir(parents=True, exist_ok=True)
    specs = [
        ("02_stage_distribution.csv", "stage", "task_count", "Распределение задач по этапам", "Задачи, шт.", "stages"),
        ("03_active_assignees.csv", "username", "active_count", "Активные задачи по исполнителям", "Задачи, шт.", "assignees"),
        ("07_completion_ranking.csv", "project_name", "completion_pct", "Доля завершения проектов", "Завершённые задачи, %", "completion"),
    ]
    for filename, label, value, title, unit, stem in specs:
        rows = load(filename)
        fig, ax = plt.subplots(figsize=(10, 5.5), layout="constrained")
        values = [float(r[value]) if r[value] else 0 for r in rows]
        bars = ax.barh([r[label] for r in rows], values, color="#287c8e")
        ax.invert_yaxis()
        ax.set_xlabel(unit)
        ax.set_title(title + "\nСинтетические данные · срез 12.11.2026")
        if stem == "completion":
            ax.set_xlim(0, 105)
        else:
            ax.set_xlim(0, max(values, default=0)*1.25+1)
        for bar, row in zip(bars, rows):
            text = row[value] if row[value] else "не определена (нет задач)"
            ax.text(bar.get_width()+0.3, bar.get_y()+bar.get_height()/2, text, va="center", fontsize=9)
        ax.spines[["top", "right"]].set_visible(False)
        fig.savefig(target / (stem + ".png"), dpi=160)
        fig.savefig(target / (stem + ".svg"))
        plt.close(fig)
    print("Построено 3 графика по проверенным CSV")

if __name__ == "__main__":
    main()
