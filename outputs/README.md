# Committed results

Most experiment outputs are not in git: this folder is ignored, and on the machine that ran
the project it holds tens of gigabytes. What is committed is each study's decisive result
file, the one its finding quotes, with the records that show what a frozen analysis ran on.

## The final agent and the held-out test

| Folder | What it holds | Finding | Written by |
|---|---|---|---|
| `e0/` | The final agent's gate on the development circuits, with its lock and manifest | [e0](../docs/findings/e0.md) | `scripts/e0_gate.py` |
| `lockbox/` | The one evaluation of the 12 held-out circuits under `protocol-v1`: the analysis, its lock, the freeze record and the per-corner table | [lockbox](../docs/findings/lockbox.md) | `scripts/lockbox.py` |
| `lockbox-provenance/` | The optima sealed on the project's first day, compared with the references the lockbox solved again | [lockbox-provenance](../docs/findings/lockbox-provenance.md) | `scripts/lockbox_provenance.py` |
| `posthoc/line-execution/` | The split of the lost time into line and execution, on the held-out and the development circuits: two `split.json` files and the record of each of the 409 solves | [line-execution](../docs/findings/line-execution.md) | `scripts/line_execution.py` |
| `posthoc/margin-rtest/` | The margin recipe's five networks on the held-out circuits, post hoc: the lap records and their summary | [margin-rtest](../docs/findings/margin-rtest.md) | `scripts/margin_rtest.py` |

## Width, margin and locality

| Folder | What it holds | Finding | Written by |
|---|---|---|---|
| `width-report/` | The report on each of the two statistical width models | [width-model](../docs/findings/width-model.md) | `scripts/width_report.py` |
| `gw3/` | The width round's analysis and manifest | [gw3](../docs/findings/gw3.md) | `scripts/gw3_analysis.py` |
| `gw5/`, `gw8/` | The margin rounds: circuits completed and edge clearances | [gw5](../docs/findings/gw5.md), [gw8](../docs/findings/gw8.md) | `scripts/gw5_analysis.py`, `scripts/gw8_analysis.py` |
| `x2x3/` | At real crash corners, how much of a corner-wide edge shift the line follows, and how much of the real, local change | [x2x3](../docs/findings/x2x3.md) | `scripts/x2x3_exploratory.py` |
| `locality-h4r/` | What training on real widths changes in that response, on the H4R networks | [locality-h4r](../docs/findings/locality-h4r.md) | `scripts/locality_h4r_exploratory.py` |

## Studies of the trained networks

| Folder | What it holds | Finding | Written by |
|---|---|---|---|
| `fields/` | Receptive fields, step 2: the decisions and the tag record | [receptive-fields-step2](../docs/findings/receptive-fields-step2.md) | `scripts/fields.py` |
| `h4r/` | H4R: the decisions, the manifest and the tag record | [h4r](../docs/findings/h4r.md) | `scripts/h4r.py` |
| `costate/` | The costate study: the decisions and the tag record | [costate](../docs/findings/costate.md) | `scripts/costate.py` |
| `vg0/`, `vg1/` | The value-gradient term: its overhead and residual checks, then the pilots and the main analysis | [vg1](../docs/findings/vg1.md) | `scripts/vgl.py`, `scripts/vg1_analysis.py` |
| `p4/`, `p4b2/` | Specialist memorisation: the conditions that option A certified, then the build, checks and classification of the five fresh specialists | [p4](../docs/findings/p4.md), [p4-b2](../docs/findings/p4-b2.md) | `scripts/p4_exploratory.py`, `scripts/p4_b2.py` |

## The maze audit

| Folder | What it holds | Finding | Written by |
|---|---|---|---|
| `maze-e5/` | Level scores against exact regret on JaxUED's and SFL's own maze agents: the analysis, its lock, the decisions and the manifest | [maze-e5](../docs/findings/maze-e5.md) | `scripts/maze_e5.py` |

Step 1 of the network studies (psychophysics) has no file here: its outputs are large and stayed
on the machine. Its numbers are in the [finding](../docs/findings/psychophysics-step1.md).
