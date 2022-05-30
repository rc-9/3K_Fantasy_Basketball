import unittest
from utils import utils

class TestCase(unittest.TestCase):
    def test_generate_season(self):
        # Test that explicitly passing None gets defaulted to current season
        self.assertEqual(utils.generate_season(None), '2021-22')

        # Test that passing null gets defaulted to current season
        self.assertEqual(utils.generate_season(), '2021-22')

        # Test that single season digit uses current season
        self.assertEqual(utils.generate_season(1), '2021-22')

        # Test that 3-digit season uses current season
        self.assertEqual(utils.generate_season(123), '2021-22')

        # Test that 5-digit season uses current season
        self.assertEqual(utils.generate_season(12345), '2021-22')

        # Test that 2 year format returns expected years
        self.assertEqual(utils.generate_season(16), '2016-17')

        # Test that 4 year format returns expected years
        self.assertEqual(utils.generate_season(2016), '2016-17')

if __name__ == '__main__':
    unittest.main()