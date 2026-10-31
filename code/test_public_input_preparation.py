import unittest
import prepare_original_input as P


class InputPreparationTests(unittest.TestCase):
    def test_whitespace_and_terminal_normalization(self):
        nums = [(i % 984) + 1 for i in range(314)]
        nums[168], nums[305] = 330, 338
        text = ',\n'.join(str(n) for n in nums) + '.\r\n'
        self.assertEqual(P.canonical_bytes(text), (', '.join(map(str, nums)) + '.\n').encode('ascii'))

    def test_already_corrected_source_rejected(self):
        nums = [1] * 314
        nums[168], nums[305] = 830, 338
        with self.assertRaises(ValueError):
            P.canonical_bytes(','.join(map(str, nums)))

    def test_wrong_number_count_rejected(self):
        with self.assertRaises(ValueError):
            P.canonical_bytes('1,2,3')


if __name__ == '__main__':
    unittest.main()
