# The showcase page

`index.html` is one self-contained page: the final agent replayed on the 12 held-out circuits
beside the optimal lap, the scoreboard of all five networks, and the project's main findings as
charts. It has no build step and no dependency beyond two web fonts.

Live: <https://adrian0729.github.io/apexzero/showcase/>

| File | What |
|---|---|
| `index.html` | The page: markup, styles and script |
| `data.js` | Everything the page shows, written by `scripts/showcase.py` |
| `img/*.png` | Stills of the page for the README, written by `scripts/showcase_stills.py` |
| `DATA-LICENSE.md`, `LGPL-3.0.txt` | The licence of the circuit geometry inside `data.js` |

## Viewing it locally

```bash
python3 -m http.server 8765 --directory docs/showcase
```

Then open `http://localhost:8765`. Opening `index.html` straight from disk works too.

Deep links: `?c=Spa&t=41.5&cam=whole` opens a circuit paused at a time, `?view=<element id>`
shows one element alone and `?theme=light|dark` fixes the theme. The stills use all three.

## Rebuilding it

```bash
uv run python scripts/showcase.py            # writes docs/showcase/data.js, about 20 s
uv run python scripts/showcase_stills.py     # writes docs/showcase/img/*.png (needs Chrome)
```

Rebuilding `data.js` needs what the lockbox run left on the machine that ran it and git does
not carry: the TUMFTM circuits under `data/`, the networks' checkpoints under `runs/`, and the
reference laps under `outputs/lockbox/ocp/`.

## Where its numbers come from

- **Scoreboard and headline figures:** `outputs/lockbox/analysis.json`, the pre-registered
  `protocol-v1` analysis, read as it is.
- **The network shown:** `e0-s52`, the median of the five by circuits completed (8 of 12). The
  choice is a rule in `scripts/showcase.py`, not a pick.
- **Replays: post hoc.** The lockbox stored each completed lap's path but no crash trace and no
  pedal or steering, so each replay is a fresh single rollout of the same checkpoint under the
  same protocol. The script stops unless every replay reproduces the stored run: the same
  outcome, and the same lap time to 1 ms or the same crash station to 5 m. On the build of
  25 Nov 2026 the largest differences were 0.83 ms and 0.06 m.
- **Charts:** the committed result files of GW-3, GW-5, GW-6, GW-8, X-2/X-3 and E0's gate.

## The geometry in `data.js`

`data.js` holds track geometry derived from the TUMFTM racetrack-database (LGPL-3.0). The
repository fetches that database by script and commits nothing else derived from it; this file
is the one exception, made on 26 Nov 2026 so the page can be served publicly.
[`DATA-LICENSE.md`](DATA-LICENSE.md) says what is under which licence. The stills in `img/`
carry the attribution in a footer, as the other committed figures do.

## One known wrinkle

`apexzero.viz.sectors.carry_over_split` stops with "the sectors do not tile the lap" on Austin
and Spa, where a sector boundary lands within 1e-12 m of a 2 m grid station without being
equal to it. `scripts/showcase.py` snaps such boundaries onto the station before calling it.
The fix lives in the script because `src/apexzero` is part of the code `protocol-v1` pins and
is kept byte-identical to that tag.
