"""
demo.py: check and score one schedule with the independent evaluator.

Usage: python demo.py [schedule_csv] [max_moves]
Default: results/schedule_3rooms_6moves.csv with a 6-move limit.
"""
import sys
import pandas as pd
from data import load_data
from evaluate import score, audit

path = sys.argv[1] if len(sys.argv) > 1 else "results/schedule_3rooms_6moves.csv"
k = int(sys.argv[2]) if len(sys.argv) > 2 else 6

d = load_data("data/", include_room4="4rooms" in path)
sched = pd.read_csv(path)

problems = audit(sched, d, max_moves=k)
print("feasibility problems:", problems if problems else "none")

r = score(dict(zip(sched.exam_id, sched.period_id)), d,
          rooms=dict(zip(sched.exam_id, sched.room_id)))["summary"]
for key, val in r.items():
    print(f"{key:>20}: {val}")
