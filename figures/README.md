# Figure assets

The main report uses Figures 1–2; the supplement uses Figures S1–S4. Numerical sections `fig1`–`fig6` in `figures-data.json` retain stable identifiers and values. Its `display_mapping` relates those identifiers to the displayed labels and filenames.

| Display label | Current asset | Original stable identifier | Interpretation |
|---|---|---|---|
| Figure 1 | [fig1_key_construction.svg](fig1_key_construction.svg) | fig1 | Each source position has two numbered key slots, including source position 492 at slots 492 and 493. Letter types may occur at multiple source positions. |
| Figure 2 | [fig2_edition_drift.svg](fig2_edition_drift.svg) | fig6 | Post-answer alignment of the 1801-attributed Wikisource transcription with the inspected Alden printed witness. MY occupies positions 94–95; position 95 is the first differing letter. Dark blue indicates agreement with Alden and light grey indicates difference. |
| Figure S1 | [figS1_key_usage.svg](figS1_key_usage.svg) | fig2 | Observed combined coverage is 224/492 source positions. Dark blue indicates forward numbering and grey indicates reversed numbering. |
| Figure S2 | [figS2_window_control.svg](figS2_window_control.svg) | fig3 | F1 histogram for the MY-restored Wikisource transcription; comparison annotations show other-family best scores. The true-window indicator is solid blue; the best-other-window indicator is dashed grey. |
| Figure S3 | [figS3_coverage.svg](figS3_coverage.svg) | fig4 | Dictionary spans of 3–18 letters; top-50 alternatives were language-model selected, so this remains a corpus-dependent cross-check. |
| Figure S4 | [figS4_fold_detection.svg](figS4_fold_detection.svg) | fig5 | Exploratory and clue-informed. The observed curve is blue, the pointwise shuffle mean is dashed light grey and the pointwise 99th percentile is solid dark grey. These curves differ from the maximum-over-R comparison, whose p-value does not adjust every analyst choice. |

`presentation_updater.py` applies titles, witness labels and accessible colour/line styles to existing SVGs in a new directory. It does not recreate measurements. From this directory:

```text
python presentation_updater.py . NEW_EMPTY_OUTPUT_DIRECTORY
```

Figure 1 includes short literary-source fragments. Figure 2 shows letter-agreement indicators sorted by source position, rather than ordered ciphertext-to-plaintext correspondence. The numerical ciphertext, complete decoded poem, original photographs and private transcripts are not included. The Wikisource comparison was not checked against an image of the original 1801 printed page; it does not establish a difference between physical editions.
