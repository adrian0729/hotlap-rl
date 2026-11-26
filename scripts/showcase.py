"""Build the data file behind the showcase page (docs/showcase/index.html).

    uv run python scripts/showcase.py                    # all 12 held-out circuits
    uv run python scripts/showcase.py --circuits Spa     # a subset, while developing

The page shows one of E0's five pre-registered networks on the 12 R_TEST circuits, against
the lockbox's own reference laps, with the scoreboard of all five networks and the numbers
behind the page's charts.

Where the numbers come from
- Scoreboard and headline figures: ``outputs/lockbox/analysis.json``, the pre-registered
  ``protocol-v1`` analysis, read as it is.
- The network shown: the median one of the five by circuits completed on the 12 originals
  (ties broken by the median gap closest to the headline), so the choice is a rule, not a
  pick.
- Replays: POST HOC. The lockbox stored each completed lap's path at 2 m stations, but no
  crash trace and no pedal or steering. Each replay is therefore a fresh single rollout of
  the same checkpoint (sha256-checked against ``docs/prereg/protocol-v1-subjects.json``)
  under run 0's protocol: n = 0, v = 0.9 x the reference speed, deterministic action. The
  script stops unless every replay reproduces the stored run 0: the same outcome, and the
  same lap time to 1 ms or the same crash station to 5 m.
- Charts: the committed result files of GW-3, GW-5, GW-6, GW-8, X-2/X-3 and E0's gate.

Lockbox. ``protocol-v1`` was tagged and the lockbox ran once on 29 Oct 2026. Every later
R_TEST run is POST HOC (protocol Section 2), and the page labels these replays so. No new
subject, checkpoint or metric is evaluated here.

Output: ``docs/showcase/data.js``, which sets ``window.APEXZERO``. It holds TUMFTM-derived
track geometry (LGPL-3.0), so it is git-ignored like the other demo exports.
"""

import argparse
import dataclasses
import hashlib
import json
import pickle
import subprocess
import time
from pathlib import Path

import _bootstrap  # noqa: F401  (makes src/ importable)
import numpy as np

from apexzero.env import racing
from apexzero.env.adapters import reference_speed
from apexzero.tracks.corners import R_TEST
from apexzero.tracks.reference import refine_reference
from apexzero.tracks.track import load_tumftm
from apexzero.viz import export
from apexzero.viz.sectors import corner_sectors

ROOT = Path(__file__).resolve().parents[1]
LOCKBOX = ROOT / "outputs" / "lockbox"
SUBJECTS = ROOT / "docs" / "prereg" / "protocol-v1-subjects.json"
OUT = ROOT / "docs" / "showcase" / "data.js"
MARGIN = ROOT / "outputs" / "posthoc" / "margin-rtest"
MARGIN_SUBJECTS = ROOT / "docs" / "findings" / "margin-rtest-subjects.json"

RATE_HZ = 10.0        # replay samples per second (the simulation runs at 20 Hz)
PLOT_DS = 5.0         # m; the distance grid of the speed and gap plots
LAP_TOL_S = 1e-3      # a replayed lap must match the stored run 0 this closely
CRASH_TOL_M = 5.0     # and a replayed crash must end this close to the stored station
SLOW_KPH, FAST_KPH = 120.0, 200.0   # corner types by the optimum's apex speed (plan-v1)

DISPLAY = {"Austin": "Austin", "Budapest": "Budapest", "MexicoCity": "Mexico City",
           "Montreal": "Montreal", "Monza": "Monza", "Sakhir": "Sakhir",
           "SaoPaulo": "São Paulo", "Shanghai": "Shanghai", "Silverstone": "Silverstone",
           "Spa": "Spa", "Spielberg": "Spielberg", "Suzuka": "Suzuka"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head() -> str:
    try:
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                              text=True, check=True, cwd=ROOT).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True, check=True,
                               cwd=ROOT).stdout.strip()
        return head + ("+dirty" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def load_json(path: Path):
    return json.loads(path.read_text())


# ------------------------------------------------------------------------- packing


def q(a, scale: float) -> list[int]:
    """Quantise to integers: value = int / scale."""
    return np.rint(np.asarray(a, float) * scale).astype(np.int64).tolist()


def dq(a, scale: float) -> list[int]:
    """Quantise and delta-code (first value absolute): value = cumsum(ints) / scale."""
    v = np.rint(np.asarray(a, float) * scale).astype(np.int64)
    return np.r_[v[:1], np.diff(v)].tolist()


def pack_ghost(t: np.ndarray, ch: dict[str, np.ndarray]) -> dict:
    """A ghost resampled to RATE_HZ, ending exactly at its last sample's time."""
    t = np.asarray(t, float)
    T = float(t[-1])
    tg = np.arange(0.0, T, 1.0 / RATE_HZ)
    if T - tg[-1] < 1e-3:
        tg = tg[:-1]
    tg = np.r_[tg, T]

    def f(k):
        return np.interp(tg, t, np.asarray(ch[k], float))

    return {"T": round(T, 4), "dt": 1.0 / RATE_HZ, "n": len(tg),
            "x": dq(f("x"), 10), "y": dq(f("y"), 10), "h": dq(f("heading"), 1000),
            "s": dq(f("s"), 10), "v": q(f("speed"), 10),
            "p": q(f("throttle") - f("brake"), 100), "st": q(f("steering"), 1000),
            "g": q(np.clip(f("ellipse_use"), 0.0, 1.5), 100)}


def pack_track(track) -> dict:
    left, right = track.edges()
    return {"n": int(track.n_points), "ds": round(track.ds, 6), "length": round(track.length, 3),
            "lx": dq(left[:, 0], 10), "ly": dq(left[:, 1], 10),
            "rx": dq(right[:, 0], 10), "ry": dq(right[:, 1], 10)}


# ------------------------------------------------------------------------- one circuit


def increasing(s: np.ndarray) -> np.ndarray:
    """s with ties and tiny reversals removed, so it can be interpolated against."""
    s = np.maximum.accumulate(np.asarray(s, float))
    return s + 1e-9 * np.arange(len(s))


def on_grid(s_a, t_a, v_a, ref: export.Ghost, s_end: float) -> dict:
    """Agent and optimum speed, and the agent's time behind the optimum, on PLOT_DS."""
    grid = np.r_[np.arange(0.0, s_end, PLOT_DS), s_end]
    s_a = increasing(s_a)
    d = np.interp(grid, s_a, t_a) - ref.time_at(grid)
    return {"ds": PLOT_DS, "s_end": round(float(s_end), 2),
            "va": q(np.interp(grid, s_a, v_a), 10),
            "vo": q(np.interp(grid, ref.s, ref.channels["speed"]), 10),
            "dt": q(d, 1000)}


def snapped_sectors(track) -> list:
    """``corner_sectors`` with any boundary within 1e-6 m of a grid station moved onto it.

    A boundary is the midpoint of a straight, and on Austin and Spa one lands within 1e-12 m
    of a 2 m station without being equal to it. ``carry_over_split`` then sees an interval
    about 6e-13 m wide whose midpoint lies in no sector and stops ("the sectors do not tile
    the lap"). Snapping the boundary removes that interval and moves nothing by more than
    1e-6 m. It is done here, not in ``apexzero.viz.sectors``, because ``src/apexzero`` is the
    code ``protocol-v1`` pins and stays byte-identical to the tag."""
    secs = corner_sectors(track)
    L = float(track.length)
    grid = np.r_[track.s, L]
    starts = []
    for sec in secs:
        j = int(np.argmin(np.abs(grid - sec.s_start)))
        g = float(grid[j]) if abs(grid[j] - sec.s_start) < 1e-6 else float(sec.s_start)
        starts.append(0.0 if g >= L else g)
    out = []
    for i, sec in enumerate(secs):
        nxt = starts[(i + 1) % len(secs)]
        end = nxt if nxt > starts[i] else nxt + L
        out.append(dataclasses.replace(sec, s_start=starts[i], s_end=end))
    if abs(sum(s.s_end - s.s_start for s in out) - L) > 1e-6:
        raise SystemExit(f"{track.name}: the snapped sectors do not tile the lap")
    return out


def corner_type(v_mps: float) -> str:
    kph = 3.6 * v_mps
    return "slow" if kph < SLOW_KPH else "fast" if kph > FAST_KPH else "medium"


def ref_vmin(ref: export.Ghost, s0: float, s1: float, L: float) -> float:
    """The optimum's minimum speed over [s0, s1] (s1 may exceed L for the wrapping sector)."""
    s, v = ref.s, ref.channels["speed"]
    inside = (s >= s0) & (s <= s1) if s1 <= L else (s >= s0) | (s <= s1 - L)
    return float(v[inside].min()) if inside.any() else float("nan")


def crash_ghost(ro, track):
    """The run's last lap up to and including the terminating step, re-zeroed at that lap's
    start line. ``policy_ghost`` drops the terminating step; here it is the point."""
    L = float(track.length)
    k = int(np.nonzero(~ro.alive)[0][0])            # the state after the terminating step
    ch = export.state_channels(track, ro.x[:k + 1], ro.params, cmd=ro.action[:k + 1])
    t = np.asarray(ro.t[:k + 1], float)
    lap = int(ch["s"][k - 1] // L) + 1
    start = (lap - 1) * L
    if lap > 1:                                     # interpolate the start-line crossing
        j = int(np.nonzero(ch["s"] >= start)[0][0])
        w = (start - ch["s"][j - 1]) / max(ch["s"][j] - ch["s"][j - 1], 1e-12)
        cut = {name: np.r_[(1 - w) * a[j - 1] + w * a[j], a[j:]] for name, a in ch.items()}
        t = np.r_[(1 - w) * t[j - 1] + w * t[j], t[j:]]
        ch = cut
    t = t - t[0]
    ch["s"] = ch["s"] - start
    return t, ch, lap, ro.x[k]


def crash_facts(track, x_term, sectors, ref, margin: float) -> dict:
    """Where the run ended: station, edge, whether that edge is the inside of the corner."""
    L = float(track.length)
    s_c = float(x_term[0] % L)
    n_c = float(x_term[1])
    grid = np.r_[track.s, L]
    wl = float(np.interp(s_c, grid, np.r_[track.w_left, track.w_left[0]]))
    wr = float(np.interp(s_c, grid, np.r_[track.w_right, track.w_right[0]]))
    side = "left" if n_c > wl - margin else "right" if n_c < -(wr - margin) else None
    sec = next((x for x in sectors if x.s_start <= s_c < x.s_end
                or (x.s_end > L and s_c < x.s_end - L)), sectors[-1])
    out = {"s": round(s_c, 1), "speed_kph": round(3.6 * float(np.hypot(x_term[3], x_term[4])), 1),
           "side": side, "corner": sec.name,
           "r_min": round(float(sec.r_min), 1) if np.isfinite(sec.r_min) else None,
           "turn": "left" if sec.angle > 0 else "right",
           "inside": (side == ("left" if sec.angle > 0 else "right")) if side else None,
           "corner_type": corner_type(ref_vmin(ref, sec.s_start, sec.s_end, L))}
    return out


def replay(circuit: str, policy, start_fraction: float, stored: dict) -> dict:
    """One circuit: geometry, the optimum, the network's run, and how they compare."""
    track = refine_reference(load_tumftm(ROOT / "data" / "tracks" / "tumftm" / f"{circuit}.csv"))
    if track.name != circuit:
        raise SystemExit(f"{circuit}: the track is named {track.name}")
    L = float(track.length)
    with open(LOCKBOX / "ocp" / f"{circuit}__w+0.0.pkl", "rb") as fh:
        res = pickle.load(fh)
    ref = export.ocp_ghost(res, track, rate_hz=20.0, unsealed=True)
    sectors = snapped_sectors(track)
    v0 = float(reference_speed(track)[0]) * start_fraction
    if abs(v0 - stored["v_start"]) > 1e-9 * max(v0, 1.0):
        raise SystemExit(f"{circuit}: start speed {v0} differs from the lockbox's "
                         f"{stored['v_start']}")
    ro = export.rollout_policy(policy, track, v0, laps=2, unsealed=True)
    completed = bool(ro.alive.all() and ro.x[:, 0].max() >= 2 * L)
    if completed != bool(stored["completed"][0]):
        raise SystemExit(f"{circuit}: the replay's outcome (completed={completed}) differs "
                         "from the lockbox's run 0")

    out = {"id": circuit, "name": DISPLAY[circuit], "track": pack_track(track),
           "t_opt": round(float(ref.lap_time), 4), "opt": pack_ghost(ref.t, ref.channels),
           "completed": completed}
    if completed:
        g = export.policy_ghost(ro, track, badge="POST HOC", unsealed=True)
        d_lap = abs(g.lap_time - float(stored["lap_time_s"][0]))
        if d_lap > LAP_TOL_S:
            raise SystemExit(f"{circuit}: the replayed lap differs from the lockbox's run 0 "
                             f"by {d_lap:.2e} s")
        doc = export.build_document(track, [g, ref], reference="ocp", sectors=sectors,
                                    unsealed=True)
        comp = doc["comparisons"][0]
        charged, sp = comp["sector_split"]["charged_s"], comp["sector_speed"]
        out.update(
            agent=pack_ghost(g.t, g.channels), t_agent=round(float(g.lap_time), 4),
            gap=round(float(g.lap_time / ref.lap_time - 1.0), 6),
            plot=on_grid(g.s, g.t, g.channels["speed"], ref, L),
            parity={"lap_abs_diff_s": float(d_lap)},
            corners=[{"name": s.name, "s0": round(s.s_start, 1), "s1": round(s.s_end, 1),
                      "apex": round(s.s_apex, 1), "lost": round(float(charged[i]), 3),
                      "va": round(3.6 * sp["vmin_mps"][i], 1),
                      "vo": round(3.6 * sp["ref_vmin_mps"][i], 1),
                      "type": corner_type(sp["ref_vmin_mps"][i])}
                     for i, s in enumerate(sectors)])
    else:
        t, ch, lap, x_term = crash_ghost(ro, track)
        facts = crash_facts(track, x_term, sectors, ref, float(racing.EnvParams().edge_margin))
        d_s = abs(facts["s"] - float(stored["term_s"][0]) % L)
        d_s = min(d_s, L - d_s)
        if lap != int(stored["term_lap"][0]) or d_s > CRASH_TOL_M:
            raise SystemExit(f"{circuit}: the replay ends on lap {lap} at {facts['s']:.0f} m, "
                             f"the lockbox's run 0 on lap {stored['term_lap'][0]} at "
                             f"{float(stored['term_s'][0]) % L:.0f} m")
        facts.update(lap=lap, cause=stored["cause"][0], t=round(float(t[-1]), 3))
        out.update(
            agent=pack_ghost(t, ch), crash=facts,
            plot=on_grid(ch["s"], t, ch["speed"], ref, float(ch["s"][-1])),
            parity={"crash_abs_diff_m": float(d_s)},
            corners=[{"name": s.name, "s0": round(s.s_start, 1), "s1": round(s.s_end, 1),
                      "apex": round(s.s_apex, 1),
                      "vo": round(3.6 * ref_vmin(ref, s.s_start, s.s_end, L), 1),
                      "type": corner_type(ref_vmin(ref, s.s_start, s.s_end, L))}
                     for s in sectors])
    return out


# ------------------------------------------------------------------------- tables


def pick_median(counts: dict, gaps: dict, head_gap: float) -> str:
    """The median network by circuits completed; ties go to the one whose median gap is
    closest to the headline's, then to the first name."""
    med = float(np.median(list(counts.values())))
    return min(counts, key=lambda s: (abs(counts[s] - med), abs(gaps[s] - head_gap), s))


def pick_subject(analysis: dict) -> str:
    """E0's network for the replays, from the pre-registered analysis."""
    per = {s: analysis["per_subject"][s]["original"] for s in analysis["subjects"]}
    return pick_median({s: per[s]["circuits_completed"] for s in per},
                       {s: per[s]["median_gap"] for s in per},
                       analysis["headline_median_subject"]["original"]["median_gap"])


def board(subs: list[str], rows: list[dict], circuits: list[str]) -> list[dict]:
    """Every network on every circuit, from rows in the lockbox analysis's form."""
    out = []
    for c in circuits:
        rs = {r["subject"]: r for r in rows if r["circuit"] == c}
        nets = []
        for s in subs:
            done = bool(rs[s]["completion"] > 0.5)
            gap = rs[s]["gap"]["+0.0"]
            nets.append({"done": done, "laps": int(rs[s]["n_completed"]),
                         "gap": round(float(gap), 6) if done and gap is not None else None})
        gaps = [n["gap"] for n in nets if n["gap"] is not None]
        out.append({"id": c, "name": DISPLAY[c], "nets": nets,
                    "n_done": sum(n["done"] for n in nets),
                    "median_gap": round(float(np.median(gaps)), 6) if gaps else None})
    return out


def scoreboard(analysis: dict) -> dict:
    """E0 on the originals, straight from the pre-registered analysis."""
    subs = list(analysis["subjects"])
    rows = [r for r in analysis["rows"] if r["variant"] == "original"]
    head = analysis["headline_median_subject"]
    h1 = head["h1_as_written_on_median_subject"]
    return {"subjects": subs, "circuits": board(subs, rows, list(analysis["circuits"])),
            "per_subject": {s: {k: analysis["per_subject"][s]["original"][k] for k in
                                ("circuits_completed", "laps_completed_share", "median_gap")}
                            for s in subs},
            "headline": {"circuits_completed": head["original"]["circuits_completed"],
                         "laps_completed_share": h1["laps_completed_share"],
                         "median_gap": h1["median_gap"], "holds": h1["holds"],
                         "target_laps": 0.90, "target_gap": 0.04},
            "source": "outputs/lockbox/analysis.json (protocol-v1, pre-registered)"}


def margin_block(circuits: list[str], start_fraction: float) -> dict | None:
    """The post hoc margin run, if it exists: its median network's replays, its scoreboard
    and its summary (docs/findings/margin-rtest.md). None before that run."""
    if not (MARGIN / "summary.json").exists():
        return None
    summary = load_json(MARGIN / "summary.json")
    per = summary["margin"]["per_subject"]
    name = pick_median({s: per[s]["circuits_completed"] for s in per},
                       {s: per[s]["median_gap"] for s in per},
                       summary["margin"]["median_subject"]["median_gap"])
    sub = next(s for s in load_json(MARGIN_SUBJECTS)["subjects"] if s["name"] == name)
    ckpt = ROOT / sub["checkpoint"]
    if sha256(ckpt) != sub["sha256"]:
        raise SystemExit(f"{ckpt} is not the checkpoint the margin plan pinned")
    policy = export.load_policy(ckpt)
    runs = {}
    for c in circuits:
        t1 = time.time()
        stored = load_json(MARGIN / "laps" / name / f"{c}.json")
        if stored["checkpoint_sha256"] != sub["sha256"]:
            raise SystemExit(f"{c}: the stored margin laps are for another checkpoint")
        rep = replay(c, policy, start_fraction, stored)
        runs[c] = {k: v for k, v in rep.items() if k not in ("track", "opt")}
        what = f"lap {rep['t_agent']:.3f} s" if rep["completed"] else "crash"
        print(f"margin {c:12s} {what}  parity {rep['parity']}  [{time.time() - t1:.1f} s]",
              flush=True)
    med, e0 = summary["margin"]["median_subject"], summary["e0"]["median_subject"]
    return {
        "label": "POST HOC (docs/findings/margin-rtest.md)",
        "subject": {"name": name, "timesteps": sub["timesteps"], "sha256": sub["sha256"],
                    "rule": "the median network of the five by circuits completed"},
        "runs": runs,
        "scoreboard": {"subjects": summary["subjects"],
                       "circuits": board(summary["subjects"], summary["rows"], circuits)},
        "result": {
            "circuits": summary["circuits_completed"],
            "median": {k: med[k] for k in ("circuits_completed", "laps_completed_share",
                                           "median_gap")},
            "e0_median": {k: e0[k] for k in ("circuits_completed", "laps_completed_share",
                                             "median_gap")},
            "h1": summary["h1_as_written_on_median_margin_network"],
            "predictions": [{k: p[k] for k in ("id", "value", "interval", "observed", "held")}
                            for p in summary["predictions"]],
            "plan_commit": summary["plan_commit"]},
        "source": "outputs/posthoc/margin-rtest/summary.json",
    }


def story() -> dict:
    """The numbers behind the page's charts, each from a committed result file."""
    gw3 = load_json(ROOT / "outputs" / "gw3" / "analysis.json")
    gw5 = load_json(ROOT / "outputs" / "gw5" / "completion.json")
    gw5e = load_json(ROOT / "outputs" / "gw5" / "edges.json")
    gw6 = load_json(ROOT / "outputs" / "gw5" / "gw6.json")
    gw8 = load_json(ROOT / "outputs" / "gw8" / "completion.json")
    gw8e = load_json(ROOT / "outputs" / "gw8" / "edges.json")
    x23 = load_json(ROOT / "outputs" / "x2x3" / "results.json")
    gate = load_json(ROOT / "outputs" / "e0" / "gate.json")

    def clearance(edges: dict, prefix: str) -> list[float]:
        return [round(float(v["base_c_min"]), 3) for k, v in sorted(edges["networks"].items())
                if k.startswith(prefix)]

    base = gw3["descriptive"]["counts"]["v1/base"]["all_12"]["per_seed"]
    ladder = [
        {"key": "default", "label": "Default generator", "steps": "200M",
         "circuits": [int(base[k]) for k in sorted(base)],
         "source": "GW-3, v1 baseline, seeds 20-29"},
        {"key": "widths", "label": "Real width profiles", "steps": "200M",
         "circuits": gw5["arms"]["ctrl"]["circuits"], "source": "GW-5 control, seeds 70-74"},
        {"key": "e0", "label": "Same recipe, 1B steps (E0, the final agent)", "steps": "1B",
         "circuits": gate["counts"], "source": "E0 gate, seeds 50-54"},
        {"key": "margin", "label": "Plus a 1.4 m training margin", "steps": "200M",
         "circuits": gw5["arms"]["margin"]["circuits"], "source": "GW-5 margin, seeds 70-74"},
        {"key": "margin1b", "label": "Training margin, 1B steps", "steps": "1B",
         "circuits": gw6["gw6_circuits"], "source": "GW-6, seeds 80-84"},
    ]
    dial = [{"margin_m": float(m), "circuits": gw8["arms"][m]["circuits"],
             "gap": [round(float(g), 5) for g in gw8["arms"][m]["median_gaps"]],
             "clearance_m": clearance(gw8e, f"gw8-m{m}-")} for m in ("1.2", "1.4", "1.6")]
    ctrl = sorted(k for k in gw5["runs"] if k.startswith("gw5-ctrl-"))
    dial_ref = {"margin_m": 1.0, "circuits": [int(gw5["runs"][k]["circuits"]) for k in ctrl],
                "gap": [round(float(gw5["runs"][k]["median_gap"]), 5) for k in ctrl],
                "clearance_m": clearance(gw5e, "gw5-ctrl-"),
                "note": "GW-5's control: an earlier round, other seeds and another box"}
    if dial_ref["circuits"] != gw5["arms"]["ctrl"]["circuits"]:
        raise SystemExit("GW-5's control runs are not in the arm's seed order")
    prof = x23["x2"]["profiles"]["L_per_e"]
    scale = [{"width_m": w, "follow": round(float(prof[f"sigma_b={w}"]["median"]), 4)}
             for w in (2, 4, 8, 16, 32, 64)]
    x3 = x23["x3"]
    return {
        "gate": {"pass_mark": gate["threshold"]["pass_if_median_at_least"], "of": 12},
        "ladder": ladder,
        "ladder_gap": {"e0": round(float(gw6["gap"]["e0_mean_median_gap"]), 5),
                       "margin1b": round(float(gw6["gap"]["gw6_mean_median_gap"]), 5),
                       "widths": round(float(gw5["arms"]["ctrl"]["mean_median_gap"]), 5),
                       "margin": round(float(gw5["arms"]["margin"]["mean_median_gap"]), 5)},
        "others": {"bumps": gw5["arms"]["bumps"]["circuits"],
                   "simba": gw5["arms"]["simba"]["circuits"],
                   "clearance_ctrl_m": clearance(gw5e, "gw5-ctrl-"),
                   "clearance_margin_m": clearance(gw5e, "gw5-margin-"),
                   "clearance_simba_m": clearance(gw5e, "gw5-simba-")},
        "dial": dial,
        "dial_ref": dial_ref,
        "follow": {"by_width": scale,
                   "corner_wide": round(float(x23["x2"]["reading"]["T_median_trapezoid_G"]), 4),
                   "real_change": round(float(x23["x2"]["L_per_e_real"]["median"]), 4),
                   "optimum": 1.0, "unit_phases": 12,
                   "crash_local_1m": int(x3["sigma_b=4"]["by_amplitude"]["-1"]["n_crashed"]),
                   "crash_wide_1m": int(x3["trapezoid"]["by_amplitude"]["-1"]["n_crashed"])},
        "sources": ["outputs/gw3/analysis.json", "outputs/gw5/completion.json",
                    "outputs/gw5/edges.json", "outputs/gw5/gw6.json",
                    "outputs/gw8/completion.json", "outputs/gw8/edges.json",
                    "outputs/x2x3/results.json", "outputs/e0/gate.json"],
    }


# ------------------------------------------------------------------------- main


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--circuits", nargs="*", default=list(R_TEST))
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    bad = [c for c in args.circuits if c not in R_TEST]
    if bad:
        raise SystemExit(f"not R_TEST circuits: {bad}")

    t0 = time.time()
    analysis = load_json(LOCKBOX / "analysis.json")
    freeze = load_json(LOCKBOX / "freeze.json")
    start_fraction = float(freeze["protocol"]["laps"]["start_fraction"])
    name = pick_subject(analysis)
    sub = next(s for s in load_json(SUBJECTS)["subjects"] if s["name"] == name)
    ckpt = ROOT / sub["checkpoint"]
    if sha256(ckpt) != sub["sha256"]:
        raise SystemExit(f"{ckpt} is not the checkpoint protocol-v1 registered")
    policy = export.load_policy(ckpt)

    circuits = []
    for c in args.circuits:
        t1 = time.time()
        stored = load_json(LOCKBOX / "laps" / name / f"{c}.json")
        if stored["checkpoint_sha256"] != sub["sha256"]:
            raise SystemExit(f"{c}: the stored laps are for another checkpoint")
        rep = replay(c, policy, start_fraction, stored)
        circuits.append(rep)
        what = (f"lap {rep['t_agent']:.3f} s, gap {rep['gap']:+.2%}" if rep["completed"]
                else f"ends on lap {rep['crash']['lap']} at {rep['crash']['s']:.0f} m "
                     f"({rep['crash']['corner']}, {rep['crash']['side']} edge, "
                     f"inside={rep['crash']['inside']})")
        print(f"{c:12s} {what}  parity {rep['parity']}  [{time.time() - t1:.1f} s]", flush=True)

    doc = {
        "subject": {"name": name, "timesteps": sub["timesteps"], "sha256": sub["sha256"],
                    "rule": "the median network of the five by circuits completed"},
        "circuits": circuits,
        "scoreboard": scoreboard(analysis),
        "margin": margin_block(args.circuits, start_fraction),
        "story": story(),
        "provenance": {"script": "scripts/showcase.py", "git_head": git_head(),
                       "lockbox_freeze_id": analysis["freeze_id"],
                       "replays": "POST HOC single rollouts that reproduce the lockbox's run 0",
                       "geometry": "TUMFTM racetrack-database (LGPL-3.0)",
                       "built": time.strftime("%Y-%m-%d")},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("window.APEXZERO = " + json.dumps(doc, separators=(",", ":")) + ";\n")
    print(f"{out}  {out.stat().st_size / 1e6:.2f} MB  [{time.time() - t0:.0f} s]")


if __name__ == "__main__":
    main()
