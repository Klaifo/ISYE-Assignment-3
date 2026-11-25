"""ISyE 3133 PA3: Final exam scheduling."""
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
import gurobipy as gp
from gurobipy import GRB
from data import load_data

WEIGHTS = {'same_day': 1, 'b2b': 5, 'overnight': 3, 'triple': 10}
LIMITS = list(range(25))
ROOM_CHANGE_WEIGHT = 0.01


def solve_schedule(d, max_moves=24, time_limit=300):
    # 1. Read the sets and parameters from data.py.
    E = d['E']  # exam sections
    P = d['P']  # usable ISyE periods
    R = d['R']  # rooms
    S = d['S']  # students
    A = sorted(d['A'])  # available (room, period) pairs
    courses = sorted(set(d['course'].values()))

    # Include fixed external exams in the student timeline.
    external_periods = set()
    for s in S:
        external_periods.update(d['ext_s'][s])
    T = [p for p in d['P_all'] if p in P or p in external_periods]
    days = sorted({d['day'][p] for p in T})
    start = {}
    end = {}
    for p in T:
        start[p] = datetime.fromisoformat(d['day'][p] + 'T' + d['start'][p])
        end[p] = datetime.fromisoformat(d['day'][p] + 'T' + d['end'][p])

    # Identify penalized pairs using the actual dates and times.
    pair_type = {}
    overlapping = []
    for i, p in enumerate(T):
        for q in T[i+1:]:
            gap = start[q] - end[p]
            if gap < timedelta(0):
                overlapping.append((p, q))
            elif d['day'][p] == d['day'][q]:
                if gap <= timedelta(minutes=30):
                    pair_type[p, q] = 'b2b'
                else:
                    pair_type[p, q] = 'same_day'
            elif ((start[q].date() - start[p].date()).days == 1
                  and start[p].hour == 18 and start[q].hour == 8):
                pair_type[p, q] = 'overnight'

    # 2. Create the model and binary decision variables.
    model = gp.Model('Final_Exam_Scheduling')
    model.Params.Threads = 1
    model.Params.TimeLimit = time_limit
    model.Params.MIPGap = 0

    # x = 1 if exam e is assigned to room r at period p.
    x = model.addVars([(e, r, p) for e in E for r, p in A],
                      vtype=GRB.BINARY, name='x')
    # y = 1 if exam e is held at period p, regardless of room.
    y = model.addVars(E, P, vtype=GRB.BINARY, name='y')
    # z = 1 if course c is allowed to use room r at period p.
    z = model.addVars([(c, r, p) for c in courses for r, p in A],
                      vtype=GRB.BINARY, name='z')
    # busy = 1 if student s has an exam at period p.
    busy = model.addVars(S, T, vtype=GRB.BINARY, name='busy')
    # pair = 1 if p and q are consecutive exams for student s.
    pair = model.addVars([(s, p, q) for s in S for p, q in pair_type],
                         vtype=GRB.BINARY, name='pair')
    # triple = 1 if student s has at least three exams on a day.
    triple = model.addVars(S, days, vtype=GRB.BINARY, name='triple')

    # 3. Each exam must be assigned to exactly one available room and period.
    for e in E:
        model.addConstr(x.sum(e, '*', '*') == 1)
        for p in P:
            model.addConstr(y[e, p] == x.sum(e, '*', p))

    # 4. Room capacity and same-course room sharing.
    for r, p in A:
        model.addConstr(gp.quicksum(d['size'][e] * x[e, r, p]
                                    for e in E) <= d['cap'][r])
        # At most one course can use a room in a period.
        model.addConstr(z.sum('*', r, p) <= 1)
        for e in E:
            model.addConstr(x[e, r, p] <= z[d['course'][e], r, p])

    # 5. Prevent student conflicts, including fixed external exams.
    for s in S:
        for p in T:
            internal = 0
            if p in P:
                internal = gp.quicksum(y[e, p] for e in sorted(d['E_s'][s]))
            fixed = int(p in d['ext_s'][s])
            # busy is binary, so the right side cannot exceed one.
            model.addConstr(busy[s, p] == internal + fixed)
        for p, q in overlapping:
            model.addConstr(busy[s, p] + busy[s, q] <= 1)

    # 6. Count penalties only between consecutive exams for each student.
    for p, q in pair_type:
        between = [t for t in T if start[p] < start[t] < start[q]]
        for s in S:
            model.addConstr(pair[s, p, q] <= busy[s, p])
            model.addConstr(pair[s, p, q] <= busy[s, q])
            for t in between:
                model.addConstr(pair[s, p, q] <= 1 - busy[s, t])
            # If both exams occur and none is between them, pair must be 1.
            model.addConstr(pair[s, p, q] >= busy[s, p] + busy[s, q] - 1
                            - gp.quicksum(busy[s, t] for t in between))

    # Add 10 points once per day with three or more exams.
    for day in days:
        daily_periods = [p for p in T if d['day'][p] == day]
        for s in S:
            count = gp.quicksum(busy[s, p] for p in daily_periods)
            model.addConstr(count >= 3 * triple[s, day])
            model.addConstr(count <= 2 + len(daily_periods) * triple[s, day])

    # 7. Limit disruption and minimize workload plus room-change penalty.
    workload = gp.quicksum(WEIGHTS[pair_type[p, q]] * pair[s, p, q]
                           for s in S for p, q in pair_type)
    workload += WEIGHTS['triple'] * triple.sum()
    moves = gp.quicksum(1 - y[e, d['draft_period'][e]] for e in E)
    room_changes = gp.quicksum(x[e, r, p] for e, r, p in x.keys()
                               if r != d['draft_room'][e])
    model.addConstr(moves <= max_moves, name='disruption_limit')
    model.setObjective(workload + ROOM_CHANGE_WEIGHT * room_changes, GRB.MINIMIZE)
    model.optimize()

    # 8. Return the schedule and summary statistics.
    info = {'rooms': len(R), 'max_moves': max_moves, 'status': model.Status,
            'optimal': model.Status == GRB.OPTIMAL, 'runtime': model.Runtime}
    if model.SolCount == 0:
        return None, info

    rows = []
    moved_exams = set()
    for e, r, p in x.keys():
        if x[e, r, p].X > 0.5:
            rows.append((e, p, r))
            if p != d['draft_period'][e]:
                moved_exams.add(e)
    schedule = pd.DataFrame(rows, columns=['exam_id', 'period_id', 'room_id'])
    counts = {'same_day': 0, 'b2b': 0, 'overnight': 0}
    for s, p, q in pair.keys():
        if pair[s, p, q].X > 0.5:
            counts[pair_type[p, q]] += 1
    info.update(workload=round(workload.getValue()), moves=len(moved_exams),
                room_changes=round(room_changes.getValue()),
                triple_days=round(triple.sum().getValue()),
                b2b_pairs=counts['b2b'], overnight_pairs=counts['overnight'],
                long_gap_pairs=counts['same_day'],
                students_affected=sum(bool(d['E_s'][s] & moved_exams) for s in S),
                mip_gap=model.MIPGap, combined_bound=model.ObjBound)
    return schedule, info


def main():
    # Command-line options let us test a few limits before the full sweep.
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data/')
    parser.add_argument('--output', default='results')
    parser.add_argument('--limits', nargs='+', type=int, default=LIMITS)
    parser.add_argument('--time-limit', type=float, default=300)
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    results = []

    # Run the same model with three rooms and then four rooms.
    for extra_room in (False, True):
        d = load_data(str(Path(args.data)) + '/', include_room4=extra_room)
        for limit in args.limits:
            schedule, info = solve_schedule(d, limit, args.time_limit)
            results.append(info)
            if schedule is not None:
                filename = f'schedule_{len(d["R"])}rooms_{limit}moves.csv'
                schedule.to_csv(output / filename, index=False)
            pd.DataFrame(results).to_csv(output / 'summary.csv', index=False)
            print(info)


if __name__ == '__main__':
    main()
