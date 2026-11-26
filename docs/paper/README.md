# Notes for the planned paper

The paper was to audit the level scores that curriculum methods use, against exact regret.
It was not finished. Its LaTeX draft is in [`../../paper/`](../../paper/README.md).

| Document | What it is |
|---|---|
| [score-spec.md](score-spec.md) | The implementation spec of the level-score audit: the `audit-v1` scorer and the racing versions of PLR and SFL |
| [sources-jaxued.md](sources-jaxued.md) | How JaxUED computes its PVL and MaxMC scores, and how its level buffer and maze environment work |
| [sources-sfl.md](sources-sfl.md) | How SFL (Rutherford et al. 2024) computes learnability and samples levels |
| [sources-recent.md](sources-recent.md) | Exact definitions of more recent level scores |

The part of the audit that was run is the maze one: [maze E5](../findings/maze-e5.md).
