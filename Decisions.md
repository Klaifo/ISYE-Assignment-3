# Decisions Log

**Project:** ISyE 3133 PA3, Improving the Final Exam Schedule
**Team:** Kelechi Ejieke and Temidayo Solomon
**Status:** Model done. All 50 schedules audited and feasible. Recommendation, report and slides in progress.

Single source of truth for modeling calls, results and open items. Merged from `Decisions.md` (Kelechi) and `Decisions-1.md` (Temidayo) on Nov 24.

## 1. Data facts

- 24 ISyE exam sections, 360 students, section sizes 54 to 66.
  Largest: ISYE4133-A and ISYE4134-A (66). Smallest: ISYE2028-B, ISYE3030-A, ISYE3044-B (54).
- 26 periods: 21 regular, 3 reading, 2 conflict. Reading and conflict periods are off limits.
- Only 8 periods have rooms: P03, P05, P09, P14, P17, P21, P22, P23. All 4 rooms are open in exactly those 8.
- Dec 17 holds 3 of the 8 usable periods (P21, P22, P23), so the draft puts 9 exams on one day.

| Room | Capacity | Scenario |
| --- | --- | --- |
| Klaus-1447 | 75 | both |
| Klaus-1456 | 100 | both |
| Klaus-1443 | 200 | both |
| Klaus-2443 | 100 | optional 4th room |

- 3 rooms give 24 room-period slots, 4 rooms give 32. These are not hard exam limits, because same-course sections can share Klaus-1443.
- 7 external common exams, all evening (18:00 to 20:50): P04, P08, P12, P16, P20. MATH 1551 + ECE 3710 share P04, MATH 1553 + 1554 share P16.
- 210 students take exactly one external exam. 150 students have 4 exams total, 210 have 5.
- Every consecutive period on a day has a 30 min gap. Same-day back to back pairs that can occur: P03->P04, P21->P22, P22->P23.
- Evening to 8am next-day pairs: P04->P05, P16->P17, P20->P21. These only hit students with an external exam.
- No usable ISyE period is in the evening, so ISyE exams can never clash with externals directly.

## 2. Modeling decisions

### Feasibility

1. Each section gets exactly one room and one period. No splitting (max section 66 < min room 75).
2. Only available room-period pairs in regular periods.
3. External exams fixed and included in each student's timeline.
4. Student overlaps are a hard constraint, not a penalty.
5. Sections of the same course may share a room if combined enrollment fits. Different courses never share. Only Klaus-1443 can hold more than one section. Reason: same exam and instructor, so no proctoring confusion.
6. Makeup exams and accommodations are out of scope (no data). Goes in limitations.

### Student penalty

Scored on consecutive exams in each student's timeline, externals included.

| Situation | Penalty |
| --- | --- |
| Same day, long gap | 1 |
| Back to back, 30 min gap | 5 |
| Evening exam, then 8am next calendar day | 3 |
| 3+ exams in one day | +10 once per day, on top of transitions |

- The only possible 3-exam day is all of Dec 17 (P21, P22, P23) = 5 + 5 + 10 = 20. The first and third exams are not a consecutive pair, so no extra +1.
- Why: a 30 min back to back is the worst pair (no break, no food, no review). Overnight is next (short night, but time to sleep and eat). A long same-day gap leaves time to recover.
- Weights were swapped from 3/5 to 5/3 on Nov 24. The 3/5 version is the sensitivity check. These are team judgments, not measured student preferences.

### Disruption and objective

- A time move = a section's period differs from the draft, regardless of room.
- Room changes counted separately, weight 0.01, so the solver only changes rooms when it helps. 24 room changes max = 0.24 < 1 workload point, so they never outweigh a real improvement.
- Students affected = distinct students with at least one ISyE section moved in time.
- Minimize `workload + 0.01 * room_changes` s.t. `moves <= k`, swept k = 0 to 24 for 3 and 4 rooms. k is an upper bound, not a target.

## 3. Implementation

| File | Owner | What it does |
| --- | --- | --- |
| `data.py` | Kelechi | Reads the 7 CSVs into sets and dicts (`load_data(include_room4=...)`) |
| `model.py` | Temidayo | Binary IP in Gurobi. Variables x[e,r,p], y[e,p], z[c,r,p], busy[s,p], pair[s,p,q], triple[s,day] |
| `evaluate.py` | Kelechi | `score()`: independent penalty and disruption scoring. `audit()`: checks one assignment per exam, room availability, capacity, same-course sharing, student conflicts, move limit |
| `audit_results.py` | Kelechi | Runs `audit()` and `score()` on all 50 schedules, writes `results/audit.csv` |
| `make_pareto.py` | Kelechi | Builds the nondominated frontier and `results/pareto.png` |

Solver: 1 thread, 300 s limit, MIPGap = 0. All 50 runs optimal (status 2), 0.01 to 1.7 s each.

```bash
conda activate isye3133
python data.py                          # sanity check
python model.py --limits $(seq 0 24)    # full sweep, writes results/
python audit_results.py                 # independent audit
python make_pareto.py                   # chart
```

## 4. Results

**Baseline (draft):** 5(121) + 3(81) + 1(59) + 10(0) = **907**. 226 of 360 students penalized, worst student 8.

**Audit (Nov 24):** 50/50 schedules feasible. Evaluator penalty matches model workload on 50/50.

Nondominated frontier, 3 rooms (actual moves, from `results/frontier_3rooms.csv`):

| Moves | Penalty | Students with a time change |
| --- | --- | --- |
| 0 | 907 | 0 |
| 1 | 722 | 55 |
| 2 | 615 | 103 |
| 3 | 518 | 158 |
| 4 | 408 | 218 |
| 5 | 338 | 250 |
| **6** | **282** | **291** |
| 11 | 265 | 333 |
| 12 | 253 | 352 |
| 14 | 218 | 353 |
| 17 | 215 | 360 |

**4th room:** identical frontier except 2 moves (615 vs 607, 8 points). The 4-room model does place exams in Klaus-2443, but it gains nothing, because same-course sharing in Klaus-1443 already frees the slots. The k=6 3-room schedule stacks 2028-A+B, 3044-A+B, 3104-A+B and 3133-A+C in Klaus-1443. **Verdict: not worth it.** The extra room would only matter if room sharing were banned.

## 5. Recommendation (pending team sign-off)

`results/schedule_3rooms_6moves.csv`, 3 rooms, no extra room.

| Metric | Draft | Recommended (6 moves) | Min penalty (17 moves) |
| --- | --- | --- | --- |
| Total penalty | 907 | 282 (-69%) | 215 (-76%) |
| Back to backs | 121 | 0 | 0 |
| Overnight pairs | 81 | 76 | 32 |
| Long-gap pairs | 59 | 54 | 119 |
| 3-exam days | 0 | 0 | 0 |
| Students penalized | 226 | 119 | 138 |
| Worst student | 8 | 4 | 4 |
| Sections moved | 0 | 6 | 17 |
| Room changes | 0 | 3 | 3 |
| Students with a time change | 0 | 291 | 360 |

- 6 moves captures 625 of the 692 possible points (90%) and removes every back to back. 11 more moves buy only 67 more points.
- Drawback: 291 of 360 students (81%) see a time change. Every moved section carries about 60 students, so this is hard to avoid.
- Alternative if disruption matters more: 4 moves = 408 penalty, 218 students affected, 28 back to backs left.

## 6. Limitations

- Weights are subjective and may not match all student preferences.
- Total penalty is not a full fairness measure. We also report worst student and students penalized.
- Instructors and TAs (grading load), proctors, room staff, accommodations, and students outside the pilot are not modeled.
- No monetary cost assigned to the 4th room.
- Optimality is relative to the modeled constraints and objective.

## 7. To do

- [x] Data loader, evaluator, model
- [x] Correct weights, rerun all 50 scenarios, all optimal
- [x] Independent audit of all 50 schedules (feasibility + scores)
- [x] Pareto frontier with students affected
- [ ] Confirm recommendation (6 moves vs 4 moves) together
- [ ] Sensitivity check with the old 3/5 weights
- [ ] Formulation write-up, Pareto chart and results in the 2-page report
- [ ] Fill slides 5 and 6, formulation appendix, rehearse demo
- [ ] AI disclosure: ChatGPT (Temidayo: model development, debugging, commands, documentation) and Claude (Kelechi: data loader, evaluator, audit, report draft, slide deck, git help). Both teammates ran the code and verified results.
