"""
audit_results.py: independently audit every schedule in results/ and compare
the evaluator's scores with the model's summary.csv.

Usage: python audit_results.py
Writes results/audit.csv
"""
from pathlib import Path
import pandas as pd
from data import load_data
from evaluate import score, audit

RESULTS = Path("results")
summary = pd.read_csv(RESULTS / "summary.csv")
data = {3: load_data("data/", include_room4=False), 4: load_data("data/", include_room4=True)}

rows = []
for s in summary.itertuples():
    f = RESULTS / f"schedule_{s.rooms}rooms_{s.max_moves}moves.csv"
    d = data[s.rooms]
    sched = pd.read_csv(f)
    problems = audit(sched, d, max_moves=s.max_moves)
    r = score(dict(zip(sched.exam_id, sched.period_id)), d,
              rooms=dict(zip(sched.exam_id, sched.room_id)))["summary"]
    rows.append({
        "rooms": s.rooms, "max_moves": s.max_moves,
        "feasible": not problems, "problems": "; ".join(problems),
        "eval_penalty": r["total_penalty"], "model_workload": s.workload,
        "match": r["total_penalty"] == s.workload,
        "moves": r["exams_moved"], "room_changes": r["room_changes"],
        "students_affected": r["students_affected"],
        "students_penalized": r["students_penalized"], "worst_student": r["worst_student"],
        "b2b": r["b2b"], "overnight": r["overnight"], "long_gap": r["long_gap"],
        "three_in_day": r["three_in_day"],
    })

out = pd.DataFrame(rows)
out.to_csv(RESULTS / "audit.csv", index=False)
print(f"feasible: {out.feasible.sum()}/{len(out)}   scores match model: {out.match.sum()}/{len(out)}")
if not out.feasible.all():
    print(out.loc[~out.feasible, ["rooms", "max_moves", "problems"]].to_string(index=False))
print(out[["rooms", "max_moves", "moves", "eval_penalty", "students_affected",
           "students_penalized", "worst_student", "b2b", "overnight", "long_gap", "room_changes"]]
      .to_string(index=False))
