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
- Exam loads: 150 students have 4 exams, 210 have 5 (verify in notebook).
- Evening to next-morning pairs: P04 -> P05, P16 -> P17, P20 -> P21.
- Same-day, 30-minute-gap pair: P03 (ends 17:30) -> P04 (starts 18:00).

## Decided

1. **No splitting exams across rooms.** Max section (66) < min room capacity (75), so it is never needed.
2. **Room sharing only for sections of the same course**, and only if combined enrollment fits the room.
   In practice only Klaus-1443 (200) can hold 2 or 3 sections. Reason: same exam and instructor, so no proctoring confusion.
3. **Each exam is held at exactly one time** (given in the assignment).
4. **Makeup / unexpected exams are out of scope.** No data for them. Goes in limitations.

## Leaning toward (confirm together)

5. **Back to back counts in two forms:**
   - same day, consecutive (P03 -> P04, 30 min gap)
   - overnight (evening exam -> 8am next morning: P04 -> P05, P16 -> P17, P20 -> P21)
   Overnight may be worse than a same-day pair with a long gap (lost sleep and study night).
6. **Same-day pairs with a long gap (e.g. morning + evening) get a light penalty or none.**
   An 8 hour gap leaves time to recover and study.
7. **3+ exams in one day is the worst case** and should get the heaviest penalty.

## Open (decide on our call)

- Final student workload / fairness metric and penalty weights.
- Disruption metric: number of exams moved? number of students whose exam time changed? room changes count?
- How to trade off workload vs. disruption: weighted sum, lexicographic, or a Pareto sweep.
- Whose interests the model does not capture (instructors, TAs, proctors, room staff, students with accommodations, students outside the pilot).

## Roles

- Kelechi: data loader (`data.py`) and evaluator (`evaluate.py`).
- Temidayo: Gurobi model (`model.py`).
- Together: metrics, formulation review, 3 vs 4 room comparison, report and slides.
