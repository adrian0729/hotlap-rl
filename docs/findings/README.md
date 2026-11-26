# Findings

Every study has one note here. Notes named `*-plan.md` were committed before the numbers they
plan for existed. The label says how much weight a result carries:

- **Confirmatory:** design, code and decision rules frozen under a git tag before any outcome was
  computed; the deciding analysis ran once.
- **Exploratory:** a plan with expected directions was committed first; nothing was tagged.
- **Post hoc:** run on the held-out circuits after the lockbox was spent.
- **Pilot / descriptive:** decides nothing.

Start with [lockbox.md](lockbox.md) for the headline result, then
[psychophysics-step1.md](psychophysics-step1.md), [x2x3.md](x2x3.md), [gw5.md](gw5.md) and
[margin-rtest.md](margin-rtest.md) for why the agent fails and what helped. [../STATUS.md](../STATUS.md) has the whole story in order.

## The held-out test

| Note | Label | Result |
|---|---|---|
| [lockbox.md](lockbox.md) | Confirmatory, `protocol-v1` | On 12 unseen circuits the median network completes 66.7% of laps at 5.16% off the optimal lap. Both targets (90%, 4%) are missed. |
| [lockbox-provenance.md](lockbox-provenance.md) | Descriptive | Optima sealed on day one agree with the re-solved references to within 0.06%. |
| [line-execution.md](line-execution.md) ([plan](line-execution-plan.md)) | Post hoc | About 30% of the lost time comes back on the car's own line, half within 0.37 m of it. The loss is mostly line choice, in small moves. |
| [e0.md](e0.md) | Run plan tagged, `e0-train-v1` | The final agent, five seeds at 1B steps, completes a median 8 of 12 development circuits against a pass mark of 10. |

## Why the agent crashes

| Note | Label | Result |
|---|---|---|
| [psychophysics-step1.md](psychophysics-step1.md) | Confirmatory, `psychophysics-prereg-v2` | The networks judge ordinary corners like their own optimum. The expected overspeed never appears. Of 160 real-road crashes, 159 leave by the inside edge where it moves. |
| [receptive-fields-step2.md](receptive-fields-step2.md) | Confirmatory, `receptive-fields-prereg-v1` | The line follows 76 to 85% of a corner-wide inside-edge shift, and about 19% of the edge's local move on real crash corners. |
| [locality.md](locality.md) ([plan](locality-plan.md)) | Exploratory | Edge following depends on length scale: about 0.8 corner-wide, 0.3 for an 8 m bump, 0.1 for a 2 m bump. |
| [h4r.md](h4r.md) | Confirmatory, `h4r-prereg-v1` | Training on real width profiles lowers edge tracking and raises inside clearance and completion. It buys margin, not tracking. |
| [locality-h4r.md](locality-h4r.md) ([plan](locality-h4r-plan.md)) | Exploratory | On same-code networks, width training changes only the slow, far-upstream part of the response. |
| [x2x3.md](x2x3.md) ([plan](x2-plan.md)) | Exploratory | At real crash corners the line follows a corner-wide shift at 0.75 and the real local change at 0.07. A 1 m local intrusion crashes 10 of 12 cases; a corner-wide one, none. |
| [interp-leftovers.md](interp-leftovers.md) ([plan](interp-leftovers-plan.md)) | Exploratory | Intervals and common-key checks for the two studies above. |
| [p4.md](p4.md) ([plan](p4-plan.md)), [p4-b2.md](p4-b2.md) | Exploratory; confirmatory, `p4-b2-prereg-v1` | Whether single-circuit specialists memorise their circuit: five fresh networks give five different answers. |
| [generalist-seeds.md](generalist-seeds.md), [dr-pilot-200M-crashes.md](dr-pilot-200M-crashes.md), [dr-pilot-v2-tilt30-crashes.md](dr-pilot-v2-tilt30-crashes.md) | Descriptive | The first generalists: three generator variants do not differ over five seeds, and three circuits defeat all fifteen networks. |

## What helped

| Note | Label | Result |
|---|---|---|
| [width-test.md](width-test.md) ([leave-out plan](width-test-loo-plan.md)) | Exploratory | Real width profiles lift completion from 5.4 to 8.25 of 12 development circuits. |
| [gate-diagnostics.md](gate-diagnostics.md) ([plan](gate-diagnostics-plan.md)) | Exploratory | The shortfall is transfer: 96 to 99% completion on the training distribution against 67% on real circuits. Most crashes are inside-edge exits. |
| [width-model.md](width-model.md) ([bands](width-model-plan.md)) | Exploratory | Two statistical width models that copy no circuit; each misses 3 of 90 pre-set checks. |
| [gw3.md](gw3.md), [gw4.md](gw4.md) | Confirmatory, `gw3-prereg-v1` | A width model fitted on one fold of circuits raises completion on the other fold (9.8 against 4.6), at 1.5 points of lap time. The pre-set rule then gives the final generator copied widths. |
| [gw5.md](gw5.md) ([plan](gw5-plan.md)) | Exploratory | A 1.4 m training-only margin lifts completion from 8.0 to 10.6 at 200M steps and to 11.4 at 1B, for about one point of lap time. Local width bumps and a SimBa network do not help. |
| [gw8.md](gw8.md) ([plan](gw8-plan.md)) | Exploratory | The margin is a dial: 1.2, 1.4 and 1.6 m complete 9.6, 10.8 and 11.4 circuits at rising lap-time cost. |
| [margin-rtest.md](margin-rtest.md) ([plan](margin-rtest-plan.md)) | Post hoc | On the 12 held-out circuits the margin recipe's five networks complete 12, 12, 12, 10 and 11 against the final agent's 6, 10, 8, 10 and 7 (p = 0.012), at 6.3% off optimal against 5.2%. All five predictions held. |

## Critics and the costate

| Note | Label | Result |
|---|---|---|
| [costate.md](costate.md) | Confirmatory, `costate-prereg-v1` | The critic's value gradient does not match the optimal-control costate in any of nine networks, though the values themselves fit. |
| [costate-followups.md](costate-followups.md) ([plan](costate-followups-plan.md)) | Exploratory | The refute holds at the policies' own states and at all 144 training snapshots. The costate is decodable from the network's input. |
| [vg1.md](vg1.md) | Confirmatory, `vg1-prereg-v1` | A value-gradient loss term moves the critic's gradient toward the costate and does not improve driving. |

## Curriculum scores, the planned paper

| Note | Label | Result |
|---|---|---|
| [maze-e5.md](maze-e5.md) | Confirmatory, `maze-e5-prereg-v1` | On mazes with exact regret, none of PVL, MaxMC or learnability ranks regret better than the agent's own return. |
| [maze-audit-pilot.md](maze-audit-pilot.md) | Pilot | The early pilot of the maze audit. |
| [pilot-audit.md](pilot-audit.md) | Pilot, proxy labels | The racing audit's machinery on 13 early checkpoints. The audit itself was not run. |

## Foundations

| Note | Label | Result |
|---|---|---|
| [ppo-verification.md](ppo-verification.md) | Check | The from-scratch PPO matches or beats rejax on CartPole and Pendulum. |
| [braking-gamma.md](braking-gamma.md) | Exercise | In one-dimensional braking, short discount horizons brake late and crash; the environment's 10 s horizon brakes with the optimum. |
| [to-ocp-spike.md](to-ocp-spike.md) | Engineering | The solver for the agent's own 60 s problem: a median 206 CPU-seconds per level, replay exact. |

## Public F1 telemetry

| Note | Label | Result |
|---|---|---|
| [snapping-audit.md](snapping-audit.md) | Descriptive | The public position feed carries no driver-specific racing line across 85 qualifying sessions. |
| [drivers-pilot.md](drivers-pilot.md) | Pilot | Teammate time deltas per corner phase on four 2025 sessions; held-out sector error 11 to 19 ms. |
| [drivers-power.md](drivers-power.md) ([plan](drivers-power-plan.md)) | Exploratory | The reliability gate of the full study would pass with probability 0.08 at best, so it was not run. |
