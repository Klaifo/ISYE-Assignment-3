"""make_pareto.py: plot the workload vs. moves frontier for 3 and 4 rooms.
Usage: python make_pareto.py   (needs results/audit.csv from audit_results.py)"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

a = pd.read_csv("results/audit.csv")

def frontier(df):
    # best penalty for each actual number of moves, keep only nondominated points
    best = df.groupby("moves").agg(penalty=("eval_penalty", "min")).reset_index()
    best["students"] = [df[(df.moves == m) & (df.eval_penalty == p)].students_affected.min()
                        for m, p in zip(best.moves, best.penalty)]
    keep, low = [], float("inf")
    for r in best.sort_values("moves").itertuples():
        if r.penalty < low:
            keep.append(r._asdict()); low = r.penalty
    return pd.DataFrame(keep).drop(columns="Index")

f3, f4 = frontier(a[a.rooms == 3]), frontier(a[a.rooms == 4])
f3.to_csv("results/frontier_3rooms.csv", index=False)
f4.to_csv("results/frontier_4rooms.csv", index=False)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4), dpi=200)
ax1.step(f3.moves, f3.penalty, where="post", color="#C2410C", lw=2, label="3 rooms")
ax1.plot(f3.moves, f3.penalty, "o", color="#C2410C")
ax1.plot(f4.moves, f4.penalty, "s", mfc="none", color="#1D4ED8", ms=9, label="4 rooms")
pick = f3[f3.moves == 6].iloc[0]
ax1.annotate("recommended\n6 moves, 282", (6, pick.penalty), xytext=(8.5, 520),
             arrowprops=dict(arrowstyle="->", color="#333"), fontsize=9)
ax1.annotate("4th room only helps here\n(615 vs 607)", (2, 607), xytext=(4.3, 760),
             arrowprops=dict(arrowstyle="->", color="#333"), fontsize=9)
ax1.set(xlabel="Exam sections moved", ylabel="Total student penalty",
        title="Penalty vs. disruption", ylim=(150, 950))
ax1.legend(frameon=False)

ax2.plot(f3.moves, f3.students, "o-", color="#C2410C")
ax2.axvline(6, color="#999", ls=":")
ax2.set(xlabel="Exam sections moved", ylabel="Students with an exam time change",
        title="Who feels the change", ylim=(0, 380))
for ax in (ax1, ax2):
    ax.set_xticks(range(0, 19, 2))
    ax.spines[["top", "right"]].set_visible(False); ax.grid(alpha=0.2)
fig.tight_layout()
fig.savefig("results/pareto.png")
print(f3.to_string(index=False)); print(f4.to_string(index=False))
