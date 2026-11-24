"""
data.py: load the CSVs into model-ready sets and dicts.

Usage:
    from data import load_data
    d = load_data("data/", include_room4=False)
    d["E"], d["P"], d["A"], ...

Every key is documented in load_data() below.
"""

import pandas as pd

EXTRA_ROOM = "Klaus-2443"  # the optional 4th room


def load_data(path="data/", include_room4=True):
    # ---------- read raw CSVs ----------
    exams    = pd.read_csv(path + "exams.csv")
    periods  = pd.read_csv(path + "periods.csv")
    rooms    = pd.read_csv(path + "rooms.csv")
    avail    = pd.read_csv(path + "room_availability.csv")
    draft    = pd.read_csv(path + "draft_schedule.csv")
    external = pd.read_csv(path + "external_exams.csv")
    enroll   = pd.read_csv(path + "enrollments.csv")

    # drop the extra room everywhere if we're running the 3-room case
    if not include_room4:
        rooms = rooms[rooms["room_id"] != EXTRA_ROOM]
        avail = avail[avail["room_id"] != EXTRA_ROOM]

    # ---------- exams ----------
    E = exams["exam_id"].tolist()                                   # 24 ISyE exams
    course = dict(zip(exams["exam_id"], exams["course_code"]))      # exam -> "ISYE 3133"

    # ---------- rooms ----------
    R = rooms["room_id"].tolist()
    cap = dict(zip(rooms["room_id"], rooms["capacity"]))            # room -> seats

    # ---------- periods ----------
    # every period (needed to place externals in time), in time order
    periods = periods.sort_values(["date", "start_time"]).reset_index(drop=True)
    P_all = periods["period_id"].tolist()
    day   = dict(zip(periods["period_id"], periods["date"]))         # period -> "2026-12-10"
    start = dict(zip(periods["period_id"], periods["start_time"]))   # period -> "14:40"
    end   = dict(zip(periods["period_id"], periods["end_time"]))
    ptype = dict(zip(periods["period_id"], periods["period_type"]))  # regular/reading/conflict

    # allowed (room, period) pairs, only regular periods
    A = {(r, p) for r, p in zip(avail["room_id"], avail["period_id"])
         if ptype[p] == "regular"}
    P = sorted({p for _, p in A}, key=P_all.index)                  # usable ISyE periods

    # ---------- students ----------
    is_isye = enroll["exam_id"].isin(E)
    isye_enroll = enroll[is_isye]
    ext_enroll  = enroll[~is_isye]

    S_e = isye_enroll.groupby("exam_id")["student_id"].apply(set).to_dict()     # exam -> students
    size = {e: len(S_e.get(e, set())) for e in E}                                # exam -> headcount
    S = sorted(enroll["student_id"].unique())                                    # all students
    E_s = isye_enroll.groupby("student_id")["exam_id"].apply(set).to_dict()     # student -> ISyE exams

    # external exams: student -> set of fixed periods they're busy in
    ext_period = dict(zip(external["exam_id"], external["period_id"]))
    ext_s = (ext_enroll.assign(period_id=ext_enroll["exam_id"].map(ext_period))
             .groupby("student_id")["period_id"].apply(set).to_dict())

    # make sure every student has an entry, even if empty
    E_s   = {s: E_s.get(s, set())   for s in S}
    ext_s = {s: ext_s.get(s, set()) for s in S}

    # ---------- draft ----------
    draft_period = dict(zip(draft["exam_id"], draft["period_id"]))  # exam -> period
    draft_room   = dict(zip(draft["exam_id"], draft["room_id"]))    # exam -> room

    return {
        # sets
        "E": E, "P": P, "P_all": P_all, "R": R, "S": S, "A": A,
        # exam info
        "course": course, "size": size, "S_e": S_e,
        # room info
        "cap": cap,
        # period info
        "day": day, "start": start, "end": end, "ptype": ptype,
        # student info
        "E_s": E_s, "ext_s": ext_s,
        # draft
        "draft_period": draft_period, "draft_room": draft_room,
    }


if __name__ == "__main__":
    # quick sanity check: python data.py
    for rooms4 in (False, True):
        d = load_data("data/", include_room4=rooms4)
        print(f"--- include_room4={rooms4} ---")
        print("exams:", len(d["E"]), "| students:", len(d["S"]),
              "| rooms:", len(d["R"]), "| usable periods:", len(d["P"]),
              "| slots:", len(d["A"]))
        print("usable periods:", d["P"])
        print("section sizes:", min(d["size"].values()), "to", max(d["size"].values()))
        print("students with an external:", sum(1 for s in d["S"] if d["ext_s"][s]))
