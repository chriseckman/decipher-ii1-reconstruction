"""Tampered correspondence tests use an invented 314-number stream."""
from pathlib import Path
import copy
import hashlib
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ii1_verify as V
import check_reproduction_outputs as C


class TestCorrespondenceChecks(unittest.TestCase):
    def setUp(self):
        self.source = ''.join(chr(65 + (7 * i + 3) % 26) for i in range(492))
        self.key = V.build_key(self.source)
        original = [1 + ((i * 17 + 5) % 984) for i in range(314)]
        original[168], original[305] = 330, 338
        corrected, _ = V.apply_corrections(original, [
            {'position': 169, 'transcribed': 330, 'corrected': 830},
            {'position': 306, 'transcribed': 338, 'corrected': 388}])
        self.rows = V.correspondence(original, corrected, self.key, [(1, self.source)])
        self.plaintext = V.decode(corrected, self.key)
        serialized = (', '.join(map(str, original)) + '.\n').encode('ascii')
        self.reference = {'sha256': hashlib.sha256(serialized).hexdigest(), 'bytes': len(serialized)}

    def test_valid_synthetic_correspondence(self):
        C.check_correspondence(self.rows, self.key, self.plaintext, self.reference, self.source)

    def test_tampering_each_critical_correspondence_field_is_detected(self):
        changes = {'position': 0, 'transcribed': 985, 'corrected': 985, 'was_corrected': 1,
                   'key_half': 'reversed', 'source_letter_index': 0, 'plaintext_letter': '?',
                   'numbers_available_for_letter': 0, 'uses_of_this_number': 0, 'positions_using_this_number': ''}
        for field, value in changes.items():
            with self.subTest(field=field):
                rows = copy.deepcopy(self.rows)
                rows[0][field] = value
                with self.assertRaises(AssertionError):
                    C.check_correspondence(rows, self.key, self.plaintext, self.reference, self.source)

    def test_ordering_original_fingerprint_and_missing_rows_are_checked(self):
        variants = [self.rows[::-1], self.rows[:-1]]
        rows = copy.deepcopy(self.rows)
        rows[0]['transcribed'] = 2
        variants.append(rows)
        for rows in variants:
            with self.subTest(length=len(rows)), self.assertRaises(AssertionError):
                C.check_correspondence(rows, self.key, self.plaintext, self.reference, self.source)


if __name__ == '__main__':
    unittest.main()
