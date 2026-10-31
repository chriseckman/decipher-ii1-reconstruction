"""Reader-entrypoint tests using invented numbers, never historical ciphertext."""
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import decode as D


def synthetic_original():
    numbers = [1 + ((i * 17 + 5) % 984) for i in range(314)]
    numbers[168], numbers[305] = 330, 338
    return numbers


class ReaderFacingTests(unittest.TestCase):
    def test_accepts_comma_whitespace_newline_and_final_period(self):
        numbers = synthetic_original()
        content = '\ufeff' + ',\n'.join(str(n) for n in numbers) + '.\r\n'
        self.assertEqual(D.parse_user_numbers(content), numbers)

    def test_accepts_whitespace_separated_text(self):
        numbers = synthetic_original()
        self.assertEqual(D.parse_user_numbers('  '.join(map(str, numbers))), numbers)

    def test_rejects_wrong_count_with_helpful_message(self):
        with self.assertRaisesRegex(D.InputProblem, 'exactly 314'):
            D.parse_user_numbers('1,2,3')

    def test_rejects_heading_or_clues(self):
        with self.assertRaisesRegex(D.InputProblem, 'headings or clues'):
            D.parse_user_numbers('Puzzle 2-1\n' + ','.join(map(str, synthetic_original())))

    def test_rejects_out_of_range_zero_instead_of_python_negative_index(self):
        numbers = synthetic_original()
        numbers[5] = 0
        with self.assertRaisesRegex(D.InputProblem, 'valid key positions are 1'):
            D.parse_user_numbers(','.join(map(str, numbers)))

    def test_rejects_pre_corrected_830(self):
        numbers = synthetic_original()
        numbers[168] = 830
        with self.assertRaisesRegex(D.InputProblem, 'Do not apply'):
            D.parse_user_numbers(','.join(map(str, numbers)))

    def test_rejects_wrong_fingerprint(self):
        with self.assertRaisesRegex(D.InputProblem, 'SHA-256'):
            D.validated_original_bytes(','.join(map(str, synthetic_original())))

    def test_wrong_source_text_is_stopped_before_processing_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp = Path(tmp) / 'some-numbers.txt'
            src = Path(tmp) / 'wrong-source.txt'
            inp.write_text('1,2,3')
            src.write_text('A' * 492)
            with self.assertRaisesRegex(D.InputProblem, 'does not match the verified'):
                D.run_reader(inp, source=src, output=Path(tmp) / 'result', show_text=False)

    def test_image_is_rejected_with_text_only_instructions(self):
        with tempfile.TemporaryDirectory() as tmp:
            img = Path(tmp) / 'numbers.png'
            img.write_bytes(b'no image processing is required')
            with self.assertRaisesRegex(D.InputProblem, 'text-only decoder'):
                D.run_reader(img, source=ROOT / 'inputs/source_transcription.txt',
                             output=Path(tmp) / 'result', show_text=False)
            self.assertFalse((Path(tmp) / 'result').exists())

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp = Path(tmp) / 'numbers.txt'
            inp.write_text('1,2,3')
            with self.assertRaisesRegex(D.InputProblem, 'already exists'):
                D.run_reader(inp, source=ROOT / 'inputs/source_transcription.txt', output=Path(tmp), show_text=False)


if __name__ == '__main__':
    unittest.main()
