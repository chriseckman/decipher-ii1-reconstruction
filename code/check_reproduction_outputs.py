"""Check locally generated result files without printing the decoded message."""
from pathlib import Path
import argparse
from collections import Counter
import csv
import hashlib
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ii1_verify import normalize_source, source_words

if not __debug__:
    raise SystemExit('Checks require assertions: run without -O, -OO or PYTHONOPTIMIZE.')


def check_correspondence(rows, key, plaintext, reference, source_text=None):
    """Validate every row against its input fingerprint and actual source text.

    The bundled source is the backwards-compatible default. When a different
    source transcription was used, pass its exact text to check its word labels.
    """
    if source_text is None:
        root = Path(__file__).resolve().parent.parent
        source_text = (root / 'inputs/source_transcription.txt').read_text(encoding='utf-8-sig')
    source = normalize_source(source_text)
    assert len(source) == 492 and key == source + source[::-1], 'Source text does not match output key'
    annotations = []
    for word_number, (_, word) in enumerate(source_words(source_text), 1):
        annotations.extend((word_number, word, index)
                           for index in range(1, len(normalize_source(word)) + 1))
    assert len(annotations) == 492, 'Source-word annotation coverage mismatch'
    assert len(rows) == len(plaintext) == 314, 'Correspondence count mismatch'
    assert len(key) == 984, 'Correspondence key length mismatch'
    corrected = [int(row['corrected']) for row in rows]
    original = [int(row['transcribed']) for row in rows]
    assert all(1 <= number <= 984 for number in corrected + original), 'Correspondence number outside 1..984'
    canonical = (', '.join(map(str, original)) + '.\n').encode('ascii')
    assert hashlib.sha256(canonical).hexdigest() == reference['sha256'], 'Original input fingerprint mismatch'
    assert len(canonical) == reference['bytes'], 'Original input byte count mismatch'
    usage, available = Counter(corrected), Counter(key)
    correction_map = {169: (330, 830), 306: (338, 388)}
    for position, row in enumerate(rows, 1):
        old, number = original[position - 1], corrected[position - 1]
        index = number if number <= 492 else 985 - number
        letter = key[number - 1]
        assert int(row['position']) == position, f'Correspondence ordering mismatch at {position}'
        if position in correction_map:
            assert (old, number) == correction_map[position], f'Correction row mismatch at {position}'
        else:
            assert old == number, f'Unexpected correction at {position}'
        assert int(row['was_corrected']) == int(old != number), f'Correction flag mismatch at {position}'
        assert row['key_half'] == ('forward' if number <= 492 else 'reversed'), f'Key half mismatch at {position}'
        assert int(row['source_letter_index']) == index, f'Source index mismatch at {position}'
        word_number, word, letter_in_word = annotations[index - 1]
        assert int(row['source_word_number']) == word_number, f'Source word number mismatch at {position}'
        assert row['source_word'] == word, f'Source word mismatch at {position}'
        assert int(row['letter_in_word']) == letter_in_word, f'Letter-in-word mismatch at {position}'
        assert row['plaintext_letter'] == letter == plaintext[position - 1], f'Letter correspondence mismatch at {position}'
        assert int(row['numbers_available_for_letter']) == available[letter], f'Homophone count mismatch at {position}'
        assert int(row['uses_of_this_number']) == usage[number], f'Number usage mismatch at {position}'
        expected_positions = ' '.join(str(i + 1) for i, value in enumerate(corrected) if value == number)
        assert row['positions_using_this_number'] == expected_positions, f'Usage positions mismatch at {position}'


def check(directory, source_path=None):
    root = Path(__file__).resolve().parent.parent
    expected = json.loads((root / 'aggregate_results.json').read_text(encoding='utf-8'))['hashes']
    pairs = [('key_source_492.txt','key_source_492',492), ('key_984.txt','key_984',984), ('plaintext_literal_314.txt','plaintext_literal_314',314)]
    findings = {}
    payload = {}
    for filename, name, size in pairs:
        raw = (directory / filename).read_bytes()
        assert len(raw) == size, f'{filename}: size mismatch'
        assert all(65 <= ch <= 90 for ch in raw), f'{filename}: byte convention mismatch'
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == expected[name], f'{filename}: hash mismatch'
        findings[name] = digest
        payload[name] = raw.decode('ascii')
    meta = json.loads((directory / 'verification.json').read_text(encoding='utf-8'))
    assert all(meta['sha256'][k] == v for k,v in findings.items()), 'Metadata hash mismatch'
    assert meta['corrections_applied'] == [{'position':169,'from':330,'to':830}, {'position':306,'from':338,'to':388}], 'Correction mismatch'
    assert meta['uncorrected_decode_differs_at'] == [169,306], 'Input-comparison mismatch'
    expected_counts = {'source_letters':492,'key_positions':984,'ciphertext_numbers':314,'min_number':1,'max_number':980,'distinct_numbers':261,'numbers_in_forward_half':161,'numbers_in_reversed_half':153,'plaintext_letters':314}
    assert meta['counts'] == expected_counts, 'Aggregate count mismatch'
    with (directory / 'correspondence.csv').open(encoding='utf-8', newline='') as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 314, 'Correspondence count mismatch'
    slots = {int(r['corrected']) for r in rows}
    positions = {int(r['source_letter_index']) for r in rows}
    assert len(slots) == 261 and len(positions) == 224, 'Coverage mismatch'
    key, plaintext = payload['key_984'], payload['plaintext_literal_314']
    reference = json.loads((root / 'INPUT_REFERENCE.json').read_text(encoding='utf-8'))['original_input']
    if source_path is None:
        source_path = root / 'inputs/source_transcription.txt'
    source_text = Path(source_path).read_text(encoding='utf-8-sig')
    check_correspondence(rows, key, plaintext, reference, source_text)
    return {'result':'PASS', 'hashes':findings, 'observations':314, 'source_positions_exercised':224,'numbered_slots_exercised':261,
            'scope':'Conditional fixed-rule reproduction; digit certainty and historical searches not adjudicated.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('directory', type=Path)
    ap.add_argument('--source', type=Path, help='Actual literary-source transcription used to generate these outputs (defaults to the bundled source)')
    args = ap.parse_args()
    print(json.dumps(check(args.directory, args.source), indent=2))


if __name__ == '__main__':
    main()
