# Licence of `data.js`

`data.js` holds two kinds of content under two licences.

**Circuit geometry: LGPL-3.0.** The `track` entries (the left and right edges of the 12
circuits) are derived from the [TUMFTM racetrack-database](https://github.com/TUMFTM/racetrack-database)
of the Institute of Automotive Technology, Technical University of Munich, which is licensed
under the GNU Lesser General Public License v3.0. The derived geometry is distributed here
under the same licence. Its text is in [`LGPL-3.0.txt`](LGPL-3.0.txt); it builds on the GNU
General Public License v3.0, at <https://www.gnu.org/licenses/gpl-3.0.txt>.

What was changed from the source files: each centreline and its widths were resampled every
2 m, the reference line was refined (`apexzero.tracks.reference.refine_reference`), the two
edges were computed from it, and the coordinates were rounded to 0.1 m and delta-coded.
`scripts/showcase.py` does this. The unmodified source files are not in this repository;
`scripts/fetch_tracks.py` fetches them.

**Everything else: Apache-2.0.** The laps, the optimal laps, the scoreboard and the chart data
are this project's own results, under the repository's licence.

Until 26 Nov 2026 the repository committed no geometry derived from that database. `data.js`
is the one exception, made so that the showcase page can be served publicly.
