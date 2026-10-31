#!/usr/bin/env python3
"""Reader-friendly local Decipher II-1 reconstruction.

Accept a reader-supplied, plain-text 314-number transcription as TXT/CSV.
The published literary source and correction specification are bundled.
The historical input is deliberately *not* bundled or downloaded. This
program does not recognize images or attempt OCR.

This front end authenticates the complete numerical input and verifies output
hashes before reporting success. It delegates all key construction and
number-to-letter correspondence to the unchanged ii1_verify.py implementation.
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

if sys.version_info < (3, 10):
    raise SystemExit("Decipher II-1 requires Python 3.10 or newer. Install a current Python 3 release and try again.")

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "code"))
import ii1_verify as verifier  # noqa: E402
import prepare_original_input as original_input  # noqa: E402
from check_reproduction_outputs import check as verify_outputs  # noqa: E402


class InputProblem(ValueError):
    """An actionable user-input/setup problem, not a decoder traceback."""


def expected_input_sha256() -> str:
    info = json.loads((ROOT / "INPUT_REFERENCE.json").read_text(encoding="utf-8"))
    expected = info["original_input"]["sha256"]
    if expected != original_input.EXPECTED:
        raise InputProblem("INPUT_REFERENCE.json does not match the recorded original-input fingerprint. Restore the released package.")
    return expected


def expected_output_hashes() -> dict[str, str]:
    info = json.loads((ROOT / "aggregate_results.json").read_text(encoding="utf-8"))
    return info["hashes"]


def parse_user_numbers(raw: str) -> list[int]:
    """Accept comma- or whitespace-delimited numbers with optional final period.

    Deliberately reject other prose such as document headings and clues rather
    than extracting possibly wrong numbers from them.
    """
    try:
        return original_input.parse_original_numbers(raw)
    except ValueError as exc:
        raise InputProblem(str(exc)) from exc


def validated_original_bytes(raw: str) -> bytes:
    expected_input_sha256()  # Bind the public reference to the fixed fingerprint.
    try:
        return original_input.validated_original_bytes(raw)
    except ValueError as exc:
        raise InputProblem(str(exc)) from exc


def run_reader(cipher_input: Path, *, source: Path, output: Path, show_text: bool) -> dict:
    if not cipher_input.is_file():
        raise InputProblem(f"No such ciphertext input: {cipher_input}")
    if not source.is_file():
        raise InputProblem(f"No source text file: {source}. The exact source is bundled in inputs/source_transcription.txt.")
    if output.exists():
        raise InputProblem(f"Output directory already exists: {output}. Choose a fresh --output path to avoid overwriting results.")
    source_text = source.read_text(encoding="utf-8-sig")
    src = verifier.normalize_source(source_text)
    expected_src = expected_output_hashes()["key_source_492"]
    if len(src) != 492 or verifier.sha256(src) != expected_src:
        raise InputProblem(
            "The supplied literary source does not match the verified 492-letter passage. "
            "Use the bundled inputs/source_transcription.txt, or verify your source's exact wording, including 'take my measure'."
        )
    if cipher_input.suffix.lower() not in {".txt", ".csv"}:
        raise InputProblem(
            f"Unsupported input type {cipher_input.suffix or '(none)'}. "
            "This text-only decoder accepts .txt or .csv files, not images or PDFs. "
            "Copy the original 314 numbers from Kavett's public 'Puzzle 2-1' text "
            "into a plain-text file named numbers.txt, then run: python decode.py numbers.txt"
        )
    original = validated_original_bytes(cipher_input.read_text(encoding="utf-8-sig"))
    corrections = ROOT / "inputs" / "corrections.json"
    correction_data = json.loads(corrections.read_text(encoding="utf-8"))
    required = [{"position": 169, "transcribed": 330, "corrected": 830},
                {"position": 306, "transcribed": 338, "corrected": 388}]
    if correction_data.get("corrections") != required:
        raise InputProblem("The correction specification differs from the two documented working corrections. Restore inputs/corrections.json.")
    with tempfile.TemporaryDirectory(prefix="decipher_ii1_reader_") as tmp:
        inp = Path(tmp) / "original_transcription.txt"
        inp.write_bytes(original)
        # Match validation to execution: strip an optional UTF-8 BOM once, then
        # hand precisely that text to the authoritative verifier. No second
        # implementation of the key or decoding algorithm is used here.
        clean_source = Path(tmp) / "source_transcription.txt"
        clean_source.write_bytes(source_text.encode("utf-8"))
        result = verifier.run(inp, corrections, clean_source)
        for name, digest in expected_output_hashes().items():
            if result["sha256"][name] != digest:
                raise InputProblem(f"Internal output verification failed: {name} did not match its recorded hash. No output directory was created.")
        checked_output = Path(tmp) / "checked-output"
        verifier.write_outputs(result, checked_output)
        try:
            verified = verify_outputs(checked_output, source_path=clean_source)
        except (AssertionError, KeyError, ValueError) as exc:
            raise InputProblem(f"Internal output checks failed: {exc}. No output directory was created.") from exc
        # Only copy the already checked, deterministic result after every
        # validation succeeds. write_outputs refuses existing directories.
        verifier.write_outputs(result, output)
    print(f"\nDECIPHER II-1 RECONSTRUCTION: {verified['result']}")
    print(f"Output files: {output.resolve()}")
    print("Plaintext: plaintext_literal_314.txt (314 uppercase letters; original spacing/punctuation is not encoded)")
    if show_text:
        print("\nRecovered plaintext (literal, no editorial spacing):")
        print(result["_plaintext"])
    print(f"\nSource, key and plaintext SHA-256: VERIFIED. Source positions used: {verified['source_positions_exercised']}/492; key slots: {verified['numbered_slots_exercised']}/984.")
    print("Note: observation 169 uses probable 830, not a blind-confirmed photographic reading.")
    print("Local generated input/output/poem files are not part of the public release package.")
    return verified


def main(argv: list[str] | None = None) -> int:
    # Windows pipes may use a legacy encoding even when filenames are Unicode.
    # Preserve that encoding but escape unsupported characters instead of
    # reporting failure after a successful decode merely while printing a path.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(
        description="Reproduce Decipher II-1 from a plain-text copy of the 314 original ciphertext numbers.",
        epilog=(
            "First: copy ONLY the numbers under 'Puzzle 2-1' in Karen Kavett's public research "
            "compilation into numbers.txt (no headings; do not correct digits yourself).\n"
            "Examples:\n"
            "  python decode.py numbers.txt\n"
            "  python decode.py numbers.txt --output ../new-local-result\n"
            "The verified literary source and correction specification are already supplied. "
            "No OCR, GPU, additional packages, or network request is used by this program."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("ciphertext", type=Path, help="Local UTF-8 .txt or .csv file containing only the original 314 numbers")
    parser.add_argument("--source", type=Path, default=ROOT / "inputs/source_transcription.txt", help="Optional alternative transcription of the same literary source paragraph")
    parser.add_argument("--output", "-o", type=Path, default=Path.home() / "Decipher-II1-local-result", help="Fresh output directory; defaults to a folder in your home directory")
    parser.add_argument("--no-print", action="store_true", help="Save the plaintext without printing it to the terminal")
    args = parser.parse_args(argv)
    try:
        run_reader(args.ciphertext, source=args.source, output=args.output, show_text=not args.no_print)
    except (ValueError, OSError, UnicodeError, KeyError, TypeError, AssertionError) as exc:
        print(f"\nDECIPHER II-1 RECONSTRUCTION: FAIL\nERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
