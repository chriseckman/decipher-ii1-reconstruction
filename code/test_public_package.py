"""Candidate-only implementation checks, not cryptanalytic performance tests."""
from pathlib import Path
import contextlib
import io
import json
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ii1_verify as V


class TestCandidateImplementation(unittest.TestCase):
    def test_nfkd_ascii_filter(self):
        self.assertEqual(V.normalize_source('com-\npasses, — Ill! 1911'), 'COMPASSESILL')
        self.assertEqual(V.normalize_source('é Ａ x'), 'EAX')

    def test_all_mirror_addresses(self):
        source = ''.join(chr(65 + (7 * i + 3) % 26) for i in range(492))
        key = V.build_key(source)
        for n in range(1, 985):
            expected = n if n <= 492 else 985 - n
            self.assertEqual(V.source_index(n), expected)
            self.assertEqual(key[n - 1], source[expected - 1])
        for invalid in [0, 985]:
            with self.assertRaises(ValueError):
                V.source_index(invalid)

    def test_correction_precondition(self):
        with self.assertRaises(ValueError):
            V.apply_corrections([10] * 314, [{'position': 169, 'transcribed': 11, 'corrected': 12}])

    def test_synthetic_cli_outputs(self):
        # Purely synthetic numbers/source; deliberately not the historical poem.
        source = ''.join(chr(65 + (7 * i + 3) % 26) for i in range(492))
        nums = [1 + (31 * i + 7) % 984 for i in range(314)]
        expected = ''.join(source[(n if n <= 492 else 985 - n) - 1] for n in nums)
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            (directory / 'synthetic-source.txt').write_text(source, encoding='ascii')
            (directory / 'synthetic-numbers.txt').write_text(','.join(map(str, nums)), encoding='ascii')
            (directory / 'synthetic-corrections.json').write_text(json.dumps({'corrections': []}), encoding='ascii')
            out = directory / 'new-output'
            with contextlib.redirect_stdout(io.StringIO()):
                code = V.main(['--ciphertext', str(directory / 'synthetic-numbers.txt'),
                    '--corrections', str(directory / 'synthetic-corrections.json'),
                    '--source', str(directory / 'synthetic-source.txt'), '--outdir', str(out)])
            self.assertEqual(code, 0)
            self.assertEqual((out / 'plaintext_literal_314.txt').read_text(), expected)
            self.assertEqual(len((out / 'correspondence.csv').read_text().splitlines()), 315)
            self.assertEqual(json.loads((out / 'verification.json').read_text())['sha256']['plaintext_literal_314'], V.sha256(expected))


if __name__ == '__main__':
    unittest.main()
