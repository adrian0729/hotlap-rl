"""The post hoc margin run (scripts/margin_rtest.py): its test, its reading rule, its
prediction check and its rows, on made-up numbers. Nothing here loads a circuit or a network."""

import importlib
import json
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"


@pytest.fixture(scope="module")
def mr():
    sys.path.insert(0, str(SCRIPTS))
    try:
        yield importlib.import_module("margin_rtest")
    finally:
        sys.path.remove(str(SCRIPTS))


def test_permutation_p_is_exact_for_five_against_five(mr):
    t = mr.permutation_p([11, 12, 12, 11, 11], [4, 10, 8, 8, 6])
    assert t["n_relabellings"] == 252 and t["count_ge"] == 1
    assert t["p_one_sided"] == pytest.approx(1 / 252)
    assert t["mean_diff"] == pytest.approx(4.2)


def test_permutation_p_counts_ties_and_is_one_for_the_worst_split(mr):
    assert mr.permutation_p([1, 1], [1, 1])["p_one_sided"] == 1.0
    assert mr.permutation_p([0, 0, 0], [5, 5, 5])["p_one_sided"] == 1.0
    assert mr.permutation_p([3, 2], [1, 0])["p_one_sided"] == pytest.approx(1 / 6)


def test_the_reading_rule(mr):
    e0 = [6, 10, 8, 10, 7]
    assert mr.reading([11, 12, 11, 10, 11], e0, 0.02) == "the completion gain transfers"
    assert mr.reading([11, 12, 11, 10, 11], e0, 0.06) == "partly"            # p misses
    assert mr.reading([9, 12, 9, 12, 9], e0, 0.04) == "partly"               # median below 10
    assert mr.reading([8, 10, 9, 10, 8], e0, 0.30) == "the completion gain does not transfer"


def test_predictions_hold_on_the_closed_interval(mr):
    preds = [{"id": "a", "interval": [9, 12]}, {"id": "b", "interval": [0.052, 0.068]}]
    out = mr.check_predictions(preds, {"a": 12, "b": 0.0519})
    assert [(p["held"], p["side"]) for p in out] == [(True, "inside"), (False, "below")]
    assert mr.check_predictions(preds[:1], {"a": 13})[0]["side"] == "above"


def lap_record(completed, lap=80.0):
    done = np.asarray(completed, bool)
    return {"completed": done.tolist(), "lap_time_s": [lap if d else None for d in done],
            "crash": (~done).tolist(), "cause": ["" if d else "corridor" for d in done]}


def test_rows_and_summary_follow_the_lockbox_definitions(mr):
    t_ref = {c: {"+0.0": 76.0, "-0.5": 77.0, "+0.5": 75.0} for c in ("A", "B", "C")}
    laps = {"A": lap_record([1] * 10), "B": lap_record([1] * 5 + [0] * 5),
            "C": lap_record([1] * 6 + [0] * 4, lap=83.6)}
    rows = mr.rows_for("n0", laps, t_ref)
    by = {r["circuit"]: r for r in rows}
    assert by["A"]["gap"]["+0.0"] == pytest.approx(80.0 / 76.0 - 1.0)
    assert by["B"]["completion"] == 0.5 and by["B"]["crashes"] == 5
    s = mr.summarise({"n0": rows}, cmin=0.5)["per_subject"]["n0"]
    assert s["circuits_completed"] == 2                       # exactly half does not count
    assert s["laps_completed_share"] == pytest.approx(21 / 30)
    assert s["median_gap"] == pytest.approx(np.median([80.0 / 76.0 - 1.0, 83.6 / 76.0 - 1.0]))
    assert s["median_gap_narrow"] < s["median_gap"] < s["median_gap_wide"]


def test_the_plan_files_agree_with_each_other(mr):
    subs = json.loads(mr.SUBJECTS.read_text())["subjects"]
    assert [s["name"] for s in subs] == [f"gw6-margin-s{k}" for k in range(80, 85)]
    assert all(len(s["sha256"]) == 64 and s["timesteps"] == 999948288 for s in subs)
    preds = json.loads(mr.PREDICTIONS.read_text())
    ids = [p["id"] for p in preds["predictions"]]
    assert ids == ["circuits", "lap_share", "median_gap", "gap_cost", "min_circuits"]
    assert all(p["interval"][0] <= p["value"] <= p["interval"][1] for p in preds["predictions"])
    assert preds["e0_rtest"]["circuits_completed"] == [6, 10, 8, 10, 7]
    assert mr.PLAN.exists()
