# Addendum 1: Independent Replication, Textual Witnesses, and Clue Interpretation

*Supplement to* An Independent Reconstruction of Decipher II, Message 1 (1985–86)

**Christopher A. Eckman**

Independent Researcher

ORCID: [0009-0008-3325-4513](https://orcid.org/0009-0008-3325-4513)

*Non-peer-reviewed research addendum. November 2026.*

**Supplements:** Eckman, C. A. (2026). *An Independent Reconstruction of Decipher II, Message 1 (1985–86).* Zenodo, 31 October 2026. [https://doi.org/10.5281/zenodo.23844582](https://doi.org/10.5281/zenodo.23844582).

**Relationship to the original report:** This addendum supplements the report. It is not a replacement or new version, and it changes none of the report's results; one descriptive clarification is noted in §5. The report, its supplement, software release v1.0.0 and their published checksums are unchanged, and the reconstruction, its working corrections and its limitations stand as published.

## Abstract

On 4 November 2026 the independent researcher umbrellaid reported an external check of the Decipher II, Message 1 reconstruction published on 31 October 2026, together with a separately made numerical transcription, a third textual witness of the key paragraph and readings of the recorded clues. This addendum documents those reports and separates what was checked for it from what rests on umbrellaid's account. A separately written implementation of the published construction passed all 19 of its checks, including the four published hashes, and a rerun for this addendum confirmed the result. The umbrellaid sequence of 314 values, public since 6 October 2026, differs from the original input only at observation 306 and reproduces the published input fingerprint when that value is set to the compilation's 338. Project Gutenberg eBook #829, which umbrellaid identified as a third witness of the paragraph, normalizes to 491 letters, against 492 for the Alden witness and 490 for the Wikisource transcription; a direct comparison for this addendum confirmed both reported differences in wording. Three of the five recorded clues are consistent with the construction. The results strengthen the reproducibility of the specified reconstruction but do not resolve the probable reading 830 at observation 169, identify the designer's edition or establish the designer's intent.

## 1. Purpose and scope

On 4 November 2026 (UTC) umbrellaid posted three comments in a public GitHub issue thread opened by the author (umbrellaid 2026a) and published supporting code and notes (umbrellaid 2026b, commit `d0f7d83`). The author had earlier contributed one documentation pull request to that repository, merged on 3 November as `33d5517`, which added a summary of the original report to `docs/decipher-ii.md`; the passages of that file cited here were written by umbrellaid. This addendum records the findings because they bear on the reproducibility and evidential limits of the original report (Eckman 2026a). It adds no new decoding and changes no input, correction or software. Observation numbers, key slots and source positions are one-based, as in the original report, unless marked zero-based. Each claim is classified by its evidential basis (Table 1).

**Table 1. Evidence classes used in this addendum.**

| Class | Basis | Examples |
|---|---|---|
| Checked | Recomputed for this addendum from retained or public files | Published hashes; the external verifier's result; agreement of the stored sequence with the input fingerprint; Gutenberg #829 wording |
| Supported | Visible in umbrellaid's public code, data or commit history | Implementation imports no code from this project; `HalfFwdRev` limited to word initials |
| Reported | The umbrellaid account, not reproduced here | Transcription procedure and its independence; dates of umbrellaid's own procedures |
| Interpretation | A reading of the evidence, not a test | Clue readings; implications for negative searches |

Decipher II, Message 1 was solved in 1986 by Eileen Novak and three other contestants (Forstrom 1986). Neither the original report nor this addendum claims a first solution or first publication.

## 2. Independent computational replication

The umbrellaid script `solver/verify_ii1.py` (commit `4919119`, 4 November 2026 UTC) reimplements the construction of §3.1 of the original report. Unicode NFKD normalization, uppercase conversion and retention of ASCII A–Z give S; the key is K = S || reverse(S); and slot n addresses source position σ(n) = n for n ≤ 492 and 985 − n otherwise. The script imports no code from this project, takes its expected values from the published report and README, and reports only the length and SHA-256 value of the decoded message. Its 19 checks cover the quantities in Table 2, mirror addressing, the duplicated turnaround at slots 492 and 493, the two working corrections, reachability and a repeated-value consistency check.

For this addendum the script was run unmodified with Python 3.10.11 in isolated mode, without the `uv` launcher, on a fresh copy of the files at commit `d0f7d83`. It reported 19 passes and no failures. The published values were also recomputed with the released verifier (Eckman 2026b; Table 2), and the canonical form behind the input fingerprint was confirmed: 314 decimal integers joined by a comma and one space, then a period and LF, in 1,530 ASCII bytes without a BOM or CR.

**Table 2. Published values and their external replication.** Full SHA-256 values appear in the original report's Supplementary Table S2b and, for the input fingerprint, in the notes to Supplementary Table S1.

| Quantity | Published value | External verifier | Recomputed for this addendum |
|---|---|---|---|
| Source S | 492 letters; `9eeff566…f29d` | Pass | Pass |
| Key K | 984 slots; `571b2327…5466` | Pass | Pass |
| Literal output | 314 letters; `859f2c34…ee1f` | Pass | Pass |
| Original input fingerprint | 1,530 bytes; `1e60d5d6…2edc` | Pass, from its stored sequence with observation 306 set to the published 338 (§3) | Pass, from the retained input |
| Distinct values | 259 original; 261 corrected | Pass | Pass |
| Values above 492 | 152 original; 153 corrected | Pass | Pass |

The replication is external but not independent of the specification. Its source file is byte-identical to the published `inputs/source_transcription.txt` (SHA-256 `8bfcfb35…fdcf`), and its correction values match the published `inputs/corrections.json`. umbrellaid's own contributions are the implementation and the numerical sequence, whose independence §3 qualifies. The result shows that a separately written program reproduces the published outputs from the published inputs, not independent discovery of the passage or construction, independent recovery of the message, or the designer's intent.

Because the matching output hash includes the working value 830 at observation 169, the replication is conditional on that reading in the same way as the original decoding, as umbrellaid states. The same correction explains why 152 original but 153 corrected values exceed 492: the transcribed 330 addresses forward slot 330, whereas 830 addresses the reversed half at source position 155. The correction at observation 306 from 338 to 388 remains in the forward half; as in the original report, umbrellaid is credited with its earlier public report.

## 3. Independent numerical transcription

According to umbrellaid, the Message 1 numbers were re-transcribed on 5 October 2026 from the printed puzzle surface at 3× magnification, independently of Kavett's compilation, and the resulting sequence, with observation 306 set to 338, reproduces the published input fingerprint (umbrellaid 2026a).

The stored sequence was checked for this addendum. The file `data/ciphers.json` is byte-identical at commits `0b2acfd`, `8889ffb` and `d0f7d83`. The first was public by 6 October 2026, 19:58:34 UTC (server-recorded), before the original report appeared, and this project has not redistributed its numerical input. The 314 stored integers differ from the retained original input only at observation 306, where they record 388 and the compilation records 338. With that value set to 338, their canonical serialization reproduces the published fingerprint `1e60d5d6…2edc`. At observation 169 the stored value is 330.

The two records therefore agree at 313 of 314 observations, and at observation 306 the umbrellaid reading matches the photograph-supported working value 388. This second reading corroborates the original input at those 313 observations, including 330 at observation 169, and reduces the concern of a typing error peculiar to Kavett's compilation.

Three qualifications apply. First, the image source is not identified: the repository describes the re-transcription as made from the printed puzzle surfaces, calls the puzzle images in Kavett's shared archive “the shared scans” and states that multimodal models read them (umbrellaid 2026b, `README.md`, `docs/decipher-ii.md`). The photograph examined in this study also comes from Kavett's compilation (Kavett n.d.), so the second reading is not documented as a reading of a separate physical copy. Second, the repository describes the re-transcription as compared token by token with a previously stored sequence of undocumented origin, so its independence from Kavett's typed transcription rests on umbrellaid's account. Third, agreement between two readings neither shows that the printed puzzle is free of error nor resolves observation 169: the umbrellaid reading supports 330 as the transcribed value, and 830 remains a probable working reading based on candidate-aware readings rather than blind verification (original report, Table 2).

The umbrellaid discussion calls 338 the “as-printed” value at observation 306. Because the photograph supports 388, this addendum calls 338 the value recorded in Kavett's compilation.

## 4. Additional textual witness: Project Gutenberg #829

The original report compared two witnesses of the tailor paragraph in Part III, Chapter 2: the text printed in Alden's anthology (Swift 1911), which normalizes to the required 492 letters, and a Wikisource transcription attributed to the 1801 *Works* (Swift n.d.), which omits MY and normalizes to 490. umbrellaid identified a third witness, Project Gutenberg eBook #829 (Swift 1997), which normalizes to 491 letters and differs from Alden at two places: “take measure” for “take my measure” (−2 letters) and “with a rule and compasses” for “with rule and compasses” (+1).

For this addendum the author downloaded the Gutenberg plain-text file (`pg829.txt`, most recently updated 6 April 2025; SHA-256 `fca36de3…6edd`) on 4 November 2026, and the paragraph was located by the anchor phrase that umbrellaid's `solver/check_ii1_witness.py` uses. It normalizes to the same 491 letters obtained by applying the two reported differences to the inspected Alden transcription, so those are its only letter-level differences from Alden. The Wikisource values were recomputed from the retained transcription, whose file SHA-256 (`7d285988…53d1`) is recorded in Supplementary Table S1 of the original report.

**Table 3. Normalized witnesses of the tailor paragraph.** Positions are one-based positions in the Alden source sequence. For each corrected observation value c, same-index agreement compares the Alden letter at source position σ(c) with the witness letter at that position. Own-length decoding applies the construction at the witness's length, K = W || reverse(W), and compares each decoded letter with the Alden decoding.

| Witness | Wording at the two variants | Letters | First divergence | Same-index agreement | Own-length decoding |
|---|---|---:|---:|---:|---:|
| Alden anthology (copyright 1911), p. 97 | take my measure; with rule | 492 | — | 314/314 | 314/314 |
| Wikisource, 1801-attributed | take measure; with rule | 490 | 95 | 55/314 | 40/314 |
| Gutenberg #829, plain text | take measure; with a rule | 491 | 95 | 63/314 | 72/314 |

The SHA-256 values of the normalized sequences, serialized as uppercase ASCII without separators or a trailing newline, are:

```text
Alden 1911 (492)            9eeff566fe707e39486c1bb119d5c82f19566772706342c44803d6079faef29d
Wikisource (490)            965b567c82fe360a6b99827962f3a04242dea3d24bba28636c6a72227617af47
Gutenberg #829 (491)        531f427e4948ccdd7787adf142cd1255a492c7fa89ebdb236d394a40a9d73a85
```

The deletion of MY removes Alden positions 94–95 (zero-based 93–94). Because the next word, MEASURE, also begins with M, the first differing letter is at position 95. The inserted A falls between Alden positions 234 and 235, immediately before the R of RULE, and occupies position 233 (zero-based 232) of the 491-letter sequence. The figures 94 and 232 in the umbrellaid report are therefore a one-based Alden position and a zero-based Gutenberg position, respectively. Between the two variants each Alden letter appears two positions earlier in the Gutenberg sequence, and after the insertion one position earlier.

Under the published construction, a 491-letter source would give a 982-slot key with mirror pairs n and 983 − n, and the released decoder rejects any source that does not normalize to 492 letters. With the Alden addressing retained, 53 of the 314 corrected observations address positions 1–94, whose letters are unchanged, and the other 261 address positions at or beyond the first divergence. Overall, 63 observations find the same letter at the same position, the 53 before the divergence and 10 coincidental matches, while 251 find a different letter or none; two of them address position 492, which the 491-letter sequence lacks. The Wikisource transcription gives 55 of 314, consistent with the agreement reported for its paragraph-start window in §5 of the original report. Applying the construction at each witness's own length instead displaces the reversed half as well: the 982-slot Gutenberg key reproduces 72 of the 314 decoded letters, and the 980-slot Wikisource key 40.

The third witness supports the original report's argument that exact wording matters to a position-indexed literary key. A reader who finds the correct work and paragraph in a widely available free e-text would recover only a small part of the message. Under the demonstrated construction and normalization, an exact count of 492 letters is therefore a necessary condition, which the Gutenberg and Wikisource texts do not meet as they stand; §5 reads the clue “492” as that count. The condition is not sufficient. A witness of the correct length can still differ in its letters, for example through a substituted word of equal length. Agreement with the published source hash establishes identity with the published key. Compatibility with the observed decoding is a weaker condition: the 314 observations address only 224 of the 492 source positions, so a witness that differs from Alden only at some of the other 268 positions reproduces the same message (checked for one altered position). Printings with the same normalized paragraph produce the same key, and neither condition identifies the designer's edition. Both conditions presuppose the construction and normalization, which were established here only after decoding. The Alden anthology remains a compatible witness; the designer's edition and earlier printings remain unexamined.

## 5. Retrospective interpretation of the recorded clues

Kavett's compilation records five clues for Message 1 (Table 4), read here from the export retrieved on 11 October 2026 (SHA-256 `d960bac8…1e65`). It does not state whether each clue was printed with the game materials or issued through the telephone hotline described in contemporary reporting, and the photographed Message 1 face carries no clue text. This addendum therefore calls them the recorded clues. The original report (§7 and Supplementary Table S6) calls “S.I.N.” a printed clue. The photographed Message 1 face does not carry it, and whether it was printed elsewhere in the game materials or given through the hotline is not established here.

**Table 4. Recorded clues for Message 1 and their relation to the reconstruction.**

| Recorded clue | Reading | Status |
|---|---|---|
| “The key to message one, you see, is from the authors in group C.” | Jonathan Swift is among the eleven authors the compilation lists for Message 1 | Compatible with the choice of author; does not concern the construction |
| “492” | Identifies the passage by its letter count, half of the 984-slot key, rather than by page | Consistent; the 1986 report already linked it to a passage |
| “A single place has a certain pattern to create the key.” | One contiguous passage, whose pattern is the passage followed by its reversal | Consistent; nonspecific |
| “One way gets you half way there.” | One direction of the passage supplies 492 of the 984 numbered slots | Consistent |
| “S.I.N.” | No reading proposed | Unexplained |

umbrellaid set out the readings of the second, third and fourth clues publicly (umbrellaid 2026a; 2026b, `docs/decipher-ii.md`) and counts three of the five clues as explained. The original report treated 492 as the required letter count but did not discuss the wording of the other two clues. The readings are consistent with a key drawn from one contiguous passage and extended symmetrically by its reversal. The first clue concerns the choice of author and was already compatible with the 1986 identification of the book. “S.I.N.” remains unexplained, as in the original report, and no reading of it is proposed here.

These readings are retrospective interpretations, not a separate test. “492” and “One way gets you half way there” guided the hypotheses that produced the bidirectional construction: the original report (§4 and Supplement §5) describes those mechanism choices as clue-informed, and the project's unpublished experiment log names the two clues (entries E137 and E154). Agreement between those clues and a mechanism chosen partly because of them is therefore expected. The readings add to the plausibility of the mechanism as a designed construction, but the evidence for the reconstruction remains the complete correspondence under the stated inputs, and the clues do not establish the designer's intent.

## 6. Methodological implications

In the verification comment of 4 November 2026 (13:23:44 UTC), umbrellaid corrected the description of its search tooling given in its first comment that day (00:06:34 UTC) (umbrellaid 2026a). The public history shows that `solver/body_scan.py` has contained a `HalfFwdRev` stream since the file's first commit (`7ac346b`, dated 18 October 2026; umbrellaid gives 17 October). The stream concatenates the word initials of a chapter window with their reversal rather than numbering the continuous letters of a paragraph. By umbrellaid's account (`docs/methodology.md`), the published eliminations came from the `rules.py` and `sweep.py` path instead. Those two files contain no palindromic family from the root commit `8889ffb` through `33d5517`, and an anchored palindromic family was added to them in `d0f7d83` (4 November 2026 UTC). Having a mechanism somewhere in a research codebase is not the same as exercising it in a published candidate-elimination search. A negative result covers only the constructions, source witnesses and windows actually searched, a limitation that the original report's initial family search (E115) also showed. According to umbrellaid, its Decipher III eliminations are under revision for this reason; they are outside the scope of this addendum.

The case also shows the difference between reconstructing a historically solved puzzle and deciphering an unsolved one: the reconstruction could be checked against a theme known from the 1986 reporting. External replication tests whether the published computation can be reproduced; it does not establish novelty or priority.

## 7. Limitations and unresolved questions

The complete decoding remains conditional on the probable reading 830 at observation 169, which the second transcription reading does not support. The Gutenberg comparison covers one plain-text file of eBook #829; its other formats and earlier releases were not compared. The inspected files document neither the image source of the umbrellaid transcription nor the origin of its previously stored sequence, and transcription and procedure dates are self-reported except where server-recorded. The designer's edition and procedure for choosing numerical positions, the unused mappings and the meaning of “S.I.N.” remain unresolved. The external checks are not peer review, and this addendum has not been peer reviewed.

## 8. Conclusions

An external researcher has reproduced the published Decipher II-1 computation with a separately written implementation, and the result was rerun for this addendum. The umbrellaid numerical sequence agrees with the original input at 313 of 314 observations and matches the photograph-supported reading at the remaining one. A third witness of the key paragraph identified by umbrellaid, a widely available free e-text, normalizes to 491 letters, reinforcing the original finding that exact wording governs a position-indexed key. Three recorded clues are consistent with the construction, although two of them guided its discovery and none establishes intent. The reconstruction, its working corrections and its stated limitations are unchanged.

## Data availability and reproducibility

From the root of the published repository, `py -3 -B code/check_public_materials.py` rechecks the source and key hashes (use `python3` on macOS and Linux), and `code/prepare_original_input.py` fingerprints a separately obtained Message 1 transcription. To compare another witness of the tailor paragraph, save only that paragraph as `witness.txt` and the lines below as `compare_witness.py` in a working copy of the repository (not the pristine release checkout), then run `py -3 -B compare_witness.py`; the printed opcodes are zero-based.

```text
import sys, hashlib, difflib
sys.path.insert(0, 'code')
import ii1_verify as V
a = V.normalize_source(open('inputs/source_transcription.txt', encoding='utf-8').read())
b = V.normalize_source(open('witness.txt', encoding='utf-8').read())
print(len(a), len(b), hashlib.sha256(b.encode('ascii')).hexdigest())
ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
print([op for op in ops if op[0] != 'equal'])
```

The umbrellaid checks can be rerun from the umbrellaid repository at commit `d0f7d83` with `uv run solver/verify_ii1.py` and `uv run solver/check_ii1_witness.py`; the second downloads the Gutenberg text and, because this witness has 491 letters, exits with status 1 to report the failed 492-letter condition, not a failed comparison. A verification receipt holding only hashes, counts and positions is retained with the project's records; as in the original report, the complete ciphertext, decoded message and ordered correspondence are not redistributed.

© 2026 Christopher A. Eckman. Licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/), except that the quoted clues, quotations from the umbrellaid comments and other third-party material are excluded; the underlying Swift text is public domain, and the code example may also be used under the MIT License.

## Acknowledgments

The author thanks umbrellaid for the external computational replication and transcription comparison, the identification of the Gutenberg #829 witness, the clue readings and the clarification of the umbrellaid search tooling. Karen Kavett gathered and shared the compilation, images and historical sources on which both projects draw. Original solution credit belongs to Eileen Novak and the three other 1986 contestants; the puzzle is the work of Decipher, Inc.

## AI use, funding and competing interests

Christopher A. Eckman directed the preparation of this addendum. Claude Code (Anthropic) inspected the sources, ran the verification computations and drafted the text, which the author reviewed before publication. The external replication was carried out by umbrellaid, whose repository states that its analysis, transcriptions and code were produced with AI coding assistants. This addendum has not undergone external peer review.

**Funding:** No external funding.

**Competing interests:** No competing interests. The author contributed one documentation pull request to the umbrellaid repository (§1).

## References

Eckman, Christopher A. 2026a. *An Independent Reconstruction of Decipher II, Message 1 (1985–86).* Non-peer-reviewed research report. Zenodo, October 31. [https://doi.org/10.5281/zenodo.23844582](https://doi.org/10.5281/zenodo.23844582).

Eckman, Christopher A. 2026b. *Decipher II-1 reconstruction and verification software*, version 1.0.0. [GitHub release v1.0.0](https://github.com/chriseckman/decipher-ii1-reconstruction/releases/tag/v1.0.0), commit `cd11a08746d507f0ceed058ff4da20a1058eae2d`.

Forstrom, Tom. 1986. “Decipher II game pays off in cold cash.” *Statesman Journal*, March 25, pp. 1B and 3B.

Kavett, Karen. n.d. *Decipher II and III Puzzles* [community research compilation], “Puzzle 2-1.” [Google document](https://docs.google.com/document/d/1SDRvq1iRa3oLxaSSMoG_iy1klczI2tFsN7gvgDl7pcE/edit). Export retrieved October 11, 2026.

Swift, Jonathan. 1911. *Travels into Several Remote Nations of the World* (*Gulliver's Travels*), Part III, Chapter 2. In *Readings in English Prose of the Eighteenth Century*, edited by Raymond Macdonald Alden, p. 97. Boston, New York and Chicago: Houghton Mifflin. 1911 is the copyright date; the printing date of the scanned copy has not been established. [Internet Archive scan](https://archive.org/details/readingsinenglis00alde), PDF p. 115.

Swift, Jonathan. n.d. “Gulliver's Travels,” Part III, Chapter 2. Wikisource transcription attributed to *The Works of the Rev. Jonathan Swift*, vol. 6, London, 1801. [Transcription](https://en.wikisource.org/wiki/The_Works_of_the_Rev._Jonathan_Swift/Volume_6/Gulliver%27s_Travels). Retrieved October 11, 2026. The 1801 printed page was not inspected.

Swift, Jonathan. 1997. *Gulliver's Travels into Several Remote Nations of the World*. Project Gutenberg eBook #829, released February 1, 1997; most recently updated April 6, 2025. [https://www.gutenberg.org/ebooks/829](https://www.gutenberg.org/ebooks/829). Plain-text file retrieved November 4, 2026.

umbrellaid. 2026a. Comments on “Decipher II-1 reconstruction published, and acknowledgment of your earlier finding,” issue #1, *decipher-money-hunt-research*, GitHub, November 4, 00:06:34, 13:23:44 and 13:30:06 UTC. [First comment](https://github.com/umbrellaid/decipher-money-hunt-research/issues/1#issuecomment-6618743656); [verification comment](https://github.com/umbrellaid/decipher-money-hunt-research/issues/1#issuecomment-6631781113); [clarification comment](https://github.com/umbrellaid/decipher-money-hunt-research/issues/1#issuecomment-6631922155).

umbrellaid. 2026b. *decipher-money-hunt-research* [research repository]. [GitHub](https://github.com/umbrellaid/decipher-money-hunt-research), commit `d0f7d83971eaa46a7ec7517ef6118f8b14a39788`, November 4, 2026. Files are cited by path in the text.
