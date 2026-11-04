# Decipher II-1 reconstruction

A small, text-only Python tool for reproducing the modern reconstruction of **Decipher II, Message 1**. It checks the original numerical input, applies two documented working corrections, decodes the message using the supplied literary source, and verifies the results against published hashes.

**Python 3.10 or newer; standard library only.** No package installation, account, API, OCR, image processing, GPU or machine-learning model is required. The original ciphertext is obtained separately; it is not included or downloaded by the program.

The original puzzle was solved by contestants in 1986. This project documents a modern technical reconstruction, not the first historical solution or a general cipher solver. See the [research report](paper/PAPER_A.pdf), [editable report](paper/PAPER_A.docx), [Markdown source](paper/PAPER_A.md), [supplement](paper/PUBLIC_SUPPLEMENT.pdf) and [AI-use disclosure](paper/AI_USE_DISCLOSURE.md).

The project repository is [chriseckman/decipher-ii1-reconstruction](https://github.com/chriseckman/decipher-ii1-reconstruction). Software version **1.0.0** is distributed in the [v1.0.0 release](https://github.com/chriseckman/decipher-ii1-reconstruction/releases/tag/v1.0.0). The accompanying [research report and supplement are published on Zenodo](https://doi.org/10.5281/zenodo.23844582) (31 October 2026). Original code is MIT-licensed and original report/figure material is licensed CC BY 4.0, with third-party exclusions; see [licensing](LICENSE_STATUS.md).

## Quick start

### 1. Get Python and open the project folder

Download and extract this repository or its release ZIP. On Windows, use **Extract All** before running anything. Open the extracted folder that contains `decode.py`, then open a terminal in that folder: on Windows, right-click inside the folder and choose **Open in Terminal**; on macOS or Linux, open Terminal and use `cd` to enter the folder.

If Python is not installed, obtain it from [python.org](https://www.python.org/downloads/). On Windows, install the Python launcher if offered. Check the version:

| Platform | Command |
|---|---|
| Windows | `py -3 --version` |
| macOS / Linux | `python3 --version` |

The reported version must be **3.10 or newer**. The remaining examples use the appropriate command for each platform; no `pip install` step is needed.

### 2. Save only the original 314 numbers as `numbers.txt`

Open **Karen Kavett, *Decipher II and III Puzzles***: [public Google document](https://docs.google.com/document/d/1SDRvq1iRa3oLxaSSMoG_iy1klczI2tFsN7gvgDl7pcE/edit).

1. Find the exact heading **“Puzzle 2-1”**. Do not use “Puzzle 2-2,” “Puzzle 2-3,” or a Decipher III puzzle.
2. Copy only the numerical transcription directly under that heading, in its original order. Stop at the end of that numerical block, **before the “Clues” text**. Do not include the heading, clue numbers, surrounding commentary, images, or another puzzle's numbers.
3. Paste into a plain-text editor, such as Notepad, and save as **`numbers.txt`** in the folder containing `decode.py`. On macOS, use TextEdit's **Format → Make Plain Text** before saving. Avoid a hidden extra extension such as `numbers.txt.txt`.

The program accepts comma-separated or whitespace-separated integers, including copied line breaks and an optional final period. It rejects headings and other prose. Use the **original readings**: observation 169 is `330` and observation 306 is `338`. Do not correct them yourself.

Your `numbers.txt` is the historical **numerical ciphertext**. It is different from the **literary source paragraph**, which is already supplied as `inputs/source_transcription.txt`.

### 3. Run the decoder

Windows:

```text
py -3 decode.py numbers.txt
```

macOS / Linux:

```text
python3 decode.py numbers.txt
```

The decoder first authenticates all 314 original integers against the retained fingerprint. It then applies the two documented corrections exactly once. A changed or reordered sequence is rejected before decoding.

### 4. Read the result and find the files

A successful run prints **PASS**, the complete 314-character literal message, its verification summary, and the absolute output-folder path. Spaces and punctuation are not part of this literal output.

The default destination is a new **`Decipher-II1-local-result`** folder in your home folder, outside this repository:

- Windows: `%USERPROFILE%\Decipher-II1-local-result`
- macOS / Linux: `~/Decipher-II1-local-result`

The output folder contains:

| File | Contents |
|---|---|
| `key_source_492.txt` | The normalized 492-letter source sequence |
| `key_984.txt` | That sequence concatenated with its reversal |
| `plaintext_literal_314.txt` | The complete literal decoded message, generated locally |
| `correspondence.csv` | The 314 ordered numerical-to-letter correspondences, generated locally |
| `verification.json` | Hashes, corrections, coverage and verification metadata |

Existing output folders are never overwritten. For another run, choose a fresh folder:

```text
py -3 decode.py numbers.txt --output "../another-local-result"
```

On macOS / Linux, replace `py -3` with `python3`. Add **`--no-print`** to save and verify the message without displaying it in the terminal. Use **`--help`** for all options. A failed run exits with a nonzero status and an error explaining what to check; do not treat an error as a verified reconstruction.

## What is verified

The retained input fingerprint is SHA-256:

```text
1e60d5d63422148b385abfd0569edb1c709308eb79d51e4195b6c8a781be2edc
```

It describes **1,530 canonical ASCII bytes**: decimal integers separated by comma-space, followed by a period and LF, without a BOM or CR. The decoder canonicalizes the copied numbers before checking, so ordinary whitespace differences do not change the result. This is an input fingerprint, not the plaintext hash. Acquisition details are retained in [INPUT_REFERENCE.json](INPUT_REFERENCE.json).

| Observation (one-based) | Original input | Working value | Qualification |
|---|---:|---:|---|
| 169 | 330 | 830 | Probable reading; 330 remains the competing transcription. Supporting AI readings were candidate-aware, not blind human verification. |
| 306 | 338 | 388 | Photograph-supported; umbrellaid is credited for its earlier public report. |

The literary passage is normalized by Unicode NFKD decomposition, uppercase conversion and ASCII A–Z filtering. The resulting sequence `S` contains 492 letters; the numbered key is `K = S || reverse(S)`, with 984 positions. Numbered positions are one-based; the turnaround duplicates the last source letter at slots 492 and 493.

Expected SHA-256 values apply to uppercase ASCII letters **without a trailing newline**:

| Output | Letters | SHA-256 |
|---|---:|---|
| Source | 492 | `9eeff566fe707e39486c1bb119d5c82f19566772706342c44803d6079faef29d` |
| Key | 984 | `571b2327a0ef55d6fc74394b228ffc59e24a00f2ef6f670beb1fa08879eb5466` |
| Plaintext | 314 | `859f2c3458025e03ad8a425b8e9b9e16f152927b8b34e33300ad1d49d065ee1f` |

The corrected input exercises **224 of 492 underlying source positions** and **261 of 984 numbered slots**. Unused mappings follow from the construction rather than independent historical authentication. Matching hashes reproduce the specified working reconstruction; they do not establish the uncertain 830 reading, the designer's physical edition, the original choice among eligible numbers, universal uniqueness, or publication priority.

## Troubleshooting

| Problem | What to do |
|---|---|
| `py` or `python3` is not found | Install Python, close and reopen the terminal, then run the version command again. On Windows, ensure the Python launcher is installed. |
| The version is older than 3.10 | Install a supported Python version and select that interpreter. |
| `decode.py` or `numbers.txt` is not found | Open the extracted project folder, check the spelling and hidden filename extensions, or provide the input's full path in quotes. |
| Input contains letters or other characters | Copy only the numerical block under “Puzzle 2-1,” without the heading or clues. Save as plain text, not a Word document or PDF. |
| There are not exactly 314 values | Check for a truncated copy, duplicated lines, clue numbers or numbers from another puzzle. |
| Original-value check fails | Restore 330 at observation 169 and 338 at observation 306. The decoder applies corrections automatically. |
| Fingerprint does not match | Check every copied value and its order. Do not edit values merely to obtain PASS or bypass the check. A changed public transcription requires examination. |
| Output directory already exists | Use `--output` with a new folder name. Existing results are deliberately protected. |
| A source/key or package check fails | Re-extract a clean release and retry. Do not repair scientific inputs by guessing. |

Quote paths containing spaces, for example `py -3 decode.py "../my input/numbers.txt"`. The same options work with `python3` on macOS and Linux. The program reads local files only and makes no network requests.

## Developer and reproducibility checks

From this repository's root, on Windows:

```text
py -3 -B code/check_manifest.py
py -3 -B code/check_public_materials.py
py -3 -B -m unittest discover -s code -p "test_public_*.py" -v
```

On macOS / Linux, substitute `python3` for `py -3`. Run the **manifest check on a pristine extracted release or fresh checkout**, before adding your `numbers.txt`. It checks both hashes and the strict public-file inventory: a local `numbers.txt` or generated output is intentionally not allowlisted and causes that check to fail. `.gitignore` does not make private files eligible for public release. On the main branch, `MANIFEST.json` also lists documentation added after the release, such as Addendum 1; the v1.0.0 release ZIP carries its own frozen manifest. Keep the pristine copy for release checking and use a separate working copy for decoding.

Run the checkers without `-O` or `-OO` and with `PYTHONOPTIMIZE` unset; they refuse optimized execution. The remaining public checks validate source/key integrity, synthetic cases, parsing, correction boundaries and implementation behavior. They do not need the historical ciphertext, do not reveal the complete message and do not rerun historical whole-book or GPU searches.

For the lower-level workflow, `code/prepare_original_input.py` authenticates and canonicalizes an original transcription; `code/ii1_verify.py` implements normalization, construction and decoding; and `code/check_reproduction_outputs.py` checks an output directory. The simple `decode.py` command delegates to those implementations rather than providing a second decoding algorithm. The public manifest inventories release files and hashes; it is not a scientific certification or rights grant.

For outputs produced with an alternate `decode.py --source` file, pass that same source to the standalone checker: `py -3 -B code/check_reproduction_outputs.py OUTPUT_DIR --source ACTUAL_SOURCE`. On macOS / Linux, use `python3`. The decoder supplies its actual source to the checker automatically; the standalone checker otherwise defaults to the bundled source. All three source-word annotation fields are checked against that source.

## Independent Replication and Subsequent Findings

On 4 November 2026 the independent researcher umbrellaid reported further checks of this reconstruction in a [public GitHub discussion](https://github.com/umbrellaid/decipher-money-hunt-research/issues/1#issuecomment-6631781113) ([clarification](https://github.com/umbrellaid/decipher-money-hunt-research/issues/1#issuecomment-6631922155)). [Addendum 1](paper/addenda/ADDENDUM_01.pdf) ([Markdown source](paper/addenda/ADDENDUM_01.md)) documents those findings and separates what was rechecked from what is reported.

- **Computational replication.** A separately written implementation of the published construction, importing no code from this repository, reproduced the published source, key and plaintext hashes and passed all 19 of its checks. It used this repository's published source paragraph and corrections.
- **Numerical transcription.** umbrellaid's separately made 314-value transcription differs from the original input only at observation 306, where it reads the photograph-supported `388`. With that value set to the compilation's `338`, it reproduces the published input fingerprint.
- **Textual witness.** umbrellaid identified Project Gutenberg eBook #829 as a third witness of the key paragraph. It normalizes to 491 letters rather than 492 (checked directly for the addendum), so it does not reproduce the key, which reinforces the report's finding that exact source wording matters.

These results support the reproducibility of the specified reconstruction. The complete decode remains conditional on the probable reading `830` at observation 169, where umbrellaid's transcription also reads `330`. The addendum does not change the reconstruction, the software or the v1.0.0 release. It is a separate supplement to the report, published on Zenodo with its own DOI, [10.5281/zenodo.23963541](https://doi.org/10.5281/zenodo.23963541). Cite the report for the reconstruction and the addendum for these later findings.

## Scope, attribution and citation

Actual-message reproduction requires separately obtaining the original numerical input. This is a **source-referenced reproduction workflow**, not a fully self-contained historical data bundle. The full ciphertext, full poem, ordered correspondence, original photographs, private transcripts and unrelated research are not distributed. Keep locally generated input and output files out of contributions and releases.

The key construction intentionally enables readers who obtain the ciphertext elsewhere to reconstruct the message. Public access to the ciphertext does not itself grant redistribution rights. The report quotes only an approved 21-character opening for scholarly commentary; third-party quotations are excluded from the CC BY 4.0 license on original report material. See [NOTICE.md](NOTICE.md), [rights inventory](RIGHTS_AND_LICENSING.md) and [licensing status](LICENSE_STATUS.md).

Please cite the research report as the principal publication:

> Eckman, C. A. (2026). *An Independent Reconstruction of Decipher II, Message 1 (1985–86).* Zenodo. https://doi.org/10.5281/zenodo.23844582

Published **31 October 2026** as a non-peer-reviewed research report. [CITATION.cff](CITATION.cff) provides the preferred report citation and software metadata. The corresponding software release is [v1.0.0](https://github.com/chriseckman/decipher-ii1-reconstruction/releases/tag/v1.0.0). A DOI identifies the deposited report; it does not indicate external peer review.

The separate supplement is cited as:

> Eckman, C. A. (2026). *Addendum 1: Independent Replication, Textual Witnesses, and Clue Interpretation.* Supplement to *An Independent Reconstruction of Decipher II, Message 1 (1985–86).* Zenodo. https://doi.org/10.5281/zenodo.23963541

Christopher A. Eckman — Independent Researcher — [ORCID 0009-0008-3325-4513](https://orcid.org/0009-0008-3325-4513). No external funding. No competing interests.
