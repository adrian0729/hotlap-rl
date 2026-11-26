"""The margin recipe on the 12 held-out circuits (docs/findings/margin-rtest-plan.md): POST HOC.

    uv run python scripts/margin_rtest.py laps --mode dryrun   # R-dev: check against stored evals
    uv run python scripts/margin_rtest.py laps                 # R_TEST, the run itself
    uv run python scripts/margin_rtest.py analyse              # summary.json, once

GW-6's five networks (the 1.4 m training-margin recipe at 1B steps) through the lockbox's own
lap protocol and code, on the 12 R_TEST originals, against the lockbox's stored references.
The lockbox was spent on E0 under ``protocol-v1``; every number here is POST HOC and none
changes ``outputs/lockbox/analysis.json``.

What keeps it honest
- ``scripts/lockbox.py`` is imported unchanged. Its ``clear`` is the only door to circuit
  geometry, so the R_TEST run needs ``tag_gate`` to pass: the metric code in the working tree
  is the code ``protocol-v1`` pins.
- The R_TEST run refuses to start unless the plan, the subjects file, the predictions file and
  this script are committed and that commit is on origin's main. The commit is recorded.
- Outputs are written once and never overwritten. ``laps`` prints no outcome; ``analyse`` takes
  a lock before it reads a lap and runs once.
- ``--mode dryrun`` admits R-dev circuits only and compares each network with the
  ``eval_rdev.json`` its training run stored.

Outputs: ``outputs/posthoc/margin-rtest/laps/<network>/<circuit>.json`` and ``summary.json``
(``outputs/posthoc/margin-rtest-dryrun/`` for the dry run).
"""

import argparse
import itertools
import json
import time
from pathlib import Path

import lockbox as lb  # sets the lockbox run's thread settings on import
import numpy as np

from apexzero.env.adapters import reference_speed
from apexzero.tracks.corners import R_DEV, R_TEST

ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "docs" / "findings"
PLAN = FINDINGS / "margin-rtest-plan.md"
SUBJECTS = FINDINGS / "margin-rtest-subjects.json"
PREDICTIONS = FINDINGS / "margin-rtest-predictions.json"
OUT = {"lockbox": ROOT / "outputs" / "posthoc" / "margin-rtest",
       "dryrun": ROOT / "outputs" / "posthoc" / "margin-rtest-dryrun"}
LOCKBOX = ROOT / "outputs" / "lockbox"
LABEL = ("POST HOC (docs/findings/margin-rtest-plan.md): the lockbox was spent on E0 under "
         "protocol-v1; these numbers decide nothing about E0")
DELTAS = tuple(lb.GAP_TAGS)          # "+0.0", "-0.5", "+0.5"


# ------------------------------------------------------------------------- statistics


def permutation_p(treated, control) -> dict:
    """Exact one-sided permutation test, mean(treated) above mean(control): the share of all
    relabellings whose difference is at least the observed one."""
    a, b = np.asarray(treated, float), np.asarray(control, float)
    pool, n = np.r_[a, b], len(a)
    obs = a.mean() - b.mean()
    total = ge = 0
    for idx in itertools.combinations(range(len(pool)), n):
        mask = np.zeros(len(pool), bool)
        mask[list(idx)] = True
        total += 1
        ge += pool[mask].mean() - pool[~mask].mean() >= obs - 1e-12
    return {"mean_diff": float(obs), "p_one_sided": ge / total, "n_relabellings": total,
            "count_ge": int(ge)}


def reading(margin_counts, e0_counts, p_one_sided: float) -> str:
    """The plan's Section 5 rule, on circuits completed."""
    m, e = np.asarray(margin_counts, float), np.asarray(e0_counts, float)
    if p_one_sided <= 0.05 and np.median(m) >= 10:
        return "the completion gain transfers"
    if m.mean() - e.mean() < 1.0:
        return "the completion gain does not transfer"
    return "partly"


def check_predictions(preds: list[dict], values: dict) -> list[dict]:
    """Each prediction against its value: held when the value lies in the closed interval."""
    out = []
    for p in preds:
        v = values[p["id"]]
        lo, hi = p["interval"]
        out.append({**p, "observed": v, "held": bool(lo <= v <= hi),
                    "side": "inside" if lo <= v <= hi else "below" if v < lo else "above"})
    return out


def rows_for(subject: str, laps: dict, t_ref: dict) -> list[dict]:
    """One network's rows in the lockbox analysis's form: per circuit the completion fraction,
    the run flags, and the gap of the median completed lap against each reference."""
    rows = []
    for circuit, rec in laps.items():
        completed = np.asarray(rec["completed"], bool)
        lt = np.asarray([lb.unclean(x) for x in rec["lap_time_s"]], float)
        med = lb._med(lt[completed]) if completed.any() else float("nan")
        gap = {d: (med / t_ref[circuit][d] - 1.0
                   if np.isfinite(t_ref[circuit][d]) and np.isfinite(med) else float("nan"))
               for d in DELTAS}
        rows.append({"subject": subject, "circuit": circuit, "completion": float(completed.mean()),
                     "completed": completed.tolist(), "n_completed": int(completed.sum()),
                     "median_lap_s": med, "gap": gap,
                     "crashes": int(np.sum(rec["crash"])), "causes": sorted(set(rec["cause"]) - {""})})
    return rows


def summarise(rows_by_subject: dict[str, list[dict]], cmin: float) -> dict:
    per = {s: lb.family_summary(rows, cmin) for s, rows in rows_by_subject.items()}
    keys = ("circuits_completed", "laps_completed_share", "median_gap", "median_gap_narrow",
            "median_gap_wide", "median_gap_crash_inf")
    med = {k: float(np.median([per[s][k] for s in per])) for k in keys}
    return {"per_subject": per, "median_subject": med}


# ------------------------------------------------------------------------- stages


def require_pushed_plan() -> str:
    """HEAD, after checking that the plan's four files are committed as they stand and that
    HEAD is on origin's main."""
    rels = [lb.rel(p) for p in (PLAN, SUBJECTS, PREDICTIONS, Path(__file__).resolve())]
    dirty = lb.git_run("diff", "--quiet", "HEAD", "--", *rels).returncode != 0
    untracked = lb.git_run("ls-files", "--others", "--exclude-standard", "--", *rels).stdout.strip()
    if dirty or untracked:
        raise lb.CheckFailed("commit the plan, the subjects, the predictions and this script "
                             "before the R_TEST run")
    head = lb.git("rev-parse", "HEAD")
    ls = lb.git_run("ls-remote", "origin", "refs/heads/main")
    remote = ls.stdout.split()[0] if ls.returncode == 0 and ls.stdout.strip() else None
    if remote is None or lb.git_run("merge-base", "--is-ancestor", head, remote).returncode != 0:
        raise lb.CheckFailed("HEAD is not on origin's main: push the plan before the R_TEST run")
    return head


def lap_file(mode: str, subject: str, circuit: str) -> Path:
    return OUT[mode] / "laps" / subject / f"{circuit}.json"


def stage_laps(args) -> None:
    mode = args.mode
    plan_commit = require_pushed_plan() if mode == "lockbox" else None
    subs = lb.verify_subjects(json.loads(SUBJECTS.read_text())["subjects"])
    circuits = list(R_TEST if mode == "lockbox" else R_DEV)
    clearance = lb.clear(circuits, mode)
    lp = lb.PROTOCOL["laps"]
    lb.lower_priority()
    for sub in subs:
        todo = [c for c in circuits if not lap_file(mode, sub["name"], c).exists()]
        if not todo:
            continue
        policy, _cfg, _snap = lb.load_subject(sub)
        for c in todo:
            t0 = time.time()
            track = lb.load_variant(c, "original", clearance)
            v_start = float(reference_speed(track)[0]) * lp["start_fraction"]
            ro = lb.rollout_laps(policy, track, v_start, runs=lp["runs"], laps=lp["laps"],
                                 seed=lp["seed"])
            lb.write_json_new(lap_file(mode, sub["name"], c), {
                "label": LABEL, "mode": mode, "subject": sub["name"], "circuit": c,
                "variant": "original", "checkpoint_sha256": sub["sha256"],
                "plan_commit": plan_commit, "protocol_laps": lp, "v_start": v_start,
                "length_m": ro.length, "completed": ro.completed, "lap_time_s": ro.lap_time,
                "s_reached": ro.s_reached, **lb.outcomes(ro),
                "seconds": round(time.time() - t0, 2), "provenance": lb.provenance(t0)})
            print(f"{sub['name']} {c} written", flush=True)       # no outcome is printed
    if mode == "dryrun":
        agreement(subs, circuits)


def agreement(subs, circuits) -> None:
    """Dry run only: each network's R-dev completion against its training run's stored
    evaluation (the same 10-run protocol, on the training box)."""
    same = total = 0
    for sub in subs:
        stored = json.loads((ROOT / Path(sub["checkpoint"]).parents[1] / "eval_rdev.json").read_text())
        mine, theirs = [], []
        for c in circuits:
            rec = json.loads(lap_file("dryrun", sub["name"], c).read_text())
            frac = float(np.mean(rec["completed"]))
            same += abs(frac - stored[c]["completion"]) < 1e-9
            total += 1
            mine.append(frac > 0.5)
            theirs.append(stored[c]["completion"] > 0.5)
        print(f"{sub['name']}: circuits completed {sum(mine)} here, {sum(theirs)} stored; "
              f"same circuits: {mine == theirs}")
    print(f"completion fractions equal to the stored evaluation: {same} of {total}")


def stage_analyse(args) -> None:
    root = OUT["lockbox"]
    out, lock = root / "summary.json", root / "summary.lock"
    if out.exists() or lock.exists():
        raise lb.CheckFailed(f"{lb.rel(out)} or its lock exists: analyse runs once")
    t0 = time.time()
    subs = lb.verify_subjects(json.loads(SUBJECTS.read_text())["subjects"])
    preds = json.loads(PREDICTIONS.read_text())
    missing = [lb.rel(lap_file("lockbox", s["name"], c)) for s in subs for c in R_TEST
               if not lap_file("lockbox", s["name"], c).exists()]
    if missing:
        raise lb.CheckFailed(f"laps are missing: {missing[:3]} ...")
    inputs = {}
    t_ref = {}
    for c in R_TEST:
        t_ref[c] = {}
        for d in DELTAS:
            f = LOCKBOX / "ocp" / f"{c}__w{d}.json"
            r = json.loads(f.read_text())
            inputs[lb.rel(f)] = lb.sha256_file(f)
            t_ref[c][d] = float(r["lap_time_s"]) if r["success"] and lb.shooting_ok(r) else float("nan")
    lb.write_json_new(lock, {"label": LABEL, "taken": time.strftime("%Y-%m-%dT%H:%M:%S")})

    cmin = lb.PROTOCOL["laps"]["completion_min"]
    rows_by, commits = {}, set()
    for s in subs:
        laps = {}
        for c in R_TEST:
            f = lap_file("lockbox", s["name"], c)
            rec = json.loads(f.read_text())
            if rec["checkpoint_sha256"] != s["sha256"] or rec["mode"] != "lockbox":
                raise lb.CheckFailed(f"{lb.rel(f)} is not this subject's R_TEST record")
            inputs[lb.rel(f)] = lb.sha256_file(f)
            commits.add(rec["plan_commit"])
            laps[c] = rec
        rows_by[s["name"]] = rows_for(s["name"], laps, t_ref)
    margin = summarise(rows_by, cmin)

    e0a = json.loads((LOCKBOX / "analysis.json").read_text())
    inputs[lb.rel(LOCKBOX / "analysis.json")] = lb.sha256_file(LOCKBOX / "analysis.json")
    e0_rows = {s: [r for r in e0a["rows"] if r["subject"] == s and r["variant"] == "original"]
               for s in e0a["subjects"]}
    e0 = {"per_subject": {s: e0a["per_subject"][s]["original"] for s in e0a["subjects"]},
          "median_subject": e0a["headline_median_subject"]["original"]}

    m_counts = [margin["per_subject"][s["name"]]["circuits_completed"] for s in subs]
    e_counts = [e0["per_subject"][s]["circuits_completed"] for s in e0a["subjects"]]
    if e_counts != preds["e0_rtest"]["circuits_completed"]:
        raise lb.CheckFailed("E0's counts differ from the ones the plan quotes")
    test = permutation_p(m_counts, e_counts)
    med = margin["median_subject"]
    values = {"circuits": med["circuits_completed"], "lap_share": med["laps_completed_share"],
              "median_gap": med["median_gap"],
              "gap_cost": med["median_gap"] - e0["median_subject"]["median_gap"],
              "min_circuits": float(min(m_counts))}
    h1 = lb.PROTOCOL["stats"]["h1"]
    per_circuit = []
    for c in R_TEST:
        mg = [r["gap"]["+0.0"] for rows in rows_by.values() for r in rows
              if r["circuit"] == c and r["completion"] > cmin]
        eg = [lb.unclean(r["gap"]["+0.0"]) for rows in e0_rows.values() for r in rows
              if r["circuit"] == c and r["completion"] > cmin]
        per_circuit.append({"circuit": c, "margin_networks_completing": len(mg),
                            "e0_networks_completing": len(eg),
                            "margin_median_gap": float(np.median(mg)) if mg else None,
                            "e0_median_gap": float(np.median(eg)) if eg else None})
    both = [p for p in per_circuit if p["margin_median_gap"] is not None
            and p["e0_median_gap"] is not None]
    crashes = sum(r["crashes"] for rows in rows_by.values() for r in rows)
    causes = sorted({c for rows in rows_by.values() for r in rows for c in r["causes"]})
    lb.write_json_new(out, {
        "label": LABEL, "plan": lb.rel(PLAN), "plan_commit": sorted(commits),
        "subjects": [s["name"] for s in subs], "circuits": list(R_TEST),
        "margin": margin, "e0": e0,
        "circuits_completed": {"margin": m_counts, "e0": e_counts, "test": test,
                               "reading": reading(m_counts, e_counts, test["p_one_sided"])},
        "h1_as_written_on_median_margin_network": {
            "laps_completed_share": med["laps_completed_share"], "median_gap": med["median_gap"],
            "laps_ok": bool(med["laps_completed_share"] >= h1["laps_completed_min"]),
            "gap_ok": bool(med["median_gap"] <= h1["median_gap_max"])},
        "predictions": check_predictions(preds["predictions"], values),
        "per_circuit": per_circuit,
        "gap_on_shared_circuits": {
            "n_circuits": len(both),
            "median_of_differences": (float(np.median([p["margin_median_gap"] - p["e0_median_gap"]
                                                       for p in both])) if both else None)},
        "crashes": {"runs": crashes, "of": len(subs) * len(R_TEST) * lb.PROTOCOL["laps"]["runs"],
                    "causes": causes},
        "rows": [r for rows in rows_by.values() for r in rows],
        "provenance": lb.provenance(t0, inputs)})
    print(f"{lb.rel(out)} written")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="stage", required=True)
    laps = sub.add_parser("laps")
    laps.add_argument("--mode", choices=("lockbox", "dryrun"), default="lockbox")
    sub.add_parser("analyse")
    args = ap.parse_args()
    {"laps": stage_laps, "analyse": stage_analyse}[args.stage](args)


if __name__ == "__main__":
    main()
