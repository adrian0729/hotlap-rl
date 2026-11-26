# Documentation map

| Where | What it holds |
|---|---|
| [STATUS.md](STATUS.md) | The whole project in order: what was built, every study and its result, and what was left undone. Read this first. |
| [showcase/](showcase/README.md) | The interactive page: the final agent replayed on the 12 held-out circuits against the optimal lap, with the results as charts. |
| [findings/](findings/README.md) | One note per study, indexed by theme, each labelled confirmatory, exploratory, post hoc or pilot. |
| [prereg/](prereg/README.md) | The pre-registrations written during the follow-through: the lockbox protocol (`protocol-v1`), the width round, the specialists, the value-gradient term and the maze audit. |
| [interp/](interp/README.md) | Designs and protocols of the studies of the trained networks: psychophysics, receptive fields, H4R and the costate. |
| [plan/](plan/README.md) | The plans: the first plan, the two-track plan that governed the project, the follow-through plan with its record of decisions, and E0's run plan. |
| [paper/](paper/README.md) | The level-score specification extracted from the curriculum methods' pinned source, and the source notes behind it. |
| [demo/](demo/README.md) | Earlier single-lap exports and figures (the Hockenheim specialist and one development-circuit generalist). |

The LaTeX draft of the planned paper is in [`../paper/`](../paper/README.md). It was not
finished.

## Vocabulary

| Term | Meaning |
|---|---|
| R-dev | The 12 development circuits. They may be used for fitting and tuning. |
| R_TEST, the lockbox | The 12 held-out circuits, evaluated once under `protocol-v1`. |
| E0 | The final agent: five networks, one recipe, five seeds, 1B steps each. |
| Gap | How much slower a lap is than the optimal lap, as a share of the optimal lap time. |
| s-OCP | The minimum-lap-time optimal-control problem, solved in the distance domain. |
| TO-OCP | The optimal-control problem of the agent's own discounted objective on the simulator's own time grid. |
| G, B | Edge-tracking gain (how far the line moves per metre the inside edge moves) and the clearance the line keeps from the inside edge. |
| Costate, λ | The gradient of the optimum's remaining value with respect to the car's state. |
| PVL, MaxMC, learnability | The level scores that the curriculum methods PLR and SFL use. |
| GW-n, CS-n, X-n and similar | Item numbers from the [follow-through plan](plan/follow-through.md), Section 3. |
