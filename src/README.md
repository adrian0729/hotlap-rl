# Source

One package, `apexzero`. Every file in it is pinned by the tag `protocol-v1` and has not
changed since the held-out test, which is why this note sits beside the package and not
inside it. The runnable entry points are in [`scripts/`](../scripts/README.md).

## The car, the tracks and the optimum

| Package | What it holds |
|---|---|
| `vehicle/` | The car. `dynamics.py` is the single-track model, written once; `ops.py` compiles it for JAX and for CasADi; `sim.py` integrates it on a track; `params.py` holds the F1-style parameters |
| `tracks/` | Track geometry on an arc-length grid, spline lookups, reference lines, corner segmentation, the procedural generator and its width models |
| `ocp/` | Optimal control: the minimum-lap-time problem (`min_time.py`), the agent's own problem on its training window (`window.py`), replay in the simulator, and the labels built on them |
| `oracle/` | A quasi-steady-state lap-time estimate |
| `learn/` | The one-dimensional braking problem, solved by Pontryagin and by value iteration |

## Training and evaluation

| Package | What it holds |
|---|---|
| `env/` | `racing.py` defines what the network observes, its reward and when a run ends; `adapters.py` wraps it for fixed tracks and for generated ones |
| `agents/` | `ppo.py` is PPO written from scratch; `checkpoints.py` saves training snapshots |
| `eval/` | Timed laps with a deterministic policy |
| `ued/` | Racing versions of the curriculum methods PLR and SFL, and their trainer |

## Studies of the trained networks

| Package | What it holds |
|---|---|
| `interp/` | Step 1, psychophysics: stimuli, the rollout harness, answer keys, measures and the pre-registered analysis |
| `fields/` | Step 2, receptive fields: perturbations, corner outcomes, the optimum's and the network's fields, gates and analysis |
| `costate/` | The costate study: targets from the optimum, the critic's and the policy's own estimates, probes, nulls and analysis |

`fields/prereg.json` and `costate/prereg.json` are the pre-registration records those two
studies froze.

## Audits, data and drawing

| Package | What it holds |
|---|---|
| `audit/` | The curriculum methods' level scores and their fidelity against regret |
| `maze/` | The maze audit: exact regret on JaxUED mazes and the statistics of maze E5 |
| `data/` | The OpenF1 archiver and the snapping audit of the public position feed |
| `drivers/` | The teammate-timing pipeline on OpenF1 qualifying sessions |
| `viz/` | Trajectory export, figures, the frame renderer and the earlier viewer |

`compat.py` holds one shim, so that the vendored JaxUED code runs on a current JAX.
