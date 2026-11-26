# Paper draft (not finished)

*Regret, Measured: Auditing Curriculum Level Scores Against Optimal Control.* A first draft of
18 Oct 2026, last touched on 25 Oct 2026. The project was wrapped up in November 2026 without
the paper, so this folder is kept as a record.

What is usable:
- **The method sections** (`sections/environment.tex`, `answer_key.tex`, `estimators.tex`,
  `protocol.tex`, `threats.tex`) describe the simulator, the optimal-control answer key, the
  level-score estimators and the planned audit as they were built. Every number in them carries
  a `% src:` comment naming the repository file it comes from.
- **The related-work survey** (`sections/related.tex`, `refs.bib`). Citations marked `\VERIFY`
  were not checked against their primary sources.

What is not there:
- **Results.** `sections/results.tex` and the abstract hold `\RESULT{...}` placeholders. The
  racing audit, the paper's main contribution, was never run: it needs about 5,400 labelled
  levels and 21 curriculum runs (follow-through plan, items PA-1 to PA-7).
- The one part of the paper that was run is the maze replication, which was pre-registered and
  completed: [`docs/findings/maze-e5.md`](../docs/findings/maze-e5.md).

Build: `latexmk -pdf main.tex` in this folder. `tools/gate_values.py` recomputes the gate values
the draft quotes.
