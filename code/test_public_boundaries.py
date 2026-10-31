"""Synthetic regression tests for input boundaries and checker execution safety."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ii1_verify as V


CODE = Path(__file__).resolve().parent


def synthetic_source():
    return ''.join(chr(65 + (7 * i + 3) % 26) for i in range(492))


def synthetic_run(directory, corrections=None):
    directory = Path(directory)
    source = directory / 'synthetic-source.txt'
    numbers = directory / 'synthetic-numbers.txt'
    correction_file = directory / 'synthetic-corrections.json'
    source.write_bytes(synthetic_source().encode('ascii'))
    numbers.write_bytes(','.join(['1'] * 314).encode('ascii'))
    correction_file.write_bytes(json.dumps({'corrections': corrections or []}).encode('utf-8'))
    return V.run(numbers, correction_file, source)


class TestInputAndOutputBoundaries(unittest.TestCase):
    def test_source_length_rejects_491_and_493(self):
        for size in (491, 493):
            with self.subTest(size=size), self.assertRaisesRegex(ValueError, 'expected 492'):
                V.build_key('A' * size)

    def test_correction_positions_reject_non_one_based_indices(self):
        for position in (-1, 0, 315):
            with self.subTest(position=position), self.assertRaisesRegex(ValueError, 'outside 1..314'):
                V.apply_corrections([1] * 314, [
                    {'position': position, 'transcribed': 1, 'corrected': 2}])

    def test_decode_rejects_out_of_range_numbers(self):
        key = V.build_key(synthetic_source())
        for number in (-1, 0, 985, 986):
            with self.subTest(number=number), self.assertRaisesRegex(ValueError, 'outside 1..984'):
                V.decode([number], key)

    def test_synthetic_correction_changes_only_intended_observation(self):
        original = [1] * 314
        specification = [{'position': 169, 'transcribed': 1, 'corrected': 2}]
        corrected, applied = V.apply_corrections(original, specification)
        self.assertEqual(original, [1] * 314)  # Input is preserved.
        self.assertEqual([i + 1 for i, (a, b) in enumerate(zip(original, corrected)) if a != b], [169])
        self.assertEqual(corrected[168], 2)
        self.assertEqual(applied, [{'position': 169, 'from': 1, 'to': 2}])
        with tempfile.TemporaryDirectory() as temp:
            result = synthetic_run(temp, specification)
        self.assertEqual(result['uncorrected_decode_differs_at'], [169])
        self.assertEqual(result['corrections_applied'], applied)
        row = result['_rows'][168]
        self.assertEqual((row['position'], row['transcribed'], row['corrected'], row['was_corrected']),
                         (169, 1, 2, 1))

    def test_correspondence_half_and_mirrored_source_index(self):
        source = synthetic_source()
        key = V.build_key(source)
        numbers = [1, 492, 493, 984, 494, 491]
        rows = V.correspondence(numbers, numbers, key, [(1, source)])
        expected = [('forward', 1), ('forward', 492), ('reversed', 492),
                    ('reversed', 1), ('reversed', 491), ('forward', 491)]
        for number, row, (half, index) in zip(numbers, rows, expected):
            with self.subTest(number=number):
                self.assertEqual(row['key_half'], half)
                self.assertEqual(row['source_letter_index'], index)
                self.assertEqual(row['letter_in_word'], index)
                self.assertEqual(row['plaintext_letter'], source[index - 1])

    def test_existing_output_directory_is_preserved_and_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            result = synthetic_run(directory)
            output = directory / 'existing-output'
            output.mkdir()
            sentinel = output / 'key_source_492.txt'
            sentinel.write_bytes(b'original bytes must survive')
            with self.assertRaises(FileExistsError):
                V.write_outputs(result, output)
            self.assertEqual(sentinel.read_bytes(), b'original bytes must survive')
            self.assertEqual(list(output.iterdir()), [sentinel])

    def test_input_preparation_imports_in_isolated_mode(self):
        environment = os.environ.copy()
        environment.pop('PYTHONOPTIMIZE', None)
        completed = subprocess.run(
            [sys.executable, '-B', '-I', '-X', 'utf8', str(CODE / 'prepare_original_input.py'), '--help'],
            capture_output=True, text=True, encoding='utf-8', env=environment, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn('transcription', completed.stdout)
        self.assertNotIn('ModuleNotFoundError', completed.stderr)

    def test_failed_output_write_cleans_only_its_owned_files(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            result = synthetic_run(root)
            output = root / 'new-output'
            real_open = Path.open

            def fail_second_file(path, *args, **kwargs):
                if path == output / 'key_984.txt':
                    raise OSError('synthetic disk failure')
                return real_open(path, *args, **kwargs)

            with mock.patch.object(Path, 'open', fail_second_file):
                with self.assertRaisesRegex(OSError, 'synthetic disk failure'):
                    V.write_outputs(result, output)
            self.assertFalse(output.exists())
            self.assertTrue((root / 'synthetic-numbers.txt').is_file())


class TestCheckerOptimizationSafety(unittest.TestCase):
    def test_both_checkers_refuse_optimized_execution_on_tampered_data(self):
        # Only synthetic output is created. No historical message/input is read.
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            code = root / 'code'
            code.mkdir()
            inputs = root / 'inputs'
            inputs.mkdir()
            for name in ('check_public_materials.py', 'check_reproduction_outputs.py', 'ii1_verify.py'):
                shutil.copyfile(CODE / name, code / name)
            (root / 'aggregate_results.json').write_bytes(json.dumps({'hashes': {
                'key_source_492': '0' * 64, 'key_984': '0' * 64,
                'plaintext_literal_314': '0' * 64}}).encode('utf-8'))
            (inputs / 'source_transcription.txt').write_bytes(b'A' * 492)
            wrong_output = root / 'wrong-output'
            wrong_output.mkdir()
            (wrong_output / 'key_source_492.txt').write_bytes(b'A' * 492)
            (wrong_output / 'key_984.txt').write_bytes(b'A' * 984)
            (wrong_output / 'plaintext_literal_314.txt').write_bytes(b'A' * 314)
            cases = [('check_public_materials.py', []),
                     ('check_reproduction_outputs.py', [str(wrong_output)])]
            for name, arguments in cases:
                for mode in ('-O', 'PYTHONOPTIMIZE=1'):
                    with self.subTest(checker=name, mode=mode):
                        environment = os.environ.copy()
                        environment.pop('PYTHONOPTIMIZE', None)
                        flags = ['-B', '-X', 'utf8']
                        if mode == '-O':
                            flags.append('-O')
                        else:
                            environment['PYTHONOPTIMIZE'] = '1'
                        completed = subprocess.run(
                            [sys.executable, *flags, str(code / name), *arguments],
                            capture_output=True, text=True, encoding='utf-8', env=environment, check=False)
                        self.assertNotEqual(completed.returncode, 0)
                        self.assertNotIn('PASS', completed.stdout)
                        self.assertIn('Checks require assertions', completed.stderr)


if __name__ == '__main__':
    unittest.main()
