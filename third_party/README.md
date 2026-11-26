# Third-party code

Two pieces of other people's code, copied byte for byte so that the maze audit runs the
curriculum methods exactly as their authors wrote them. Both are licensed Apache-2.0. Neither
is edited or linted here.

| Folder | Copied from | Run through |
|---|---|---|
| [`jaxued_examples/`](jaxued_examples/README.md) | `examples/maze_plr.py` of DramaCow/jaxued | `scripts/run_jaxued_maze.py` |
| [`sfl/`](sfl/README.md) | The MiniGrid maze code of amacrutherford/sampling-for-learnability (Rutherford et al. 2024) | `scripts/run_sfl_maze.py` |

Each folder's note names the commit it was copied from. The audit that uses them is
[maze E5](../docs/findings/maze-e5.md).
