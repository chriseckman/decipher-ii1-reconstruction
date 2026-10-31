"""Prepare a separately obtained transcription without downloading or decoding it."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ii1_verify as V

EXPECTED = '1e60d5d63422148b385abfd0569edb1c709308eb79d51e4195b6c8a781be2edc'


def parse_original_numbers(text):
    """Accept only ASCII integers separated by commas or whitespace.

    A single final period and one initial UTF-8 BOM are allowed. Commas must
    separate numbers: an empty field is never silently dropped.
    """
    body = text.removeprefix('\ufeff').strip()
    if body.endswith('.'):
        body = body[:-1].rstrip()
    if not body:
        raise ValueError("No ciphertext numbers found. Copy only the 'Puzzle 2-1' numbers, not its heading.")
    if re.search(r'[^0-9,\s]', body):
        raise ValueError('Input contains non-number characters. Copy only the 314-number sequence, without headings or clues.')
    if not re.fullmatch(r'[0-9]+(?:(?:\s*,\s*|\s+)[0-9]+)*', body):
        raise ValueError('Malformed separators: use commas or whitespace between numbers; do not leave empty comma fields.')
    tokens = re.split(r'[,\s]+', body)
    if len(tokens) != V.N_CIPHER:
        raise ValueError(f'Found {len(tokens)} numbers, but Decipher II-1 needs exactly 314. Check for missing or extra numbers.')
    numbers = [int(token) for token in tokens]
    for position, number in enumerate(numbers, 1):
        if not 1 <= number <= V.N_KEY:
            raise ValueError(f'Number at observation {position} is {number}; valid key positions are 1-984.')
    if (numbers[168], numbers[305]) != (330, 338):
        raise ValueError('Original-value preconditions failed: observation 169 must be 330 and 306 must be 338. Do not apply the 830/388 corrections yourself.')
    return numbers


def canonical_bytes(text):
    numbers = parse_original_numbers(text)
    return (', '.join(str(n) for n in numbers) + '.\n').encode('ascii')


def validated_original_bytes(text):
    content = canonical_bytes(text)
    digest = hashlib.sha256(content).hexdigest()
    if digest != EXPECTED:
        raise ValueError('The 314-number sequence differs from the verified Puzzle 2-1 transcription. '
                         f'Canonical SHA-256 is {digest}; expected {EXPECTED}. '
                         'Recheck the copied values and their order; decoding was NOT performed.')
    return content


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('transcription', type=Path)
    ap.add_argument('output', type=Path)
    args = ap.parse_args()
    # The helper accepts UTF-8 with an optional BOM, then writes strict ASCII
    # canonical input for ii1_verify.run; the direct verifier input stays ASCII.
    try:
        content = validated_original_bytes(args.transcription.read_text(encoding='utf-8-sig'))
        with args.output.open('xb') as stream:
            stream.write(content)
    except (OSError, UnicodeError, ValueError) as exc:
        ap.error(str(exc))
    digest = hashlib.sha256(content).hexdigest()
    print(json.dumps({'original_input_sha256': digest, 'bytes': len(content), 'numbers':314, 'corrections_applied':False}))


if __name__ == '__main__':
    main()
