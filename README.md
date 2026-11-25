# ISyE 3133 PA3: Final Exam Scheduling

Optimize a pilot GT final exam schedule (24 ISyE exams, 360 students) with Gurobi.
Kelechi Ejieke and Temidayo Solomon.

## Files
- `data.py`: loads the CSVs in `data/`
- `model.py`: the integer program (Gurobi)
- `evaluate.py`: independent scorer (`score`) and feasibility checker (`audit`)
- `audit_results.py`: audits and rescores every schedule in `results/`
- `make_pareto.py`: builds the workload vs. moves chart
- `demo.py`: audits and scores one schedule

## Run
```
pip install gurobipy pandas matplotlib
python model.py --limits 6 --output results   # solve with at most 6 moves
python demo.py                                 # check the recommended schedule (282)
python audit_results.py                        # check all 50 runs
```

Recommended schedule: `results/schedule_3rooms_6moves.csv`.
