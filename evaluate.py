"""
evaluate.py: score any exam schedule using the rules in Decisions.md.

Usage:
    from data import load_data
    from evaluate import score
    d = load_data("data/")
    result = score(d["draft_period"], d)                 # baseline
    result = score(new_period, d, rooms=new_room)        # a model solution

`schedule` is a dict: exam -> period (same shape as d["draft_period"]).
`rooms` (optional) is a dict: exam -> room, used to count room changes.
"""

from datetime import date, timedelta
import pandas as pd

# ---- penalty weights (from Decisions.md) ----
W_LONG_GAP  = 1    # two exams same day, not back to back
W_B2B       = 5    # consecutive periods same day (30 min gap)
W_OVERNIGHT = 3    # evening exam -> 8am next calendar day
W_THREE_DAY = 10   # 3+ exams in one day, added on top of transitions


def label_pair(a, b, d):
    """Label two consecutive exams (period a, then period b) in one student's timeline."""
    day_a, day_b = d["day"][a], d["day"][b]
    pos_a, pos_b = d["P_all"].index(a), d["P_all"].index(b)

    if day_a == day_b:
        # same day: back to back if the periods are next to each other in the calendar
        return "b2b" if pos_b == pos_a + 1 else "long_gap"

    # different days: overnight if a is an evening exam and b is 8am the very next day
    next_day = (date.fromisoformat(day_a) + timedelta(days=1)).isoformat()
    if d["start"][a] == "18:00" and d["start"][b] == "08:00" and day_b == next_day:
        return "overnight"

    return None


def score(schedule, d, rooms=None):
    weight = {"long_gap": W_LONG_GAP, "b2b": W_B2B, "overnight": W_OVERNIGHT}
    rows = []

    for s in d["S"]:
        # 1. all of this student's exam periods: ISyE (from the schedule) + externals (fixed)
        periods = [schedule[e] for e in d["E_s"][s]] + list(d["ext_s"][s])

        # 2. direct conflicts: same period appears twice
        conflicts = len(periods) - len(set(periods))

        # 3. sort into calendar order
        periods = sorted(periods, key=d["P_all"].index)

        # 4. label each consecutive pair
        counts = {"long_gap": 0, "b2b": 0, "overnight": 0}
        for a, b in zip(periods, periods[1:]):
            lab = label_pair(a, b, d)
            if lab:
                counts[lab] += 1

        # 5. days with 3+ exams
        per_day = pd.Series([d["day"][p] for p in periods]).value_counts()
        three_days = int((per_day >= 3).sum())

        penalty = sum(weight[k] * counts[k] for k in counts) + W_THREE_DAY * three_days

        rows.append({"student": s, "conflicts": conflicts, **counts,
                     "three_in_day": three_days, "penalty": penalty})

    students = pd.DataFrame(rows)

    # ---- disruption vs the draft ----
    moved = [e for e in d["E"] if schedule[e] != d["draft_period"][e]]
    room_changes = 0
    if rooms is not None:
        room_changes = sum(1 for e in d["E"] if rooms[e] != d["draft_room"][e])
    affected = set().union(*(d["S_e"][e] for e in moved)) if moved else set()

    summary = {
        "total_penalty":      int(students["penalty"].sum()),
        "worst_student":      int(students["penalty"].max()),
        "students_penalized": int((students["penalty"] > 0).sum()),
        "conflicts":          int(students["conflicts"].sum()),
        "long_gap":           int(students["long_gap"].sum()),
        "b2b":                int(students["b2b"].sum()),
        "overnight":          int(students["overnight"].sum()),
        "three_in_day":       int(students["three_in_day"].sum()),
        "exams_moved":        len(moved),
        "room_changes":       room_changes,
        "students_affected":  len(affected),
    }
    return {"summary": summary, "students": students, "moved": moved}


if __name__ == "__main__":
    # baseline: score the draft. python evaluate.py
    from data import load_data
    d = load_data("data/", include_room4=False)
    r = score(d["draft_period"], d, rooms=d["draft_room"])
    for k, v in r["summary"].items():
        print(f"{k:20s} {v}")
    print("\nS001:")
    print(r["students"].set_index("student").loc["S001"])
