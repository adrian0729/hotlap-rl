# Pre-registrations

Each document here was frozen by an annotated git tag before its study's outcome was computed.
The tag is what froze it: a title that still says DRAFT is part of the frozen text.

| Document | Tag | What it fixes |
|---|---|---|
| [protocol-v1.md](protocol-v1.md) | `protocol-v1` | The lockbox: the one evaluation of the 12 held-out circuits, with its [subjects](protocol-v1-subjects.json) and its [predictions](protocol-v1-predictions.json) |
| [gw3-width-round.md](gw3-width-round.md) | `gw3-prereg-v1` | GW-3, the combined width round |
| [p4-b2-specialists.md](p4-b2-specialists.md) | `p4-b2-prereg-v1` | P4, option B2: five fresh Hockenheim specialists |
| [vg1-value-gradient.md](vg1-value-gradient.md) | `vg1-prereg-v1` | VG-1: a value-gradient term in the critic's loss |
| [maze-e5.md](maze-e5.md) | `maze-e5-prereg-v1` | Maze E5: do level scores track exact regret on the curriculum methods' own agents? |

The four studies of the trained networks were pre-registered from their design documents,
which are in [../interp/](../interp/README.md).

To read a document exactly as it was frozen:

```bash
git show protocol-v1:docs/prereg/protocol-v1.md
```

The results are in [../findings/](../findings/README.md).
