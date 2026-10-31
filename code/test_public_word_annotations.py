"""Word-annotation regressions use invented numbers, never historical ciphertext."""
from pathlib import Path
import copy
import contextlib
import csv
import io
import hashlib
import re
import sys
import subprocess
import tempfile
import unittest
from unittest import mock
import unicodedata

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ii1_verify as V
import check_reproduction_outputs as C

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import decode as D


def invented_correspondence(source_text):
    source = V.normalize_source(source_text)
    key = V.build_key(source)
    original = [1 + ((i * 17 + 5) % 984) for i in range(314)]
    original[168], original[305] = 330, 338
    corrected, _ = V.apply_corrections(original, [
        {'position': 169, 'transcribed': 330, 'corrected': 830},
        {'position': 306, 'transcribed': 338, 'corrected': 388}])
    rows = V.correspondence(original, corrected, key, V.source_words(source_text))
    plain = V.decode(corrected, key)
    canonical = (', '.join(map(str, original)) + '.\n').encode('ascii')
    reference = {'sha256': hashlib.sha256(canonical).hexdigest(), 'bytes': len(canonical)}
    return rows, key, plain, reference


class TestWordAnnotations(unittest.TestCase):
    def setUp(self):
        self.bundled = (ROOT / 'inputs/source_transcription.txt').read_text(encoding='utf-8')

    def test_bundled_labels_and_every_synthetic_correspondence_byte_are_unchanged(self):
        # Baseline ASCII tokenizer, reproduced only in this synthetic regression.
        # Its historical/default labels and case must remain byte-for-byte equal.
        original = re.sub(r'-\s*\n\s*', '', unicodedata.normalize('NFKD', self.bundled))
        baseline, position = [], 1
        for match in re.finditer(r'[A-Za-z]+', original):
            baseline.append((position, match.group()))
            position += len(match.group())
        self.assertEqual(V.source_words(self.bundled), baseline)
        rows, key, plain, reference = invented_correspondence(self.bundled)
        numbers = [int(row['transcribed']) for row in rows]
        corrected = [int(row['corrected']) for row in rows]
        self.assertEqual(rows, V.correspondence(numbers, corrected, key, baseline))
        C.check_correspondence(rows, key, plain, reference)  # Backwards-compatible bundled default.

    def test_unicode_expansions_marks_and_line_hyphens_cover_all_984_positions(self):
        prefix = 'aı Café Straße ﬃ co-\noperate '
        source_text = prefix + 'z' * 467
        self.assertEqual(V.normalize_source(prefix), 'AICAFESTRASSEFFICOOPERATE')
        expected = [(1, 'aı'), (3, 'Cafe'), (7, 'Straße'), (14, 'ffi'),
                    (17, 'cooperate'), (26, 'z' * 467)]
        self.assertEqual(V.source_words(source_text), expected)
        source = V.normalize_source(source_text)
        self.assertEqual(len(source), 492)
        numbers = list(range(1, 985))
        rows = V.correspondence(numbers, numbers, V.build_key(source), V.source_words(source_text))
        expected_annotations = []
        for number, (_, word) in enumerate(expected, 1):
            size = (2, 4, 7, 3, 9, 467)[number - 1]
            expected_annotations.extend((number, word, i) for i in range(1, size + 1))
        for row in rows:
            index = row['source_letter_index']
            annotation = (row['source_word_number'], row['source_word'], row['letter_in_word'])
            self.assertEqual(annotation, expected_annotations[index - 1])
            self.assertEqual(row['plaintext_letter'], source[index - 1])

    def test_composed_and_decomposed_accents_have_identical_labels(self):
        composed = 'Café élite'
        decomposed = 'Cafe\u0301 e\u0301lite'
        self.assertEqual(V.source_words(composed), [(1, 'Cafe'), (5, 'elite')])
        self.assertEqual(V.source_words(composed), V.source_words(decomposed))

    def test_normalization_equivalent_dotless_i_has_full_annotation_coverage(self):
        alternate = self.bundled.replace('I', 'ı').replace('i', 'ı')
        self.assertEqual(V.normalize_source(alternate), V.normalize_source(self.bundled))
        lengths = [len(V.normalize_source(word)) for _, word in V.source_words(alternate)]
        self.assertEqual(sum(lengths), 492)
        rows, key, plain, reference = invented_correspondence(alternate)
        C.check_correspondence(rows, key, plain, reference, source_text=alternate)
        with self.assertRaisesRegex(AssertionError, 'Source word mismatch'):
            C.check_correspondence(rows, key, plain, reference)

    def test_case_equivalent_source_uses_its_actual_labels(self):
        alternate = self.bundled.upper()
        rows, key, plain, reference = invented_correspondence(alternate)
        C.check_correspondence(rows, key, plain, reference, source_text=alternate)
        with self.assertRaisesRegex(AssertionError, 'Source word mismatch'):
            C.check_correspondence(rows, key, plain, reference)

    def test_each_word_field_is_checked_on_every_row(self):
        rows, key, plain, reference = invented_correspondence(self.bundled)
        for position in range(314):
            for field, value in [('source_word_number', 0), ('source_word', 'CORRUPTED'),
                                 ('letter_in_word', 0)]:
                changed = copy.deepcopy(rows)
                changed[position][field] = value
                with self.subTest(position=position + 1, field=field), self.assertRaises(AssertionError):
                    C.check_correspondence(changed, key, plain, reference)

    def test_reader_passes_its_actual_unicode_source_to_output_checker(self):
        # Test the complete CLI plumbing with explicitly substituted synthetic
        # trust values. The shipped original-input fingerprint is not changed.
        alternate = self.bundled.replace('I', '\u0131').replace('i', '\u0131')
        rows, key, plain, reference = invented_correspondence(alternate)
        canonical = (', '.join(str(row['transcribed']) for row in rows) + '.\n').encode('ascii')
        hashes = {'key_source_492': V.sha256(key[:492]), 'key_984': V.sha256(key),
                  'plaintext_literal_314': V.sha256(plain)}

        def inspect_outputs(directory, source_path=None):
            self.assertIsNotNone(source_path)
            actual = source_path.read_text(encoding='utf-8')
            self.assertEqual(actual, alternate)
            with (directory / 'correspondence.csv').open(encoding='utf-8', newline='') as stream:
                actual_rows = list(csv.DictReader(stream))
            C.check_correspondence(actual_rows, key, plain, reference, source_text=actual)
            return {'result': 'PASS', 'source_positions_exercised': len({r['source_letter_index'] for r in rows}),
                    'numbered_slots_exercised': len({r['corrected'] for r in rows})}

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            numbers, source, output = root / 'invented.txt', root / 'alternate.txt', root / 'output'
            numbers.write_bytes(canonical)
            source.write_bytes(b'\xef\xbb\xbf' + alternate.encode('utf-8'))
            with mock.patch.object(D, 'validated_original_bytes', return_value=canonical), \
                 mock.patch.object(D, 'expected_output_hashes', return_value=hashes), \
                 mock.patch.object(D, 'verify_outputs', side_effect=inspect_outputs), \
                 contextlib.redirect_stdout(io.StringIO()) as printed:
                result = D.run_reader(numbers, source=source, output=output, show_text=False)
            self.assertEqual(result['result'], 'PASS')
            self.assertEqual((output / 'plaintext_literal_314.txt').read_bytes(), plain.encode('ascii'))
            self.assertNotIn(plain, printed.getvalue())

    def test_checker_isolated_cli_help_accepts_explicit_source(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, '-B', '-I', '-S',
                                     str(ROOT / 'code/check_reproduction_outputs.py'), '--help'],
                                    cwd=temp, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--source', result.stdout)

    def test_checker_rejects_source_whose_normalized_letters_differ(self):
        rows, key, plain, reference = invented_correspondence(self.bundled)
        with self.assertRaisesRegex(AssertionError, 'Source text does not match output key'):
            C.check_correspondence(rows, key, plain, reference, source_text='A' * 492)


if __name__ == '__main__':
    unittest.main()
