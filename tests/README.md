# Tests

2,088 tests in 92 files. Run them from the repository root:

```bash
uv run pytest                       # everything
uv run pytest tests/test_ppo.py     # one file
uv run pytest -k lockbox            # by name
uv run pytest --durations=15        # and list the slowest
```

On the machine that holds the project's checkpoints and outputs, the whole suite takes about
an hour. The last run, on 26 November 2026, had 2,080 passed and 8 skipped in 54 minutes.
On a fresh clone, tests that need files outside git are written to skip and to say why: the
circuits (`scripts/fetch_tracks.py`), trained checkpoints under `runs/`, or an earlier study's
uncommitted outputs.

Files are named after what they check.

| Files | What they check |
|---|---|
| `test_dynamics`, `test_skidpad`, `test_qss_distance` | The car model and the quasi-steady-state oracle |
| `test_tracks`, `test_generator`, `test_reexpress`, `test_real_widths`, `test_stat_widths`, `test_width_*` | Track geometry, the procedural generator and its width models |
| `test_ocp`, `test_window_ocp`, `test_labels`, `test_levels` | Optimal control, and the labels and levels built on it |
| `test_env`, `test_ppo`, `test_value_gradient`, `test_train_ued`, `test_ued_*` | The environment, PPO, the value-gradient term and the racing curricula |
| `test_interp_*` | Psychophysics, step 1 |
| `test_fields_*`, `test_h4r`, `test_locality` | Receptive fields, step 2, and what followed from it |
| `test_costate_*`, `test_vg1` | The costate study and the value-gradient round |
| `test_p4_*`, `test_gate_diagnostics`, `test_gw3_analysis` | The specialists, the gate diagnostics and the width round |
| `test_e0`, `test_lockbox`, `test_margin_rtest` | The final agent, the held-out test and the margin recipe's later run |
| `test_audit`, `test_estimators`, `test_fidelity`, `test_pilot_audit`, `test_maze_*` | Level scores and the maze audit |
| `test_openf1`, `test_drivers_*` | The OpenF1 archiver and the drivers pipeline |
| `test_viz_*`, `test_showcase` | Trajectory export, figures, rendering and the showcase's data |
| `test_gpu_round`, `test_dashboard` | The GPU round runner and the terminal dashboard |

`_viz_fixtures.py` holds the synthetic tracks that the export and showcase tests share.

Several tests rehearse a frozen study's stages on stand-in data. Once that study's tag exists
they skip the stages that refuse to run after it.
