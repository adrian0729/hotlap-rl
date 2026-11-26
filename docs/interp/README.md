# Studies of the trained networks: designs and protocols

Four studies looked inside the trained networks. Each was pre-registered from the document
below, under the tag beside it. A title that says "not frozen" is the text as tagged: the tag
is what froze the design.

| Document | Tag | Study |
|---|---|---|
| [psychophysics-protocol.md](psychophysics-protocol.md) | `psychophysics-prereg-v2` | Step 1, network psychophysics: the networks' responses on controlled corners, against the optimum's |
| [receptive-fields-design.md](receptive-fields-design.md) | `receptive-fields-prereg-v1` | Step 2, receptive fields: when the inside edge moves, does the line follow? |
| [h4r-design.md](h4r-design.md) | `h4r-prereg-v1` | H4R: what training on real widths does to edge tracking, on 20 fresh networks |
| [costate-design.md](costate-design.md) | `costate-prereg-v1` | Idea 2: does the network encode the costate? |

[IMPLEMENTATION.md](IMPLEMENTATION.md) maps step 1's protocol onto the code.

The code is in `src/apexzero/interp`, `fields` and `costate` ([map](../../src/README.md)), and
the results are in [../findings/](../findings/README.md).
