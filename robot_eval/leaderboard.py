"""Our mini-leaderboard: robot_eval/scores.csv -> a markdown table.

    python3 robot_eval/leaderboard.py [scores.csv]

Only executed trials count (dry runs test plumbing, not manipulation).
Score = points earned / points possible across every executed trial.
"""
import csv
import statistics
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def table(rows):
    by_model = defaultdict(list)
    for row in rows:
        if row["executed"] == "True":
            by_model[(row["model"], row["revision"][:8], row["end_effector"])].append(row)
    lines = ["| Rank | Model | Rev | End effector | Score | Successes | Tasks | Median round trip |",
             "|---|---|---|---|---|---|---|---|"]
    ranked = []
    for (model, rev, effector), trials in by_model.items():
        earned = sum(int(t["score"]) for t in trials)
        possible = sum(int(t["max_score"]) for t in trials)
        latency = [float(t["median_round_trip_s"]) for t in trials if t["median_round_trip_s"]]
        ranked.append((earned / possible if possible else 0, model, rev, effector,
                       sum(t["success"] == "True" for t in trials), len(trials),
                       len({t["task"] for t in trials}),
                       f"{statistics.median(latency):.2f}s" if latency else "-"))
    ranked.sort(key=lambda r: -r[0])
    for rank, (frac, model, rev, effector, wins, n, tasks, latency) in enumerate(ranked, 1):
        lines.append(f"| {rank} | {model} | {rev} | {effector} | {frac:.0%} | {wins}/{n} | {tasks} | {latency} |")
    return "\n".join(lines)


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "scores.csv"
    if not path.exists():
        raise SystemExit(f"no scores yet at {path}")
    with open(path, newline="") as handle:
        print(table(list(csv.DictReader(handle))))


if __name__ == "__main__":
    main()
