# The margin recipe on the 12 held-out circuits: the completion gain transfers. Its five networks complete 12, 12, 12, 10 and 11 circuits against E0's 6, 10, 8, 10 and 7, for about one point of lap gap (POST HOC)

Results of 26 Nov 2026. Plan: [margin-rtest-plan.md](margin-rtest-plan.md), committed and pushed
in `f0567ad` with its subjects, its predictions and its script before any margin network ran on
an R_TEST circuit. Every lap record carries that commit and a clean tree.

**Label: POST HOC.** The lockbox was spent once, on E0, under `protocol-v1`
([lockbox.md](lockbox.md)). This is a later look at another recipe's networks. It decides
nothing about E0 and changes no number in `lockbox.md`. H1 stays refuted for E0.

- **The run.** `scripts/margin_rtest.py laps` and then `analyse`, once each, on the Mac. `laps`
  printed no outcome. `analyse` took its lock before reading a lap and wrote
  `outputs/posthoc/margin-rtest/summary.json`. The lap records and the summary are committed.
- **The code.** `scripts/lockbox.py`'s own protocol, imported unchanged, behind its tag gate:
  the metric code was the code `protocol-v1` pins. The references are the lockbox's stored
  ones. Nothing was re-solved.
- **Subjects.** GW-6's five networks, `gw6-margin-s80` to `gw6-margin-s84`, at their final
  checkpoints, pinned by sha256. None was chosen or dropped.

Every number below is read from `summary.json`, except where marked "computed here" (from its
own rows or from the lap records).

## 1. The answer

| On the 12 R_TEST originals | Margin recipe | E0 (`lockbox.md`) |
|---|---|---|
| Circuits completed, per network | 12, 12, 12, 10, 11 | 6, 10, 8, 10, 7 |
| Mean | **11.4** | 8.2 |
| Median network: circuits completed | **12 of 12** | 8 of 12 |
| Median network: share of laps completed | **100%** | 66.7% |
| Median network: median gap | **6.33%** | 5.16% |

- **Completion test.** The exact one-sided permutation test on circuits completed gives
  p = 3/252 = **0.012** (mean difference +3.2).
- **Reading, by the plan's rule: "the completion gain transfers".** The p is at most 0.05 and
  the median margin network completes at least 10 of 12.
- **Three of the five networks complete all 12 circuits.** Of the 60 network and circuit
  pairs, 57 are completed and 3 are not; none is partial (computed here).
- **The cost is lap time, as on R-dev.** The median network's gap is 1.17 points above E0's.
  Per circuit, the margin arm's median gap is above E0's on 11 of 12, by a median of 0.76
  points (the exception is Mexico City, where E0's figure rests on one network).

## 2. The predictions: five of five held

Fixed in [`margin-rtest-predictions.json`](margin-rtest-predictions.json) before the run.

| Quantity, median margin network | Predicted | Interval | Observed | Held |
|---|---|---|---|---|
| Circuits completed, of 12 | 11 | 9 to 12 | 12 | yes |
| Share of laps completed | 92% | 75% to 100% | 100% | yes |
| Median gap | 5.9% | 5.2% to 6.8% | 6.33% | yes |
| Median gap, margin minus E0's 5.16% | +0.7 points | +0.1 to +1.6 | +1.17 points | yes |
| Circuits completed by the weakest network | 9 | 8 to 12 | 10 | yes |

Completion came in at the top of its interval, and the gap above its central value. The plan
predicted the gap from E0's R-dev to R_TEST ratio (0.81). The margin networks' ratio is 0.88
(6.33% against their 7.16% on R-dev; computed here).

## 3. H1 as written, read on the median margin network (descriptive)

| Part | Value | Bar | Met |
|---|---|---|---|
| Share of laps completed | 100% | 90% or more | yes |
| Median gap | 6.33% | 4% or less | no |

The margin recipe meets H1's completion part and misses its lap-time part. The plan expected
the gap part to fail. None of the 57 completions is within 4% of its reference; the fastest is
4.55% (computed here).

## 4. By circuit (descriptive)

| Circuit | Margin: networks completing, of 5 | Margin: median gap | E0: networks completing, of 5 | E0: median gap |
|---|---|---|---|---|
| Austin | 5 | 7.73% | 2 | 5.95% |
| Budapest | 5 | 6.85% | 3 | 6.32% |
| Mexico City | 4 | 8.93% | 1 | 9.18% |
| Montreal | 5 | 8.22% | 5 | 7.03% |
| Monza | 4 | 6.19% | 3 | 5.59% |
| Sakhir | 5 | 5.75% | 2 | 5.68% |
| São Paulo | 5 | 5.59% | 5 | 4.80% |
| Shanghai | 4 | 8.10% | 1 | 5.34% |
| Silverstone | 5 | 5.42% | 5 | 4.67% |
| Spa | 5 | 5.08% | 5 | 4.45% |
| Spielberg | 5 | 5.74% | 4 | 4.97% |
| Suzuka | 5 | 6.55% | 5 | 5.57% |

- **Every circuit is completed by at least four of the five margin networks.** E0 had four
  circuits that at most two of its networks completed (Austin, Sakhir, Mexico City, Shanghai).
- **The three failures** (computed here from the rows): `gw6-margin-s83` at Mexico City
  (corridor exits) and at Monza (slip), and `gw6-margin-s84` at Shanghai (slip). Each fails all
  ten runs.

## 5. Crashes (descriptive)

30 of the 600 runs crash, against 189 of E0's 600 on the originals. Twenty are slips (the tyre
slip limit, a loss of control) and ten are corridor exits (computed here from the lap records).
Every one of E0's crashes was a corridor exit. With the margin, leaving the road at an edge is
no longer the usual way to fail.

## 6. The geometry error bar (descriptive)

The median network's median gap is 5.29% against the references with widths narrowed by 0.5 m
and 7.46% with them widened by 0.5 m. The gap part of H1 fails across that whole bar, as E0's
did.

## 7. What it means

- **The margin's completion gain is not an artefact of R-dev.** On the 12 circuits whose width
  profiles were never in training, the margin networks complete 11.4 on average, the same as
  their 11.4 on R-dev, against E0's 8.2.
- **The price is about one point of lap gap, as on R-dev.** The recipe trades lap time for
  room. It does not close the distance to the optimal lap: that grows from 5.2% to 6.3%.
- **It does not follow the edge better.** On R-dev the margin left every edge-following
  measure unchanged ([gw5.md](gw5.md) Section 3, [gw8.md](gw8.md) Section 3). Nothing here
  measures edge following on R_TEST.

## 8. Limits

- **Post hoc, and one look.** The run was planned and predicted in advance, but after the
  lockbox was spent, and the recipe was found after E0's lockbox result was known. Section 2
  of the plan says what informed the recipe: R-dev only.
- **Five networks against five.** The smallest p the test can give is 0.004; it gave 0.012.
- **GW-6 and E0 differ in box, day and seeds** as well as in the margin.
- **Originals only.** The mirrored and reversed circuits were not run.
- **One machine.** Both arms' laps ran on the Mac. The plan's dry run showed a circuit count
  can move by one between the Mac and the training box where a circuit is borderline.

## 9. Procedure

- `f0567ad`: plan, subjects, predictions and script committed and pushed (26 Nov 2026).
- `laps`, 00:51 to 00:59 local time, 60 records, each with `plan_commit` `f0567ad` and no
  changed path.
- `analyse`, once, at 00:59. `summary.lock` stays in place.
- No deviation from the plan.
