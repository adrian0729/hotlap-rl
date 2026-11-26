"""The showcase exporter (scripts/showcase.py): packing, the subject rule, the sector snap and
the crash description, on synthetic tracks. Nothing here reads a lockbox file."""

import dataclasses
import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest
from _viz_fixtures import rounded_square, synthetic_ocp

from apexzero.viz import export
from apexzero.viz.sectors import carry_over_split, corner_sectors

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def sc():
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        spec = importlib.util.spec_from_file_location("showcase", REPO / "scripts" / "showcase.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        yield mod
    finally:
        sys.path.remove(str(REPO / "scripts"))


def decode(ints, scale):
    return np.cumsum(ints) / scale


def test_quantised_arrays_round_trip(sc):
    a = np.array([-1234.56, 0.04, 0.05, 987.654, 987.61])
    assert np.allclose(np.array(sc.q(a, 10)) / 10, np.round(a, 1))
    assert np.allclose(decode(sc.dq(a, 10), 10), np.rint(a * 10) / 10)
    assert sc.dq(a, 10)[0] == round(a[0] * 10)          # the first value is absolute


def test_packed_ghost_ends_at_its_lap_time_and_stays_on_its_path(sc):
    track = rounded_square()
    g = export.ocp_ghost(synthetic_ocp(track), track)
    p = sc.pack_ghost(g.t, g.channels)
    assert p["T"] == pytest.approx(g.lap_time, abs=1e-4)
    assert p["n"] == len(p["x"]) == len(p["v"]) == len(p["p"])
    t = np.r_[np.arange(p["n"] - 1) * p["dt"], p["T"]]
    assert np.all(np.diff(t) > 0)
    for k, scale in (("x", 10), ("y", 10), ("s", 10)):
        assert np.allclose(decode(p[k], scale), np.interp(t, g.t, g.channels[k]), atol=0.051)
    assert decode(p["s"], 10)[-1] == pytest.approx(track.length, abs=0.051)
    assert np.allclose(np.array(p["v"]) / 10, np.interp(t, g.t, g.channels["speed"]), atol=0.051)


def test_increasing_removes_ties_and_reversals(sc):
    s = sc.increasing(np.array([0.0, 1.0, 1.0, 0.9, 2.0]))
    assert np.all(np.diff(s) > 0)
    assert s[-1] == pytest.approx(2.0, abs=1e-6)


def test_rollout_run0_is_run_0_of_the_lockbox_batch(sc):
    """The replay must be the registered run, not a look-alike: run 0 of the harness's own
    batch, state for state."""
    import contextlib

    import jax
    import jax.numpy as jnp

    track = rounded_square()

    def policy(obs):                 # steer back to the middle, hold a light throttle
        steer = jnp.clip(-1.5 * obs[:, 204] - 2.0 * obs[:, 205], -1.0, 1.0)
        return jnp.stack([steer, jnp.full(obs.shape[0], 0.15)], axis=1)

    lp = sc.lb.PROTOCOL["laps"]
    ro = sc.rollout_run0(policy, track, v_start=18.0)
    # The harness is a float32 program run as its own process. Inside the whole suite another
    # module may have left this process in float64, so the reference gets the same guard that
    # rollout_run0 carries.
    float32 = getattr(jax, "enable_x64", None)
    with float32(False) if float32 is not None else contextlib.nullcontext():
        ref = sc.lb.rollout_laps(policy, track, 18.0, runs=lp["runs"], laps=lp["laps"],
                                 seed=lp["seed"])
    assert ro.x.shape == (ref.s.shape[0] + 1, 8) and ro.laps == lp["laps"]
    assert (ro.x[0, 1], ro.x[0, 3]) == (0.0, 18.0)               # run 0 starts centred
    for col, arr in ((0, ref.s), (1, ref.n), (3, ref.vx)):
        assert np.array_equal(ro.x[1:, col], arr[:, 0].astype(float))
    assert np.array_equal(ro.alive[1:], ref.alive[:, 0])
    assert np.all(np.abs(ro.action) <= 1.0)


def analysis(counts, gaps, headline_gap=0.05):
    subs = [f"n{i}" for i in range(len(counts))]
    return {"subjects": subs,
            "per_subject": {s: {"original": {"circuits_completed": c, "median_gap": g}}
                            for s, c, g in zip(subs, counts, gaps, strict=True)},
            "headline_median_subject": {"original": {"median_gap": headline_gap}}}


def test_the_subject_is_the_median_network_by_circuits_completed(sc):
    assert sc.pick_subject(analysis([6, 10, 8, 10, 7], [0.051, 0.054, 0.058, 0.052, 0.051])) == "n2"


def test_a_tie_on_circuits_goes_to_the_gap_nearest_the_headline(sc):
    assert sc.pick_subject(analysis([8, 9, 8, 4, 12], [0.070, 0.050, 0.052, 0.050, 0.050])) == "n2"


def test_corner_types_use_the_plan_bands(sc):
    assert [sc.corner_type(v / 3.6) for v in (119.9, 120.0, 200.0, 200.1)] == [
        "slow", "medium", "medium", "fast"]


def test_snapped_sectors_move_a_near_station_boundary_onto_the_station(sc, monkeypatch):
    track = rounded_square()
    L = float(track.length)
    raw = corner_sectors(track)
    station = float(track.s[round(raw[1].s_start / track.ds)])
    # Put the boundary between sectors 0 and 1 a rounding error away from a 2 m station.
    off = [dataclasses.replace(raw[0], s_end=station + 3e-13),
           dataclasses.replace(raw[1], s_start=station + 3e-13), *raw[2:]]
    monkeypatch.setattr(sc, "corner_sectors", lambda _track: off)
    out = sc.snapped_sectors(track)
    assert out[1].s_start == station and out[0].s_end == station
    assert [s.s_start for s in out[2:]] == [s.s_start for s in raw[2:]]      # others untouched
    assert sum(s.s_end - s.s_start for s in out) == pytest.approx(L, abs=1e-9)
    for a, b in zip(out, out[1:] + out[:1], strict=True):
        assert a.s_end % L == pytest.approx(b.s_start % L, abs=1e-9)
    grid = np.r_[track.s, L]
    d = np.linspace(0.0, 1.0, len(grid))
    co = carry_over_split(grid, d, np.zeros(len(grid), bool), out, L, True)
    assert co.measured.sum() == pytest.approx(1.0, abs=1e-12)


def test_crash_facts_name_the_edge_and_whether_it_is_the_inside(sc):
    track = rounded_square()                      # anticlockwise: every corner turns left
    ref = export.ocp_ghost(synthetic_ocp(track), track)
    sectors = corner_sectors(track)
    sec = sectors[1]
    assert sec.angle > 0
    x = np.zeros(8)
    x[0], x[3] = 2 * track.length + sec.s_apex, 30.0          # two laps in, 108 km/h
    half = float(np.interp(sec.s_apex, track.s, track.w_left))
    x[1] = half - 0.5                                          # 0.5 m from the left edge
    f = sc.crash_facts(track, x, sectors, ref, margin=1.0)
    assert (f["side"], f["turn"], f["inside"], f["corner"]) == ("left", "left", True, sec.name)
    assert f["s"] == pytest.approx(sec.s_apex, abs=0.1) and f["speed_kph"] == pytest.approx(108.0)
    x[1] = -(half - 0.5)
    f = sc.crash_facts(track, x, sectors, ref, margin=1.0)
    assert (f["side"], f["inside"]) == ("right", False)
    x[1] = 0.0                                                 # inside the corridor: no edge
    assert sc.crash_facts(track, x, sectors, ref, margin=1.0)["side"] is None
