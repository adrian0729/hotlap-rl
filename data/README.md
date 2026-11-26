# Data

Only this note is committed. The data itself is fetched by script, because its licences are
not the code's.

| Folder | What | Fetched by | Licence |
|---|---|---|---|
| `tracks/tumftm/` | Circuit centrelines and track widths from the TUMFTM racetrack-database | `scripts/fetch_tracks.py` | LGPL-3.0 |
| `raw/openf1/` | Qualifying and sprint-qualifying sessions, 2023 to 2026 | `scripts/fetch_openf1.py` (about three hours, resumable) | CC BY-NC-SA 4.0 |
| `raw/jolpica/` | Official qualifying results, 2023 to 2026 | `scripts/fetch_jolpica.py` | jolpica-f1's terms |

The simulator, the optimal-control solver, training and the held-out test need only the
circuits. The OpenF1 and jolpica archives feed the snapping audit and the drivers study.

One file derived from this data is committed: the showcase's `docs/showcase/data.js`, whose
circuit geometry comes from the TUMFTM database and is distributed under LGPL-3.0. Its
[notice](../docs/showcase/DATA-LICENSE.md) says what is under which licence.
