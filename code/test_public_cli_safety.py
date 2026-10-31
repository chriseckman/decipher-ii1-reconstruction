"""CLI boundary tests use invented input only, never historical ciphertext.

The staged-success test explicitly substitutes synthetic fingerprints and the
historical-result checker. It tests CLI plumbing, not historical reproduction.
"""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import decode as D


def invented_numbers():
    nums = [1 + ((i * 17 + 5) % 984) for i in range(314)]
    nums[168], nums[305] = 330, 338
    return nums


class TestReaderSafety(unittest.TestCase):
    def test_rejects_empty_comma_fields_and_non_numerical_material(self):
        base = ', '.join(map(str, invented_numbers()))
        bad = [',' + base, base + ',', base.replace(', ', ',,', 1),
               base.replace(', ', ', \n,', 1), base + '..', base + '\n492',
               base.replace('6', '6_0', 1), '\ufeff\ufeff' + base,
               'Puzzle 2-1\n' + base, '492\n' + base]
        for content in bad:
            with self.subTest(content=content[:30]), self.assertRaises(D.InputProblem):
                D.parse_user_numbers(content)

    def test_mixed_separators_and_utf8_bom_have_one_canonical_form(self):
        nums = invented_numbers()
        expected = (', '.join(map(str, nums)) + '.\n').encode('ascii')
        for separator in (', ', ',\r\n', '\t', '\n', ' , \n'):
            with self.subTest(separator=separator):
                raw = '\ufeff' + separator.join(map(str, nums)) + '.\r\n'
                self.assertEqual(D.original_input.canonical_bytes(raw), expected)

    def test_altered_and_reordered_sequences_fail_authentication(self):
        nums = invented_numbers()
        variants = [nums, [*reversed(nums)]]
        changed = nums.copy()
        changed[0], changed[1] = changed[1], changed[0]
        variants.append(changed)
        for numbers in variants:
            with self.subTest(variant=numbers[:2]), self.assertRaises(D.InputProblem):
                D.validated_original_bytes(','.join(map(str, numbers)))

    def test_corrections_cannot_be_preapplied(self):
        for position, working in ((168, 830), (305, 388)):
            nums = invented_numbers()
            nums[position] = working
            with self.subTest(position=position), self.assertRaisesRegex(D.InputProblem, 'Do not apply'):
                D.parse_user_numbers(','.join(map(str, nums)))

    def test_cli_help_works_in_isolated_mode_from_unrelated_directory(self):
        environment = os.environ.copy()
        environment.pop('PYTHONOPTIMIZE', None)
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, '-B', '-I', '-X', 'utf8', str(ROOT / 'decode.py'), '--help'],
                                    cwd=tmp, env=environment, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--output', result.stdout)
        self.assertIn('--no-print', result.stdout)

    def test_expected_user_errors_return_fail_without_traceback_or_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            path = directory / 'numbers.txt'
            output = directory / 'no-output'
            cases = [None, b'1,2,3', b'Puzzle 2-1\n1,2,3', b'\x89PNG\r\n',
                     ','.join(map(str, invented_numbers())).encode('ascii')]
            for content in cases:
                with self.subTest(content=repr(content)[:30]):
                    if content is not None:
                        path.write_bytes(content)
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr):
                        result = D.main([str(path), '-o', str(output), '--no-print'])
                    self.assertEqual(result, 2)
                    self.assertIn('FAIL', stderr.getvalue())
                    self.assertNotIn('Traceback', stderr.getvalue())
                    self.assertFalse(output.exists())

    def test_extension_does_not_turn_binary_image_into_numerical_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = Path(tmp) / 'pretend-text.txt'
            image.write_bytes(b'\x89PNG\r\n\x1a\n')
            error = io.StringIO()
            with contextlib.redirect_stderr(error):
                result = D.main([str(image), '-o', str(Path(tmp) / 'result')])
            self.assertEqual(result, 2)
            self.assertFalse((Path(tmp) / 'result').exists())

    def test_valid_synthetic_plumbing_strips_source_bom_before_verifier(self):
        # Synthetic trust values are patched only in this test. The shipping
        # CLI always authenticates the fixed historical fingerprint.
        nums = invented_numbers()
        canonical = D.original_input.canonical_bytes(','.join(map(str, nums)))
        digest = hashlib.sha256(canonical).hexdigest()
        corrected, _ = D.verifier.apply_corrections(nums, [
            {'position': 169, 'transcribed': 330, 'corrected': 830},
            {'position': 306, 'transcribed': 338, 'corrected': 388}])
        source = D.verifier.normalize_source((ROOT / 'inputs/source_transcription.txt').read_text(encoding='utf-8'))
        key = D.verifier.build_key(source)
        expected_text = D.verifier.decode(corrected, key)
        hashes = {'key_source_492': D.verifier.sha256(source), 'key_984': D.verifier.sha256(key),
                  'plaintext_literal_314': D.verifier.sha256(expected_text)}

        def check_synthetic(directory, source_path=None):
            self.assertEqual(source_path.read_text(encoding="utf-8"), (ROOT / "inputs/source_transcription.txt").read_text(encoding="utf-8"))
            self.assertEqual((directory / 'plaintext_literal_314.txt').read_bytes(), expected_text.encode('ascii'))
            self.assertEqual(len((directory / 'correspondence.csv').read_text().splitlines()), 315)
            return {'result': 'PASS', 'source_positions_exercised': len({D.verifier.source_index(n) for n in corrected}),
                    'numbered_slots_exercised': len(set(corrected))}

        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            inp = directory / 'numbers with spaces.txt'
            inp.write_bytes(b'\xef\xbb\xbf' + canonical)
            src = directory / 'source with BOM.txt'
            src.write_bytes(b'\xef\xbb\xbf' + (ROOT / 'inputs/source_transcription.txt').read_bytes())
            output = directory / 'new output'
            with mock.patch.object(D.original_input, 'EXPECTED', digest), \
                 mock.patch.object(D, 'expected_input_sha256', return_value=digest), \
                 mock.patch.object(D, 'expected_output_hashes', return_value=hashes), \
                 mock.patch.object(D, 'verify_outputs', side_effect=check_synthetic), \
                 contextlib.redirect_stdout(io.StringIO()) as printed:
                result = D.run_reader(inp, source=src, output=output, show_text=False)
            self.assertEqual(result['result'], 'PASS')
            self.assertNotIn(expected_text, printed.getvalue())
            self.assertIn('probable 830', printed.getvalue())
            self.assertEqual((output / 'plaintext_literal_314.txt').read_bytes(), expected_text.encode('ascii'))
            self.assertEqual(json.loads((output / 'verification.json').read_text())['sha256']['plaintext_literal_314'], hashes['plaintext_literal_314'])

    def test_default_output_is_home_not_checkout(self):
        with mock.patch.object(D, 'run_reader', return_value={}) as run:
            self.assertEqual(D.main(['invented.txt', '--no-print']), 0)
        self.assertEqual(run.call_args.kwargs['output'], Path.home() / 'Decipher-II1-local-result')

    def test_redirected_legacy_stdout_escapes_unicode_path_without_false_failure(self):
        # Exercise real Python pipe configuration but substitute the reader so
        # no historical ciphertext or decoded message becomes a test fixture.
        script = ("import sys; sys.path.insert(0, sys.argv[1]); import decode as D; "
                  "D.run_reader=lambda *a, **k: print('PASS: ' + str(k['output'])); "
                  "raise SystemExit(D.main(['unused.txt', '--output', sys.argv[2]]))")
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'cp1252'
        env.pop('PYTHONOPTIMIZE', None)
        result = subprocess.run([sys.executable, '-B', '-c', script, str(ROOT), 'results-\u4e2d\u6587'],
                                capture_output=True, env=env)
        self.assertEqual(result.returncode, 0, result.stderr.decode('cp1252'))
        self.assertIn(b'PASS: results-\\u4e2d\\u6587', result.stdout)
        self.assertNotIn(b'FAIL', result.stderr)

    def test_redirected_legacy_stderr_handles_unicode_missing_input(self):
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'cp1252'
        env.pop('PYTHONOPTIMIZE', None)
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / '\u4e2d\u6587-missing.txt'
            result = subprocess.run([sys.executable, '-B', str(ROOT / 'decode.py'), str(missing),
                                     '--output', str(Path(tmp) / 'new-output')],
                                    capture_output=True, env=env)
            self.assertFalse((Path(tmp) / 'new-output').exists())
        self.assertEqual(result.returncode, 2)
        self.assertIn(b'FAIL', result.stderr)
        self.assertIn(b'\\u4e2d\\u6587-missing.txt', result.stderr)
        self.assertNotIn(b'Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
