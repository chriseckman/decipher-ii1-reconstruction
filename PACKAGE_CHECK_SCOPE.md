# Verification and reproducibility scope

The public files support source/key checks, synthetic regression tests and exact file-manifest checks with Python 3.10 or later and no third-party dependencies. The simple text-only application authenticates the entire reader-supplied original ciphertext before decoding and verifies the resulting hashes and all 314 correspondences.

Actual-message reproduction requires separately obtaining the original numerical transcription, as described in [README.md](README.md). The working corrections include probable 830 at observation 169 and photograph-supported 388 at 306. Output equality does not independently authenticate the uncertain digit, unused mappings, the designer's edition or historical priority.

Historical search implementations, trained scorers and corpora are not included. The software does not replay the whole-book/GPU searches, repair comparisons or statistical calibration experiments; reported failed gates and exploratory limits remain in the [paper](paper/PAPER_A.md) and [supplement](paper/PUBLIC_SUPPLEMENT.md). The earlier nondiscriminating reversal fixture remains a disclosed limitation.

The full ciphertext, complete message, ordered correspondence, restricted images and private transcripts are excluded from the release. The mathematical construction permits decoding of input obtained elsewhere. Locally generated inputs/outputs are private working files and must not be added to a release. The strict manifest checker intentionally rejects unlisted files, including a reader's numbers.txt; use a pristine extraction for that check. Licensing is addressed in [LICENSE_STATUS.md](LICENSE_STATUS.md) and third-party exclusions in [NOTICE.md](NOTICE.md).
