# The margin recipe on the 12 held-out circuits: plan (POST HOC; written before any margin network was run on R_TEST, 26 Nov 2026)

This plan, its subjects file, its predictions file and its script are committed and pushed
before the run. The script refuses to run on R_TEST otherwise, and records the commit it ran at.

**Label: POST HOC.** The lockbox was spent once, on E0, under `protocol-v1`
([lockbox.md](lockbox.md)). Protocol Section 2 says that any later R_TEST run with another
network is POST HOC wherever it is reported. This is such a run. It decides nothing about E0,
and it changes no number in `lockbox.md`. The user asked for it on 26 Nov 2026, as part of
wrapping the project up.

## 1. The question

After the lockbox, a training-only margin of 1.4 m took the recipe from 7.2 to 11.4 of the 12
R-dev circuits at 1B steps ([gw5.md](gw5.md) Section 5). R-dev lends the generator its width
profiles, so that result is in-sample for widths, and no held-out completion was measured.

Does the margin's completion gain hold on the 12 circuits whose widths were never in training,
and what does it cost in lap time there?

## 2. Subjects

GW-6's five networks, `gw6-margin-s80` to `gw6-margin-s84`, at their final checkpoints
(999,948,288 steps), pinned by sha256 in
[`margin-rtest-subjects.json`](margin-rtest-subjects.json). None is chosen or dropped. They are
E0's recipe (`generator-v1`, v1 curvature, copied R-dev widths) with one change: training
episodes end 1.4 m from the edge instead of 1.0 m. Evaluation is at 1.0 m, as always.

What was known when they were made:
- The margin was listed as a lever on 25 Oct 2026, before the lockbox was opened (follow-through
  plan, Section 7.4, GW-5).
- Its value, 1.4 m, was fixed on 30 Oct, after E0's lockbox result was known. Nothing in that
  result was used to choose it: the choice came from R-dev diagnostics (GW-1) and was confirmed
  on R-dev only (GW-5, GW-6, GW-8).
- The networks were trained on 30 Oct. No R_TEST circuit, width profile or result entered their
  training or their selection.

## 3. Protocol

The lockbox's own, through the lockbox's own code (`scripts/lockbox.py`, imported unchanged; its
tag gate must pass, so the metric code is the code `protocol-v1` pins):
- the 12 R_TEST circuits, originals only (no mirrored or reversed variants);
- `PROTOCOL["laps"]`: default car, grip 1, no observation noise, a rolling start at 0.9 times
  the reference speed, 10 runs with run 0 centred and the rest jittered, 2 laps with lap 2 timed,
  seed 0;
- a circuit is completed when more than half its runs finish;
- the gap is the median completed lap over the lockbox's stored reference lap, minus 1. The
  references are `outputs/lockbox/ocp/<circuit>__w+0.0.pkl` and the two width re-solves, as they
  stand. Nothing is re-solved.

`laps` prints no outcome. `analyse` runs once, behind a lock, and writes
`outputs/posthoc/margin-rtest/summary.json`.

Before the R_TEST run, the same script runs on the 12 R-dev circuits (`--mode dryrun`, which
admits no R_TEST name) and is checked against each network's stored `eval_rdev.json`.

## 4. What is computed

Per network and for the median network, with the lockbox's `family_summary`: circuits completed,
the share of laps completed and the median gap over completed circuits, each also against the
-0.5 m and +0.5 m references. Beside them, E0's numbers from `outputs/lockbox/analysis.json`.

- **Completion test.** An exact one-sided permutation test on circuits completed, margin above
  E0, five networks against five (252 relabellings; the smallest possible p is 0.004). E0's
  counts on R_TEST are 6, 10, 8, 10, 7.
- **Lap-time cost** (descriptive). The median gap of each arm's median network, and, per circuit
  that at least one network of each arm completes, the arms' median gaps.
- **Per circuit** (descriptive). Networks completing, of 5, in each arm.
- **H1 as written**, read on the median margin network, descriptively.

## 5. Predictions and the reading rule

Both are in [`margin-rtest-predictions.json`](margin-rtest-predictions.json), fixed with this
plan. In brief:

| Quantity, median margin network | Predicted | Interval |
|---|---|---|
| Circuits completed, of 12 | 11 | 9 to 12 |
| Share of laps completed | 92% | 75% to 100% |
| Median gap | 5.9% | 5.2% to 6.8% |
| Median gap, margin minus E0's 5.16% | +0.7 points | +0.1 to +1.6 |
| Circuits completed by the weakest network | 9 | 8 to 12 |

The basis is E0 under the same harness: from R-dev to R_TEST its median network's circuits
went from 8 to 8 and its median gap from 6.35% to 5.16%.

**Reading.**
- "The completion gain transfers" if the permutation p is at most 0.05 and the median margin
  network completes at least 10 of 12.
- "The completion gain does not transfer" if the margin networks' mean is less than 1.0 circuit
  above E0's 8.2.
- "Partly" otherwise.

## 6. What it cannot show

- It is one look, after the lockbox, at networks from one recipe. It is not a second lockbox.
- GW-6 and E0 differ in box, day and seeds as well as in the margin ([gw5.md](gw5.md)
  Section 5).
- Five networks against five: the test can reach p = 0.004 at best, and a moderate gain can
  miss 0.05.
- Completion at the 1.0 m evaluation margin says the cars keep clear of the edge. It does not
  say they follow it better: on R-dev the margin left every edge-following measure unchanged.

## 7. What gets reported

`docs/findings/margin-rtest.md`, with the label POST HOC in its title, whatever the result. The
showcase page and the README then quote it with the same label.

## 8. The dry run on R-dev (26 Nov 2026, before this plan was committed)

`scripts/margin_rtest.py laps --mode dryrun` ran the five networks on the 12 R-dev circuits on
the Mac. It read no R_TEST file.
- **59 of the 60 completion fractions equal the stored evaluations**, which the training box
  (an A6000) wrote at the end of each run.
- **One differs:** `gw6-margin-s80` on Norisring finishes 6 of 10 runs here against 3 of 10
  stored, which moves that network from 11 circuits to 12. The jittered runs split on that
  circuit, and float32 arithmetic differs between the Mac's CPU and the box's GPU. GW-1 saw
  fractions differ between the two machines as well (334 of 336 equal), though no circuit
  changed sides there.
- So circuit counts can move by one between machines where a circuit is borderline. The
  comparison this plan makes is on one machine: E0's lockbox laps and these laps both run on
  the Mac.
