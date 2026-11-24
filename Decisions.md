# Decisions Log

Running list of modeling calls, why we made them, and what is still open.
Update this whenever we decide something. It feeds the report's "choices" section.

## Data facts (from exploration)

- 24 ISyE exams to schedule, 360 students.
- 26 periods: 21 regular, 3 reading, 2 conflict. Reading and conflict periods are off limits.
- Only 8 periods have any room available: P03, P05, P09, P14, P17, P21, P22, P23.
  All 4 rooms are available in exactly those 8.
- 3 rooms x 8 periods = 24 slots for 24 exams. With one exam per room, the draft is completely full.
  The 4th room (Klaus-2443) adds 8 empty slots.
- Dec 17 holds 3 of the 8 usable periods (P21, P22, P23), so the draft puts 9 exams on one day.
- Section sizes: 54 to 66. Largest: ISYE4133-A and ISYE4134-A (66). Smallest: ISYE2028-B, ISYE3030-A, ISYE3044-B (54).
- Room capacities: Klaus-1447 75, Klaus-1456 100, Klaus-1443 200, Klaus-2443 100 (extra room).
- 7 external common exams, all in the evening slot (18:00 to 20:50): P04, P08, P12, P16, P20.
  Two pairs share a period (MATH 1551 + ECE 3710 in P04, MATH 1553 + 1554 in P16).
- 210 students take an external exam (each takes exactly one).
- Exam loads: 150 students have 4 exams, 210 have 5.
- Every consecutive period on a day has a 30 min gap.
  Same-day back to back pairs that can occur: P03 -> P04, P21 -> P22, P22 -> P23.
- Evening to 8am next-day pairs: P04 -> P05, P16 -> P17, P20 -> P21.
- No ISyE period is in the evening, so ISyE exams can never clash with externals.

## Decided

1. **No splitting exams across rooms.** Max section (66) < min room capacity (75), so it is never needed.
2. **Room sharing only for sections of the same course**, and only if combined enrollment fits the room.
   In practice only Klaus-1443 (200) can hold 2 or 3 sections. Reason: same exam and instructor, so no proctoring confusion.
3. **Each exam is held at exactly one time** (given in the assignment).
4. **Makeup / unexpected exams are out of scope.** No data for them. Goes in limitations.

## Student penalty (locked)

Scored on consecutive exams in each student's timeline.

- Overlapping exams: not allowed (hard constraint)
- Two exams same day, long gap: 1
- Back to back, 30 min gap (P03 -> P04, P21 -> P22, P22 -> P23): 3
- Evening exam -> 8am next day (P04 -> P05, P16 -> P17, P20 -> P21): 5
- 3+ exams in one day: +10 on top of transitions
- Only possible 3-exam day is Dec 17 (P21, P22, P23, all b2b) = 3 + 3 + 10 = 16.
  The "3 exams, 0 or 1 b2b" cases cannot occur in this data.

Why: overnight is worse than a 30 min b2b (lost sleep and study night).
A long same-day gap (e.g. morning + evening) leaves time to recover, so it gets a light penalty.

## Disruption (locked)

- Primary: number of sections whose period changed from the draft.
- Room changes: tracked separately, tiny weight (0.01) so the solver doesn't shuffle rooms for no reason.
  Changing rooms is less disruptive than changing times.
- Reported: number of students with at least one exam time changed.

## Tradeoff (proposed)

- Pareto curve: minimize student penalty s.t. at most k exams moved, k = 0, 1, 2, ...
- Plot 3 rooms vs 4 rooms on one chart. That is the extra room answer.
- With 3 rooms the board is full, so most moves are swaps (2 disruptions).
  With 4 rooms an exam can move alone into an empty slot.

## Evaluation (to report)

- Total student penalty
- Worst-off student's penalty
- Number of students with any penalty
- Count of each situation (b2b, overnight, long gap, 3-in-a-day)
- Sensitivity check: rerun with a second set of weights and compare

## Open

- Whose interests the model does not capture (instructors, TAs, proctors, room staff,
  students with accommodations, students outside the pilot).

## Roles

- Kelechi: data loader (`data.py`) and evaluator (`evaluate.py`).
- Temidayo: Gurobi model (`model.py`).
- Together: metrics, formulation review, 3 vs 4 room comparison, report and slides.
