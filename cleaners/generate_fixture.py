import logging
import numpy as np
import pandas as pd

class GamesCleanser:
    """Implements cleaning methods to generate processed fixture df from the raw games information."""

    def __init__(self, from_season, raw_games):
        self.from_season = from_season
        self.raw_games_data = raw_games
        self.processed_fixture = None
        self.filtered_fixtures = None

    def clean_games_data(self):
        """Cleans & shapes raw_games_data into desired format that matches schema for fixture df."""

        logging.debug('Cleaning the raw_games_data dataframe...')

        # Assigning local df attribute (only with necessary columns needed for processing) & convert to lower case
        games_df = self.raw_games_data[
            ['GAME_DATE_EST', 'GAME_ID', 'HOME_TEAM_ID', 'VISITOR_TEAM_ID', 'SEASON', 'PTS_home', 'PTS_away']]
        games_df.columns = games_df.columns.str.lower()

        # Filter on season to only keep pertinent rows
        games_df = games_df[games_df['season'] >= self.from_season]

        # Remove duplicate records of the same game (based on duplicated game_id/fixture)
        games_df.drop_duplicates(keep='first', inplace=True)

        # Calls dates parser function to classify games based on phase of season
        games_df = self.dates_parser(games_df)

        # Edit game_id to new format (YYPNNNNN: YY-Season, P-Phase, NNNNN-GameNumber)
        games_df['game_id'] = games_df['game_id'].apply(lambda x: int(str(x)[1:3] + str(x)[0] + str(x)[3:]))

        # Convert game date, sort the dataframe, and reset the index
        games_df['game_date_est'] = games_df['game_date_est'].astype('datetime64[ns]')
        games_df = games_df.sort_values(by=['season', 'game_date_est'], ascending=True).reset_index(drop=True)

        # Set winner/loser conditionally based on scores
        games_df['home_team_win'] = np.where(games_df['pts_home'] > games_df['pts_away'], True, False)
        games_df['away_team_win'] = np.where(games_df['pts_away'] > games_df['pts_home'], True, False)

        # Reshape & reformat to match schema & get ready for export
        games_df.rename(columns={
            'game_date_est': 'played_on', 'game_id': 'fixture_id', 'visitor_team_id': 'away_team_id',
            'pts_home': 'home_team_score', 'pts_away': 'away_team_score'
        }, inplace=True)
        games_df = games_df[[
            'fixture_id', 'home_team_id', 'away_team_id', 'season', 'played_on', 'game_type',
            'home_team_score', 'away_team_score', 'home_team_win', 'away_team_win'
        ]]
        # games_df.set_index('fixture_id')

        self.filtered_fixtures = set(games_df.fixture_id.values.tolist())
        self.processed_fixture = games_df

    def dates_parser(self, games_df):
        """Uses custom dates dictionary to classify games according to phase of season."""

        dates_dict = {
            2020: ('2020-12-22', '2021-03-07', '2021-05-16'),
            2019: ('2019-10-22', '2020-02-16', '2020-08-14'),
            2018: ('2018-10-16', '2019-02-17', '2019-04-10'),
            2017: ('2017-10-17', '2018-02-18', '2018-04-11'),
            2016: ('2016-10-25', '2017-02-19', '2017-04-12'),
            2015: ('2015-10-27', '2016-02-14', '2016-04-13')
        }
        games_df['game_date_est'] = games_df['game_date_est'].astype(str)

        logging.debug('Classifying each game into appropriate type and phase...')
        for season, dates in dates_dict.items():
            games_df.loc[(games_df['season'] == season) &
                         (games_df['game_date_est'] < dates[0]), 'game_type'] = 'pre-season'
            games_df.loc[(games_df['season'] == season) &
                         (games_df['game_date_est'] > dates[2]), 'game_type'] = 'post-season'
            games_df.loc[(games_df['game_date_est'] <= dates[2]) &
                         (games_df['game_date_est'] >= dates[0]), 'game_type'] = 'regular-season'
            games_df.loc[(games_df['game_type'] == 'regular-season') &
                         (games_df['game_date_est'] < dates[1]), 'season_phase'] = 'before-asb'
            games_df.loc[(games_df['game_type'] == 'regular-season') &
                         (games_df['season_phase'] != 'before-asb'), 'season_phase'] = 'after-asb'
            games_df.loc[games_df['game_type'] != 'regular-season', 'season_phase'] = 'na'

        return games_df

def main(from_season, raw_games):
    """Instantiates data cleanser object and executes appropriate methods to generate processed_fixture df."""

    cleaner = GamesCleanser(from_season, raw_games)
    cleaner.clean_games_data()

    logging.debug(f'Finished processing games information for seasons of interest.')
    return cleaner.processed_fixture, cleaner.filtered_fixtures
