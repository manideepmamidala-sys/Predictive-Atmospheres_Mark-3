# Rating provenance

**Provenance:** investigator report supplied 2026-10-08. Original response forms, exact question wording and conversion spreadsheet are unavailable. CSV values were entered after transformation and are ingested without another conversion.

| Experiment | Original response described by investigator | Existing CSV interpretation |
| --- | --- | --- |
| 1 | Comfort score `s` in 0–10 | `comfort = s/5 - 1`; this is not valence |
| 2 | Separate valence and arousal scores `s` in 0–10 | Each axis `s/5 - 1` |
| 3 | Pleasant/unpleasant direction plus intensity `s` in 0–10 | Signed valence `+s/10` or `-s/10` |
| 3 | Calm/excited direction plus intensity `s` in 0–10 | Signed arousal `-s/10` or `+s/10` |

At zero intensity, direction cannot be reconstructed. Experiments 2 and 3 have signed numeric axes but distinct elicitation, so their measurement equivalence is unresolved. Missing ratings remain missing; the Experiment 1 comfort construct is kept separate from affect coordinates. The many questionnaires named in historical thesis prose do not have supplied response records and are not analyzed as administered measures.
