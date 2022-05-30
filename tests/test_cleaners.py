import sys
import logging
import unittest
import numpy as np
import pandas as pd

sys.path.insert(0, '..')
from cleaners.generate_team import TeamCleanser
from cleaners.generate_intermediate_player_data import IntermediatePDBuilder
from cleaners.generate_player import PlayerCleanser
from cleaners.generate_player_position import PositionCleanser
from cleaners.generate_player_team import PlayerTeamCleanser
from cleaners.generate_fixture import GamesCleanser
from cleaners.generate_player_statistic import PlayerStatsCleanser
from cleaners.comprehensive_compiler import Compiler
sys.path.remove('..')


class TestCleaners(unittest.TestCase):
    """Carries out unittests for each of the cleaner modules. Load & Export methods of execute_cleaners not tested."""

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def test_generate_team(self):
        """Set up appropriate dataframes needed to instantiate cleaner object & test the cleaning methods."""

        # TeamCleanser requires dataframes in the format of the raw files: teams.csv & nba_teams.csv
        teams_df = pd.DataFrame({
            'TEAM_ID': [0, 1, 2],
            'ABBREVIATION': ['PHI', 'DEN', 'MIL']
        })
        nba_teams_df = pd.DataFrame({
            'name': ['76ers', 'Nuggets', 'Bucks'],
            'shortname': ['PHI', 'DEN', 'MIL'],
            'city': ['PHI', 'DEN', 'MIL'],
            'State': ['PA', 'CO', 'WI'],
            'conference': ['East', 'West', 'East'],
            'division': ['Atlantic', 'Northwest', 'Central']
        })
        test_cleaner = TeamCleanser(teams_df, nba_teams_df)
        test_cleaner.clean_teams()
        output_df = test_cleaner.processed_team

        # Test to check if all required columns are in the finalized dataframe
        ret_cols = output_df.columns.values.tolist()
        self.assertEqual(ret_cols, ['team_id', 'name', 'shortname', 'city', 'state', 'conference', 'division'])

        # Test to check if output dataframe updates with correct team_id values
        ret_id = output_df.team_id.values.tolist()
        self.assertEqual(ret_id, [0, 1, 2])

    def test_generate_intermediate_pd(self):
        """Set up appropriate dataframes needed to instantiate cleaner object & test the cleaning methods."""

        # IntermediatePDBuilder requires dataframes in the format of the raw files: player_data.csv & games_details.csv
        players_df = pd.DataFrame({
            'Name': ['Joel Embiid', 'Nikola Jokic', 'Giannis Antetokounmpo'],
            'Team': ['PHI', 'DEN', 'MIL'],
            'Pos': ['C', 'C', 'PF-SF'],
            'Age': [25.2, 25.5, 25.8],
            'Draft': [3, 41, 15],
        })
        games_player_names_df = pd.DataFrame({
            'PLAYER_NAME': ['Kyle Lowry', 'Steph Curry', 'Khris Middleton']
        })
        test_cleaner = IntermediatePDBuilder(players_df, games_player_names_df)
        test_cleaner.build_comprehensive_player_data()
        output_df = test_cleaner.intermediate_player_data

        # Test to check if all required columns are in the finalized dataframe
        ret_cols = output_df.columns.values.tolist()
        self.assertEqual(ret_cols, ['player_id', 'Name', 'Team', 'Pos', 'Age', 'Draft'])

        # Test to check if output dataframe updates with modified player IDs in correct order
        ret_id = output_df.player_id.values.tolist()
        self.assertEqual(ret_id, [1, 2, 3, 4, 5, 6])
        ret_names = output_df.Name.values.tolist()
        self.assertEqual(ret_names, ['Joel Embiid', 'Nikola Jokic', 'Giannis Antetokounmpo',
                                     'Kyle Lowry', 'Steph Curry', 'Khris Middleton'])

    def test_generate_player(self):
        """Set up appropriate dataframes needed to instantiate cleaner object & test the cleaning methods."""

        # PlayerCleanser requires dataframes in the format of the raw files: intermediate_player_data.csv
        intermediate_df = pd.DataFrame({
            'player_id': [1, 2, 3, 4],
            'Name': ['A B-C', 'D-E F', 'G', 'LeBron James'],
            'Team': ['PHI', 'DEN', 'MIL', 'LAL'],
            'Pos': ['C', 'C', 'PF-SF', 'SF'],
            'Age': [25.2, 25.2, 25.8, 35.5],
            'Draft': ['2018 3', '2018 41', '2018 15', '2018 1']
        })
        test_cleaner = PlayerCleanser(intermediate_df)
        test_cleaner.clean_player_data()
        output_df = test_cleaner.processed_player_data

        # Test to check if all required columns are in the finalized dataframe
        ret_cols = output_df.columns.values.tolist()
        self.assertEqual(ret_cols, ['player_id', 'first_name', 'last_name', 'birth_year', 'draft_year', 'draft_pick'])

        # Test to check if output dataframe updates with modified column values
        ret_id = output_df.player_id.values.tolist()
        self.assertEqual(ret_id, [1, 2, 3, 4])
        ret_first_name = output_df.first_name.values.tolist()
        self.assertEqual(ret_first_name, ['A', 'D-E', 'G', 'LeBron'])
        ret_last_name = output_df.last_name.values.tolist()
        self.assertEqual(ret_last_name, ['B-C', 'F', None, 'James'])
        ret_bd = list(output_df.birth_year.unique())
        self.assertEqual(ret_bd, [1996, 1984])
        ret_draft_year = list(output_df.draft_year.unique())
        self.assertEqual(ret_draft_year, [2018])
        ret_pick = list(output_df.draft_pick.unique())
        self.assertEqual(ret_pick, [3, 41, 15, 1])

    def test_generate_player_position(self):
        """Set up appropriate dataframes needed to instantiate cleaner object & test the cleaning methods."""

        # PositionCleaner requires dataframes in the format of the raw files: intermediate_player_data.csv
        intermediate_df = pd.DataFrame({
            'player_id': [1, 2, 3, 4],
            'Pos': ['C', 'C-PF', 'PF-SF-SG', 'SF'],
        })
        test_cleaner = PositionCleanser(intermediate_df)
        test_cleaner.clean_position_data()
        output_df = test_cleaner.processed_position_data

        # Test to check if all required columns are in the finalized dataframe
        ret_cols = output_df.columns.values.tolist()
        self.assertEqual(ret_cols, ['player_id', 'season', 'position_primary',
                                    'position_secondary', 'position_tertiary'])

        # Test to check if output dataframe updates with modified column values
        ret_season = output_df.season.values.tolist()
        self.assertEqual(ret_season, [2020, 2020, 2020, 2020])
        ret_pos = output_df.position_primary.values.tolist()
        self.assertEqual(ret_pos, ['C', 'C', 'PF', 'SF'])
        ret_pos = output_df.position_secondary.values.tolist()
        self.assertEqual(ret_pos, [None, 'PF', 'SF', None])
        ret_pos = output_df.position_tertiary.values.tolist()
        self.assertEqual(ret_pos, [None, None, 'SG', None])

    def test_generate_player_team(self):
        """Set up appropriate dataframes needed to instantiate cleaner object & test the cleaning methods."""

        # PlayerTeamCleanser requires dataframes in the format of the raw files: intermediate_player_data.csv & team.csv
        intermediate_df = pd.DataFrame({
            'player_id': [111, 222, 333],
            'Team': ['A', 'B', 'C']
        })
        team_df = pd.DataFrame({
            'team_id': [i for i in range(1, 31)],
            'shortname': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                     'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'AA', 'BB', 'CC', 'DD']
        })
        test_cleaner = PlayerTeamCleanser(intermediate_df, team_df)
        test_cleaner.clean_player_team()
        output_df = test_cleaner.processed_player_team_2020

        # Test to check if output dataframe updates with modified column values
        ret_team_id = output_df.team_id.values.tolist()
        self.assertEqual(ret_team_id, [1, 2, 3])
        ret_player_id = output_df.player_id.values.tolist()
        self.assertEqual(ret_player_id, [111, 222, 333])

    def test_generate_fixture(self):
        """Set up appropriate dataframes needed to instantiate cleaner object & test the cleaning methods."""

        # GamesCleanser requires from_season parameter & dataframes in the format of the raw files: games.csv
        from_season = 2018
        games_df = pd.DataFrame({
            'GAME_DATE_EST': ['2017-09-27', '2018-01-07', '2018-02-26', '2018-05-01',
                              '2018-09-27', '2019-01-07', '2019-02-26', '2019-05-01',
                              '2019-09-27', '2020-01-07', '2020-03-09', '2020-09-17'],
            'GAME_ID': [11700001, 21700001, 31700001, 41700001,
                        11800001, 21800001, 31800001, 41800001,
                        11900001, 21900001, 31900001, 41900001],
            'HOME_TEAM_ID': [i for i in range(1, 13)],
            'VISITOR_TEAM_ID': [i for i in range(13, 25)],
            'SEASON': [2017, 2017, 2017, 2017, 2018, 2018, 2018, 2018, 2019, 2019, 2019, 2019],
            'PTS_home': [100 for i in range(12)],
            'PTS_away': [101 for i in range(12)]
        })
        test_cleaner = GamesCleanser(from_season, games_df)
        test_cleaner.clean_games_data()
        output_df = test_cleaner.processed_fixture

        # Test to check if all required columns are in the finalized dataframe
        ret_cols = output_df.columns.values.tolist()
        self.assertEqual(ret_cols, ['fixture_id', 'home_team_id', 'away_team_id', 'season', 'played_on', 'game_type',
                                    'home_team_score', 'away_team_score', 'home_team_win', 'away_team_win'])

        # Test to check if output dataframe updates with modified column values
        ret_game_id = output_df.fixture_id.values.tolist()
        self.assertEqual(ret_game_id, [18100001, 18200001, 18300001, 18400001, 19100001, 19200001, 19300001, 19400001])
        ret_game_type = output_df.game_type.values.tolist()
        self.assertEqual(ret_game_type, ['pre-season', 'regular-season', 'regular-season', 'post-season',
                                         'pre-season', 'regular-season', 'regular-season', 'post-season'])
        ret_win_bool = output_df.home_team_win.values.tolist()
        self.assertEqual(ret_win_bool, [False for i in range(8)])
        ret_win_bool = output_df.away_team_win.values.tolist()
        self.assertEqual(ret_win_bool, [True for i in range(8)])

    def test_generate_player_statistic(self):
        """Set up appropriate dataframes needed to instantiate cleaner object & test the cleaning methods."""

        # PlayerStatsCleanser requires intermediate_player_data, raw_games, raw_games_details, filtered_fixtures
        intermediate_df = pd.DataFrame({
            'player_id': [1, 2, 3, 4, 5, 6, 7, 8],
            'Name': ['A B', 'C D', 'E F', 'G H', 'I J', 'K L', 'M N', 'O P'],
        })
        games_df = pd.DataFrame({
            'GAME_ID': [11800001, 21800001, 31800001, 41800001, 11900001, 21900001, 31900001, 41900001],
        })
        games_details_df = pd.DataFrame({
            'GAME_ID': [11800001, 21800001, 31800001, 41800001, 11900001, 21900001, 31900001, 41900001],
            'PLAYER_NAME': ['A B', 'C D', 'E F', 'G H', 'I J', 'K L', 'M N', 'O P'],
            'START_POSITION': [0, 0, 0, 0, 0, 'G', 'F', 'C'],
            'COMMENT': ['coach dec', 'sick', 'right mcl', 'covid protocol',
                        'unknown status', 'suspended', 'load management', 'personal'],
            'MIN': [0, 0, 0, '10:00', '8:25', '34:45', '12', '17'],
            # Placeholder columns not getting tested (no manipulation done on these columns during cleaning)
            'FGM': [0 for i in range(8)], 'FGA': [0 for i in range(8)], 'FG3M': [0 for i in range(8)],
            'FG3A': [0 for i in range(8)], 'FTM': [0 for i in range(8)], 'FTA': [0 for i in range(8)],
            'OREB': [0 for i in range(8)], 'DREB': [0 for i in range(8)], 'REB': [0 for i in range(8)],
            'AST': [0 for i in range(8)], 'STL': [0 for i in range(8)], 'BLK': [0 for i in range(8)],
            'TO': [0 for i in range(8)], 'PTS': [0 for i in range(8)],
        })
        filtered_fixtures = {19100001, 19200001, 19300001, 19400001}
        test_cleaner = PlayerStatsCleanser(intermediate_df, games_df, games_details_df, filtered_fixtures)
        test_cleaner.clean_games_details()
        output_df = test_cleaner.processed_player_statistic

        # Test to check if all required columns are in the finalized dataframe
        ret_cols = output_df.columns.values.tolist()
        self.assertEqual(ret_cols, [
            'player_id', 'fixture_id', 'player_status', 'is_starter', 'seconds_played', 'points', 'threes_attempted',
            'threes_made', 'field_goals_attempted', 'field_goals_made', 'free_throws_attempted', 'free_throws_made',
            'offensive_rebounds', 'defensive_rebounds', 'assists', 'steals', 'blocks', 'turnovers'
        ])

        # Test to check if output dataframe updates with modified column values
        ret_game_id = output_df.fixture_id.values.tolist()
        self.assertEqual(ret_game_id, [19100001, 19200001, 19300001, 19400001])
        ret_is_starter = output_df.is_starter.values.tolist()
        self.assertEqual(ret_is_starter, [False, True, True, True])
        ret_sec = output_df.seconds_played.values.tolist()
        self.assertEqual(ret_sec, [505, 2085, 720, 1020])
        ret_status = output_df.player_status.values.tolist()
        self.assertEqual(ret_status, ['unknown status', 'SUS', 'DNP-REST', 'NWT'])
        ret_player_id = output_df.player_id.values.tolist()
        self.assertEqual(ret_player_id, [5, 6, 7, 8])

    def test_comprehensive_compiler(self):
        """Set up appropriate dataframes needed to instantiate cleaner object & test the cleaning methods."""

        # Compiler requires intermediate_player_data, processed_fixture, processed_player_statistic
        intermediate_df = pd.DataFrame({
            'player_id': [1, 2],
            'Name': ['A B', 'C D'],
        })
        fixture_df = pd.DataFrame({
            'fixture_id': [11800001, 21800001],
            'played_on': ['2018-12-01', '2018-12-02']
        })
        statistic_df = pd.DataFrame({
            'fixture_id': [11800001, 21800001], 'player_id': [1, 2], 'player_status': ['', ''],
            'is_starter': [True, False], 'seconds_played': [232, 123], 'points': [10, 20],
            'threes_attempted': [4, 1], 'threes_made': [1, 0], 'field_goals_attempted': [6, 1],
            'field_goals_made': [4, 0], 'free_throws_attempted': [2, 3], 'free_throws_made': [1, 3],
            'offensive_rebounds': [2, 1], 'defensive_rebounds': [4, 5], 'assists': [2, 3],
            'steals': [2, 2], 'blocks': [1, 2], 'turnovers': [1, 2]
        })
        test_compiler = Compiler(statistic_df, fixture_df, intermediate_df)
        test_compiler.compile_data()
        test_compiler.clean_compiled_data()
        output_df = test_compiler.comprehensive_player_statistic

        # Test to check if all required columns are in the finalized dataframe
        ret_cols = output_df.columns.values.tolist()
        self.assertEqual(ret_cols, [
            'player_id', 'player_name', 'fixture_id', 'played_on', 'player_status', 'is_starter', 'seconds_played',
            'points', 'offensive_rebounds', 'defensive_rebounds', 'rebounds', 'assists', 'steals', 'blocks',
            'field_goals_made', 'field_goals_attempted', 'fg%', 'free_throws_made', 'free_throws_attempted', 'ft%',
            'threes_made', 'threes_attempted', '3pt%', 'turnovers'
        ])

        # Test to check if output dataframe updates with modified column values
        ret_player_name = output_df.player_name.values.tolist()
        self.assertEqual(ret_player_name, ['A B', 'C D'])
        ret_played_on = output_df.played_on.values.tolist()
        self.assertEqual(ret_played_on, ['2018-12-01', '2018-12-02'])
        ret_rebounds = output_df.rebounds.values.tolist()
        self.assertEqual(ret_rebounds, [6, 6])
        ret_fg = output_df['fg%'].values.tolist()
        self.assertEqual(ret_fg, [66.67, 0])
        ret_ft = output_df['ft%'].values.tolist()
        self.assertEqual(ret_ft, [50, 100])
        ret_3pt = output_df['3pt%'].values.tolist()
        self.assertEqual(ret_3pt, [25, 0])


if __name__ == '__main__':
    unittest.main()


"""Below is code that was used for some other specific manual testing. Here to serve as a reference/future use."""
# fixID_PS = self.processed_player_statistic.fixture_id.values.tolist()
# fixID_FX = self.processed_fixture.fixture_id.values.tolist()
# leftover = []
# for i in fixID_PS:
#     if i not in fixID_FX:
#         leftover.append(i)
# print(set(leftover))
# print(len(set(leftover)))

# ne_stacked = (player_team_old != player_team_new).stack()
# changed = ne_stacked[ne_stacked]
# changed.index.names = ['id', 'col']
# difference_locations = np.where(player_team_old != player_team_new)
# changed_from = player_team_old.values[difference_locations]
# changed_to = player_team_new.values[difference_locations]
# i = pd.DataFrame({'from': changed_from, 'to': changed_to}, index=changed.index)
# print(i)

# df = pd.merge(fixture_old, fixture_new, on=['fixture_id','fixture_id'], how='right', indicator='Exist')
# df['Exist'] = np.where(df.Exist == 'both', True, False)
# i = df.Exist.values.tolist()
# print(len(i))
# x = 0
# for e in i:
#     if e is False:
#         x += 1
# print(x)

# list1 = self.processed_team.shortname.values.tolist()
# list2 = []
# for i in list1:
#     list2.append(type(i))
# print(list2)
# print(set(list2))

# for colname in []:
#     list1 = self.processed_player_statistic[colname].values.tolist()
#     list2 = []
#     for i in list1:
#         list2.append(type(i))
#     # print(list2)
#     print(set(list2))
