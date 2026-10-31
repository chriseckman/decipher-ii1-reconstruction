"""Deterministic verification of the Decipher II-1 reconstruction.

Inputs (never the proposed plaintext):
  --ciphertext   the original community transcription of Message 1: one line of 314 comma-separated integers
  --corrections  JSON correction specification {position (1-based), transcribed, corrected}:
                position 169 uses probable 830 (330 remains competing); position 306 uses photograph-supported 388
  --source       a transcription of the key passage (the Gulliver's Travels III.2 tailor paragraph)

Normalization (KEY_RULE): Unicode NFKD, uppercase, keep only the 26 ASCII letters A-Z; everything else (spaces,
punctuation, dashes, digits, line-break hyphens, newlines) is dropped. The result must have exactly 492 letters.

Key (984 positions): K = S + reverse(S), where S is the normalized 492-letter source. Number n (1..984) denotes K[n-1]:
  n <= 492  -> source letter n (forward numbering)
  n >= 493  -> source letter 985 - n (the reversed copy; 493 is source letter 492, 984 is source letter 1)

Decoding: plaintext[i] = K[c_i - 1] for every corrected ciphertext integer c_i.

Byte conventions for hashes: ASCII uppercase letters only, no separators, no trailing newline.
Outputs written to --outdir (which must not exist): key_source_492.txt, key_984.txt, plaintext_literal_314.txt,
correspondence.csv (UTF-8, LF), verification.json.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

N_SOURCE = 492
N_KEY = 2 * N_SOURCE
N_CIPHER = 314


def parse_ciphertext(text: str) -> list[int]:
    """Parse 'n1, n2, ..., n314.' into integers (a single trailing period is allowed)."""
    body = text.strip()
    if body.endswith("."):
        body = body[:-1]
    nums = [int(tok.strip()) for tok in body.split(",")]
    if len(nums) != N_CIPHER:
        raise ValueError(f"expected {N_CIPHER} numbers, found {len(nums)}")
    return nums


def apply_corrections(nums: list[int], corrections: list[dict]) -> tuple[list[int], list[dict]]:
    out = list(nums)
    applied = []
    for c in corrections:
        p = int(c["position"])
        if not 1 <= p <= len(out):
            raise ValueError(f"position {p} outside 1..{len(out)}")
        if out[p - 1] != int(c["transcribed"]):
            raise ValueError(f"position {p}: transcription has {out[p - 1]}, correction expects {c['transcribed']}")
        out[p - 1] = int(c["corrected"])
        applied.append({"position": p, "from": int(c["transcribed"]), "to": int(c["corrected"])})
    return out, applied


def normalize_source(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).upper()
    return "".join(ch for ch in t if "A" <= ch <= "Z")


def source_words(text: str) -> list[tuple[int, str]]:
    """Return source words and their one-based *normalized-letter* starts.

    Preserve the bundled ASCII spelling/case and join line-break hyphenation.
    Combining marks do not split a word. A character contributes exactly the
    ASCII letters contributed by normalize_source, including case expansions
    (for example, sharp s contributes two positions and dotless i contributes
    one). Word labels retain NFKD spelling with combining marks omitted;
    letter_in_word counts normalized letters rather than Unicode code points.
    """
    text = re.sub(r"-\s*\n\s*", "", text)
    t = unicodedata.normalize("NFKD", text)
    out: list[tuple[int, str]] = []
    chars: list[str] = []
    word_start, position = 1, 0
    for ch in t:
        letters = normalize_source(ch)
        if letters:
            if not chars:
                word_start = position + 1
            chars.append(ch)
            position += len(letters)
        elif unicodedata.category(ch).startswith("M"):
            continue  # Decomposed accents do not create word boundaries.
        elif chars:
            out.append((word_start, "".join(chars)))
            chars = []
    if chars:
        out.append((word_start, "".join(chars)))
    if position != len(normalize_source(text)):
        raise ValueError("source-word indexing differs from normalized source length")
    return out


def build_key(source_letters: str) -> str:
    if len(source_letters) != N_SOURCE:
        raise ValueError(f"source has {len(source_letters)} letters, expected {N_SOURCE}")
    return source_letters + source_letters[::-1]


def source_index(n: int) -> int:
    """1-based source letter index for cipher number n (1..984)."""
    if not 1 <= n <= N_KEY:
        raise ValueError(f"number {n} outside 1..{N_KEY}")
    return n if n <= N_SOURCE else (N_KEY + 1) - n


def decode(nums: list[int], key: str) -> str:
    for n in nums:
        source_index(n)  # Reject negative/zero indices before Python can wrap them.
    return "".join(key[n - 1] for n in nums)


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("ascii")).hexdigest()


def correspondence(original: list[int], corrected: list[int], key: str, words: list[tuple[int, str]]) -> list[dict]:
    starts = [w[0] for w in words]
    homophones = {ch: [i + 1 for i, c in enumerate(key) if c == ch] for ch in set(key)}
    uses: dict[int, list[int]] = {}
    for i, n in enumerate(corrected):
        uses.setdefault(n, []).append(i + 1)
    rows = []
    for i, (o, n) in enumerate(zip(original, corrected)):
        s = source_index(n)
        w = max(j for j, st in enumerate(starts) if st <= s)
        letter = key[n - 1]
        rows.append({
            "position": i + 1, "transcribed": o, "corrected": n, "was_corrected": int(o != n),
            "key_half": "forward" if n <= N_SOURCE else "reversed",
            "source_letter_index": s, "source_word_number": w + 1, "source_word": words[w][1],
            "letter_in_word": s - starts[w] + 1, "plaintext_letter": letter,
            "numbers_available_for_letter": len(homophones[letter]),
            "uses_of_this_number": len(uses[n]), "positions_using_this_number": " ".join(map(str, uses[n])),
        })
    return rows


def run(ciphertext_path: Path, corrections_path: Path, source_path: Path) -> dict:
    # Use prepare_original_input.py first for downloaded UTF-8/BOM transcriptions.
    original = parse_ciphertext(ciphertext_path.read_text(encoding="ascii"))
    corr = json.loads(corrections_path.read_text(encoding="utf-8"))["corrections"]
    corrected, applied = apply_corrections(original, corr)
    source_text = source_path.read_text(encoding="utf-8")
    src = normalize_source(source_text)
    key = build_key(src)
    plain = decode(corrected, key)
    plain_uncorrected = decode(original, key)
    rows = correspondence(original, corrected, key, source_words(source_text))
    # internal consistency: every number decodes to its letter; repeated numbers carry one letter
    assert all(key[r["corrected"] - 1] == r["plaintext_letter"] for r in rows)
    by_num: dict[int, set] = {}
    for r in rows:
        by_num.setdefault(r["corrected"], set()).add(r["plaintext_letter"])
    assert all(len(v) == 1 for v in by_num.values())
    return {
        "inputs_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (ciphertext_path, corrections_path, source_path)},
        "rule": "K = S + reverse(S); n<=492 -> S[n]; n>=493 -> S[985-n]; plaintext[i] = K[c_i - 1]",
        "normalization": "NFKD, uppercase, keep ASCII A-Z only",
        "counts": {"source_letters": len(src), "key_positions": len(key), "ciphertext_numbers": len(corrected),
                   "max_number": max(corrected), "min_number": min(corrected), "distinct_numbers": len(set(corrected)),
                   "numbers_in_forward_half": sum(n <= N_SOURCE for n in corrected), "numbers_in_reversed_half": sum(n > N_SOURCE for n in corrected),
                   "plaintext_letters": len(plain)},
        "corrections_applied": applied,
        "uncorrected_decode_differs_at": [i + 1 for i, (a, b) in enumerate(zip(plain, plain_uncorrected)) if a != b],
        "sha256": {"key_source_492": sha256(src), "key_984": sha256(key), "plaintext_literal_314": sha256(plain),
                   "plaintext_literal_314_lowercase": sha256(plain.lower())},
        "_key_source": src, "_key": key, "_plaintext": plain, "_rows": rows,
    }


def write_outputs(res: dict, outdir: Path) -> None:
    # Serialize before reserving the output directory. A bad result cannot
    # leave a partial directory, and existing output is never overwritten.
    payloads = {"key_source_492.txt": res["_key_source"].encode("ascii"),
                "key_984.txt": res["_key"].encode("ascii"),
                "plaintext_literal_314.txt": res["_plaintext"].encode("ascii")}
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=list(res["_rows"][0].keys()), lineterminator="\n")
    w.writeheader(); w.writerows(res["_rows"])
    payloads["correspondence.csv"] = buf.getvalue().encode("utf-8")
    public = {k: v for k, v in res.items() if not k.startswith("_")}
    payloads["verification.json"] = (json.dumps(public, indent=1) + "\n").encode("utf-8")
    outdir.mkdir(parents=True, exist_ok=False)
    owned = []
    try:
        for name, content in payloads.items():
            path = outdir / name
            with path.open("xb") as stream:
                owned.append(path)
                stream.write(content)
    except BaseException:
        # Delete only files successfully opened by this call. Never recursively
        # remove a directory that could contain another process's files.
        for path in owned:
            try:
                path.unlink()
            except OSError:
                pass
        try:
            outdir.rmdir()
        except OSError:
            pass
        raise


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ciphertext", required=True, type=Path)
    ap.add_argument("--corrections", required=True, type=Path)
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--outdir", required=True, type=Path)
    a = ap.parse_args(argv)
    res = run(a.ciphertext, a.corrections, a.source)
    write_outputs(res, a.outdir)
    print(json.dumps({k: v for k, v in res.items() if not k.startswith("_")}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
