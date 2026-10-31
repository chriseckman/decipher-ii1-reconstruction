"""Accepted three-check reversal supplement with package-local import only.

Synthetic input; no frozen release or historical ciphertext dependency.
"""
from pathlib import Path
import sys
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ii1_verify as V


class TestVariedReversal(unittest.TestCase):
    def setUp(self):
        self.source = ''.join(chr(65 + (7 * i + 3) % 26) for i in range(492))
        self.assertEqual(len(set(self.source)), 26)
        self.assertNotEqual(self.source, self.source[::-1])
        self.assertNotEqual(self.source[0], self.source[-1])

    def assert_numbering(self, key):
        self.assertEqual(len(key), 984)
        self.assertEqual(key[:492], self.source)
        self.assertEqual(key[492:], self.source[::-1])
        self.assertEqual(key[491], self.source[-1])
        self.assertEqual(key[492], self.source[-1])
        self.assertEqual(key[-1], self.source[0])

    def test_working_verifier_reverses_varied_source(self):
        self.assert_numbering(V.build_key(self.source))

    def test_detects_unreversed_second_half(self):
        with self.assertRaises(AssertionError):
            self.assert_numbering(self.source + self.source)

    def test_detects_wrong_turnaround(self):
        wrong = self.source + self.source[-2::-1] + self.source[0]
        with self.assertRaises(AssertionError):
            self.assert_numbering(wrong)


if __name__ == '__main__':
    unittest.main()
