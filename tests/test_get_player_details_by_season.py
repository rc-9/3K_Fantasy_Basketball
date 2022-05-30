import datetime
import os
import time
import unittest
from data import get_player_details_by_season
from utils import player_cache

DIR_PATH= 'data/intermediate'

class TestCase(unittest.TestCase):
    # def test_get_player_data(self):
    #     Fetcher = get_player_details_by_season.DataFetcher()

    #     # Test that no function arguments returns non-empty results for the current season
    #     Fetcher.get_player_data(None)
    #     self.assertIsNotNone(Fetcher.data)
    #     self.assertIsInstance(Fetcher.data, dict)
    #     self.assertEqual(Fetcher.data['parameters']['Season'], '2021-22')

    def test_export_player_data(self):
        Fetcher = get_player_details_by_season.DataFetcher()

        # Test that empty data returns None
        result = Fetcher.export_player_data()
        self.assertIsNone(result)

        # Test that data is export to CSV
        Fetcher.data = player_cache.cache # Use mock data from utils
        if os.path.exists(DIR_PATH):
            Fetcher.export_player_data()
            self.assertTrue(os.path.exists(DIR_PATH + f'/player.raw-{datetime.date.today()}.csv'))

if __name__ == '__main__':
    unittest.main()