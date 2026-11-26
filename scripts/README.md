# Scripts

Every script is run from the repository root with `uv run python scripts/<name>.py` and says
what it does in its docstring (`--help` prints it). They are kept in one flat folder on purpose:
the findings and the pre-registrations cite these paths, and several frozen studies hash them.

`_bootstrap.py` is imported first by every script so that `import apexzero` works without the
editable install.

## Data and physics

| Script | What it does |
|---|---|
| `fetch_tracks.py` | Fetch the TUMFTM circuit centrelines (LGPL-3.0) into `data/tracks/tumftm/`. |
| `fetch_openf1.py`, `fetch_jolpica.py` | Archive 2023-26 qualifying sessions and official results. |
| `run_audit.py` | The snapping audit of the public position feed. |
| `bench_sim.py` | Simulator throughput against batch size. |
| `braking_study.py` | One-dimensional braking: Pontryagin against value iteration. |
| `solve_all_ocp.py` | Minimum-lap-time optimum on the development circuits, checked against the simulator. |
| `spike_to_ocp.py` | Speed and replay of the solver for the agent's own 60 s problem. |

## Training and evaluation

| Script | What it does |
|---|---|
| `verify_ppo.py` | Check the from-scratch PPO against rejax. |
| `train.py` | Train on one or more fixed tracks (the Hockenheim specialists). |
| `train_dr.py` | Train a generalist on generated strips. This is E0's trainer. |
| `gw5_train.py` | `train_dr.py` with the training margin and the local width bumps. |
| `train_ued.py` | One arm of the racing curriculum comparison (PLR, SFL, DR on a labelled pool). |
| `eval_rdev.py` | Timed laps on the development circuits for any saved checkpoint. |
| `diagnose_crashes.py` | Where and why a policy crashes, per development circuit. |
| `label_levels.py` | Optimal-return labels per level for the planned paper. |

## GPU rounds

| Script | What it does |
|---|---|
| `gpu_setup.sh`, `gpu_sync.sh` | Set a rented box up and move development data only. |
| `gpu_round.sh`, `round_manifest.py` | Run one round from its run list on every GPU of a box, and check the result against its tag. |
| `*_runs.py` (`e0`, `gw3`, `gw5`, `gw6`, `gw8`, `p4b2`, `vg1`, `maze_e5`) | The run list of each round. |
| `gpu_queue_*.sh`, `queue_overnight.sh` | Queues of the earlier rounds. |
| `dashboard.py` | A terminal dashboard of everything running. |

## Studies

Each row is one study in [docs/findings](../docs/findings/README.md).

| Script | Study |
|---|---|
| `psychophysics.py`, `mirror_gate_rerun.py`, `p5_layout_check.py` | Network psychophysics, step 1. |
| `fields.py`, `fields_exploratory_h4.py`, `interp_leftovers.py` | Receptive fields, step 2, and its leftovers. |
| `h4r.py` | H4R, the width-training test on 20 fresh networks. |
| `locality_exploratory.py`, `locality_h4r_exploratory.py`, `x2x3_exploratory.py` | Locality of edge following. |
| `costate.py`, `costate_exploratory.py` | The costate study and its follow-ups. |
| `vgl.py`, `vg1_analysis.py`, `vg1_c1.py`, `vg1_snapshots.py` | The value-gradient term. |
| `p4_exploratory.py`, `p4_percorner_descriptive.py`, `p4_b2.py` | Specialist memorisation. |
| `gate_diagnostics.py`, `width_report.py`, `width_loo_analysis.py` | Gate diagnostics and width models. |
| `gw3_analysis.py`, `gw3_power.py`, `gw5_analysis.py`, `gw8_analysis.py`, `e0_gate.py` | The width round, the margin rounds and the final agent's gate. |
| `lockbox.py`, `lb1_predictions.py`, `lockbox_provenance.py`, `line_execution.py` | The held-out test and what was computed from it afterwards. |
| `margin_rtest.py` | The margin recipe's five networks on the held-out circuits, post hoc. |
| `maze_audit.py`, `maze_e5.py`, `maze_e5_dryrun.py`, `run_jaxued_maze.py`, `run_sfl_maze.py`, `pilot_audit.py` | The curriculum-score audits. |
| `drivers_pilot.py`, `drivers_report.py`, `drivers_power.py`, `drivers_power_report.py` | The drivers study. |

## Demo

| Script | What it does |
|---|---|
| `showcase.py` | Build the data behind the [showcase page](../docs/showcase/README.md). |
| `showcase_stills.py` | Render the README's stills from that page. |
| `export_demo.py`, `render_demo.py` | The earlier single-lap exports, figures and clips in `docs/demo/`. |

`scripts/lockbox.py` and `scripts/_bootstrap.py` are part of the code that `protocol-v1` pins,
together with `src/apexzero`, `uv.lock` and `pyproject.toml`. They are unchanged since that tag.
