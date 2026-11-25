# ISyE 3133 --- Programming Assignment 3: Decisions and Implementation Summary

**Project:** Improving the Final Exam Schedule\
**Team:** Temidayo Solomon and Kelechi Ejieke\
**Status:** Optimization completed; recommended schedule independently scored; final feasibility audit and report pending.

## 1. Goal and data

Reduce total student exam workload while limiting disruption to the draft schedule. Compare the existing three classrooms with the option of adding a fourth classroom.

-   24 ISyE exam sections, 360 students, section sizes 54--66.
-   Eight usable periods: P03, P05, P09, P14, P17, P21, P22, P23.
-   Seven fixed external common exams; 210 students take one external exam.
-   Three rooms provide 24 available room-period combinations; four provide 32. These are not strict exam-count limits because same-course sharing is allowed.

  Room           Capacity Scenario
  ------------ ---------- ----------------------
  Klaus-1447           75 Both
  Klaus-1456          100 Both
  Klaus-1443          200 Both
  Klaus-2443          100 Optional fourth room

## 2. Final modeling decisions

### Feasibility and assumptions

-   Each section is assigned to exactly one room and one period; no splitting across rooms. All sections fit individually in the smallest room.
-   Only available room-period combinations in regular exam periods may be used. Reading and conflict periods are excluded.
-   External exam times are fixed and included in each student's timeline.
-   Student exam overlaps are prohibited, not merely penalized.
-   Sections of the same course may share a room if their combined enrollment fits. Different courses cannot share a room at the same time. Only the 200-seat room can accommodate multiple sections in this dataset.
-   No makeup exams or individual accommodations are modeled.

### Student workload

  Situation                                                             Final penalty
  ------------------------------------------------------ ----------------------------
  Same-day consecutive exams with a long gap                                        1
  Back-to-back exams (30-minute gap in this dataset)                                5
  Evening exam followed by 8 AM exam next calendar day                              3
  Three or more exams on one day                           Additional 10 once per day

Back-to-back exams are weighted most heavily among pair penalties because students have very little time to recover or prepare between exams. Overnight exams also limit rest and preparation, but provide a longer interval. This is a proposed justification for the team's chosen weights, not a measured student preference.

Count only consecutive exams in each student's chronological timeline, including external exams. Add the daily triple-exam penalty on top of the transition penalties. Three consecutive exams on December 17 score 5 + 5 + 10 = 20, not 21: the first and third exams are not a consecutive pair.

### Disruption and objective

-   A time move means a section's assigned period differs from its draft period, regardless of room.
-   Room changes are counted separately, even when a section's time also changes.
-   Students affected counts distinct students with at least one ISyE section moved in time, not students whose room alone changes.
-   Minimize `workload + 0.01 * room_changes` subject to `moves <= k`.
-   Workload is integer-valued; at most 24 room changes contribute 0.24, so room changes cannot outweigh a one-point workload improvement.
-   Sweep k = 0 through 24 for each room scenario. A limit is an upper bound, not a requirement to move exactly k sections. Actual moves are not a secondary objective.

## 3. Implementation

`data.py` (Kelechi): reads seven CSV files and constructs sets, enrollments, capacities, available slots, external periods and draft assignments.

`model.py` (Temidayo): implements the binary integer program in Python/Gurobi. Main binary variables:

  -----------------------------------------------------------------------------------------------------------------
  Variable                            Meaning
  ----------------------------------- -----------------------------------------------------------------------------
  x\[e,r,p\]                          Section e assigned to room r at period p

  y\[e,p\]                            Section e scheduled at period p

  z\[c,r,p\]                          Course c permitted to occupy room r at period p

  busy\[s,p\]                         Student s has an exam at period p

  pair\[s,p,q\]                       p and q are consecutive exams for student s and form a penalized transition

  triple\[s,day\]                     Student s has at least three exams that day
  -----------------------------------------------------------------------------------------------------------------

The constraints enforce one assignment, link x and y, enforce room capacities and same-course sharing, prevent conflicts, identify consecutive pairs (no intervening exam), identify triple-exam days, and impose the disruption limit. The objective minimizes workload plus the small room-change penalty.

`evaluate.py` (Kelechi): independently scores schedules using student timelines and counts same-period conflicts, workload and disruption. It does not independently check room capacities, room availability, same-course sharing, or general cross-period overlaps.

`results/`: contains 50 schedule CSV files and `summary.csv`. Filenames use the allowed move limit, not necessarily the actual number of moves.

## 4. Work completed and commands

1.  Set up the `isye3133` Conda environment with Python 3.11, pandas and Gurobi 13.0.3; verified academic license.
2.  Ran `python data.py` to inspect the dataset.
3.  Implemented the optimization model and tested small move limits.
4.  Identified a mismatch between the initial model and evaluator: back-to-back and overnight weights were reversed. Corrected the model to back-to-back = 5 and overnight = 3; retained the evaluator's weights.
5.  Reran the complete optimization sweep with corrected weights.
6.  Compared the 50 results and selected a preliminary compromise schedule.
7.  Independently evaluated the six-move, three-room schedule; its metrics matched the model and it had zero same-period conflicts.

``` bash
conda activate isye3133
python data.py
python evaluate.py
python model.py --limits 0
python model.py --limits $(seq 0 24)
```

The full sweep solves 25 limits for each of two room scenarios. Solver settings: one thread, 300-second time limit per run, MIPGap = 0. The corrected summary confirms 50/50 optimal solutions, status 2, zero reported MIP gaps, and runtimes of approximately 0.014--1.651 seconds per solve.

## 5. Corrected baseline

Workload = 5(121) + 3(81) + 1(59) + 10(0) = **907**.

The earlier baseline of 827 and earlier optimization results used the reversed weights and are superseded. The draft report also needs its old penalty table, justification, triple-day example, baseline and worst-student score updated. The corrected worst-student baseline should be taken from the evaluator output, not assumed from the old report.

## 6. Full optimization results

Minimum workload at each allowed time-move limit (from corrected `summary(1).csv`, uploaded from local `results/summary.csv`):

    Allowed moves   3 rooms   4 rooms
  --------------- --------- ---------
                0       907       907
                1       722       722
                2       615       607
                3       518       518
                4       408       408
                5       338       338
                6       282       282
                7       282       282
                8       282       282
                9       282       282
               10       282       282
               11       265       265
               12       253       253
               13       253       253
               14       218       218
               15       218       218
               16       218       218
               17       215       215
               18       215       215
               19       215       215
               20       215       215
               21       215       215
               22       215       215
               23       215       215
               24       215       215

The optional room improves workload only at k = 2 (615 to 607, eight points). Both scenarios reach 215 at k = 17. The curve is flat from k = 6 through 10, illustrating diminishing returns. When plotting a nondominated frontier, use actual moves and remove duplicate or dominated points; a larger allowed limit may produce the same workload with more actual moves.

## 7. Preliminary recommendation

Recommend `results/schedule_3rooms_6moves.csv`, subject to team agreement and final feasibility validation. Do not request the fourth room for this recommendation.

  --------------------------------------------------------------------------------------------------------------------
  Metric                                         Draft   Recommended (3 rooms, k=6)   Minimum workload (3 rooms, k=17)
  --------------------------------- ------------------ ---------------------------- ----------------------------------
  Workload                                         907                          282                                215

  Workload reduction                                0%                       68.91%                             76.30%

  Actual time moves                                  0                            6                                 17

  Room changes                                       0                            3                                  3

  Back-to-back pairs                               121                            0                                  0

  Overnight pairs                                   81                           76                                 32

  Long-gap pairs                                    59                           54                                119

  Triple-exam days                                   0                            0                                  0

  Students affected by time moves                    0                          291                                360
  --------------------------------------------------------------------------------------------------------------------

The six-move solution captures 625/692 = 90.32% of the maximum achievable workload reduction while changing the times of only 25% of sections. It eliminates all back-to-back pairs. Moving another 11 sections would save only 67 additional workload points. However, 291/360 (80.83%) students still experience a time change; this is a meaningful drawback. The recommendation is a judgment about tradeoffs, not a uniquely optimal policy across all preferences.

## 8. Independent validation completed

The following command was run successfully:

``` bash
python -c "import pandas as pd; from data import load_data; from evaluate import score; d = load_data('data/', include_room4=False); s = pd.read_csv('results/schedule_3rooms_6moves.csv'); print(score(dict(zip(s.exam_id, s.period_id)), d, rooms=dict(zip(s.exam_id, s.room_id)))['summary'])"
```

Evaluator output for the recommended schedule:

``` text
total_penalty: 282
worst_student: 4
students_penalized: 119
conflicts: 0
long_gap: 54
b2b: 0
overnight: 76
three_in_day: 0
exams_moved: 6
room_changes: 3
students_affected: 291
```

The workload independently recomputes as 54 + 3(76) = 282. The combined objective is 282.03. There are 241 students with no workload penalty. This validates the recommended schedule's scoring and same-period conflicts, but is not a complete independent feasibility audit.

## 9. Limitations and remaining work

-   Workload weights are subjective and do not capture all student preferences or individual fairness.

-   Instructor/TA grading schedules, proctors, room staff, accommodations, and students outside the dataset are not fully represented.

-   No monetary cost is assigned to the fourth room.

-   The model's optimality is relative to the modeled constraints and chosen objective.

-   The latest local model was not independently inspected in full after the weight edit; implementation description is based on the available model_final.py and the confirmed corrected header and run outputs.

-   [x] Data loading and model implementation

-   [x] Correct penalty weights and rerun all 50 scenarios

-   [x] Verify solver statuses and compare room scenarios

-   [x] Independently score the preliminary recommendation

-   [ ] Independently audit all 50 schedules, including room capacity, availability, sharing, assignments, overlaps and disruption limits

-   [ ] Confirm recommendation with teammate

-   [ ] Update mathematical formulation, Pareto graph and two-page report

-   [ ] Prepare five-minute presentation, formulation appendix and code demonstration

-   [ ] Finalize accurate AI disclosure: ChatGPT assisted with model development, debugging, commands, interpretation and documentation; team members ran the code and should verify all claims. Add any other AI use by either teammate.

## 10. How I explain my contribution

I worked on the Python and Gurobi optimization model that assigns exam sections to rooms and periods while minimizing student workload. We used binary decision variables and constraints to prevent conflicts and enforce room restrictions. I tested every disruption limit from zero to 24 moves with three and four classrooms, producing 50 optimal solutions. After correcting the penalty weights to match our evaluator, I reran the experiments and compared the results. Our preliminary recommendation moves six sections, reduces workload from 907 to 282, and eliminates back-to-back exams without requiring another classroom. I also ran the independent evaluator to confirm the recommended schedule's workload and disruption metrics.

## Source and version notes

Based on the team draft `Programming_Assignment_3.pdf`, input CSVs, `model_final.py` (with the subsequently confirmed weight correction), `evaluate(1).py`, corrected `summary(1).csv`, and the terminal evaluator output provided in the conversation. The corrected weights and results supersede the older draft. This is a working project record, not the final submitted report.
