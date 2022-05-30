import os
import logging
import argparse
import pandas as pd
from pandas.errors import EmptyDataError

import cleaners.generate_team
import cleaners.generate_intermediate_player_data
import cleaners.generate_player
import cleaners.generate_player_position
import cleaners.generate_player_team
import cleaners.generate_fixture
import cleaners.generate_player_statistic
import cleaners.comprehensive_compiler

# Defining the file paths for the necessary raw data csv files that will be utilized for, or to perform cleansing on
TEAMS_DATA_PATH = './data/raw/teams.csv'  # Raw CSV contains detailed NBA teams info from Kaggle, with desired IDs
NBA_TEAMS_DATA_PATH = './data/raw/nba_teams.csv'  # Raw CSV contains concise NBA teams info from BM, without IDs
PLAYER_DATA_PATH = './data/raw/player_data.csv'  # Raw CSV contains 2020 players with team, pos, age, draft info
GAMES_DETAILS_PATH = './data/raw/games_details.csv'  # Raw CSV containing player stats for games since 2003
GAMES_DATA_PATH = './data/raw/games.csv'  # Raw CSV containing games info since 2003
INTERMEDIATE_PATH = './data/intermediate/'
PROCESSED_PATH = './data/processed/'

def logger_setup():
    """Standardized logging set up with custom handlers & formatters. Implements logging for all submodules executed."""
    logger = logging.getLogger()
    sh, fh = logging.StreamHandler(), logging.FileHandler('../logs_nba3k.log', 'a')
    sh.setFormatter(logging.Formatter('LOG|%(levelname)s|%(lineno)d: %(message)s'))
    fh.setFormatter(logging.Formatter('%(module)s (%(lineno)d): %(asctime)s | %(levelname)s | %(message)s'))
    logger.setLevel(logging.DEBUG), sh.setLevel(logging.INFO), logger.addHandler(fh), logger.addHandler(sh)
    return logger

class ExecuteCleaners:
    """Implements the raw data loads, calls appropriate cleaner, & exports processed CSVs."""

    def __init__(self, from_season=2020):
        """Instantiates class attributes to be used for storing raw, intermediate, and processed dataframes."""

        self.from_season = int(from_season)

        self.raw_teams = None
        self.raw_nba_teams = None
        self.raw_player_data = None
        self.raw_games_details = None
        self.raw_games = None

        self.intermediate_player_data = None

        self.processed_team = None
        self.processed_player = None
        self.processed_player_team = None
        self.processed_player_position = None
        self.processed_player_statistic = None
        self.processed_fixture = None

        self.comprehensive_player_statistic = None

    def load_raw_csv(self):
        """Loads data from raw CSV files into dataframe attributes, to be ready to pass into cleaning modules."""

        logging.info('Loading raw CSV files into dataframes...')

        try:
            logging.debug('Loading raw teams.csv (from Kaggle) into raw_teams_kaggle dataframe...')
            self.raw_teams = pd.read_csv(TEAMS_DATA_PATH, sep=',', header=0, encoding='utf-8')

            logging.debug('Loading raw nba_teams.csv (from Basketball Monster) into raw_teams_bm dataframe...')
            self.raw_nba_teams = pd.read_csv(NBA_TEAMS_DATA_PATH, sep=',', header=0, encoding='utf-8')

            logging.debug('Loading raw player_data.csv (from Kaggle) into raw_player_data_2020 dataframe...')
            self.raw_player_data = pd.read_csv(PLAYER_DATA_PATH, sep=',', header=0, encoding='utf-8')

            logging.debug('Loading raw games_details.csv (from Kaggle) into raw_games_details dataframe...')
            self.raw_games_details = pd.read_csv(GAMES_DETAILS_PATH, sep=',', header=0, encoding='utf-8')

            logging.debug('Loading games.csv (from Kaggle) into raw_games_data dataframe...')
            self.raw_games = pd.read_csv(
                GAMES_DATA_PATH,
                sep=',',
                header=0,
                encoding='utf-8',
                parse_dates=[0],
                infer_datetime_format=True,
                dtype={'GAME_ID': pd.Int64Dtype(), 'SEASON': pd.Int16Dtype(),
                       'HOME_TEAM_ID': pd.Int64Dtype(), 'VISITOR_TEAM_ID': pd.Int64Dtype()},
                skip_blank_lines=True
            )

            logging.info('Loading complete.')

        except FileNotFoundError as e:
            logging.error(f'File not found error: {e}')

    def call_cleaner(self):
        """Calls on cleaner sub-modules in appropriate order, passing in the corresponding raw dataframe to clean."""

        logging.info('Executing generate_team.py cleaner module...')
        self.processed_team = cleaners.generate_team.main(self.raw_teams, self.raw_nba_teams)

        logging.info('Executing generate_intermediate_player_data.py cleaner module...')
        self.intermediate_player_data = cleaners.generate_intermediate_player_data.main(
            self.raw_player_data, self.raw_games_details)

        logging.info('Executing generate_player.py cleaner module...')
        self.processed_player = cleaners.generate_player.main(self.intermediate_player_data)

        logging.info('Executing generate_player_position.py cleaner module...')
        self.processed_player_position = cleaners.generate_player_position.main(self.intermediate_player_data)

        logging.info('Executing generate_player_team.py cleaner module...')
        self.processed_player_team = cleaners.generate_player_team.main(
            self.intermediate_player_data, self.processed_team)

        logging.info('Executing generate_fixture.py cleaner module...')
        self.processed_fixture, filtered_fixtures = cleaners.generate_fixture.main(self.from_season, self.raw_games)

        logging.info('Executing generate_player_statistic.py cleaner module...')
        self.processed_player_statistic = cleaners.generate_player_statistic.main(
            self.intermediate_player_data, self.raw_games, self.raw_games_details, filtered_fixtures)

        # logging.info('Executing comprehensive_compiler.py module...')
        # self.comprehensive_player_statistic = cleaners.comprehensive_compiler.main(
        #     self.processed_player_statistic, self.processed_fixture, self.intermediate_player_data)

        logging.info('Cleaning complete.')

    def export_processed_csv(self):
        """Exports all processed dataframes to corresponding CSV files."""

        try:
            logging.debug('Checking if intermediate path exists...')
            if not os.path.exists(INTERMEDIATE_PATH):
                logging.debug('Intermediate path doesn\'t exist. Creating processed path...')
                os.mkdir(INTERMEDIATE_PATH)

            logging.debug('Checking if processed path exists...')
            if not os.path.exists(PROCESSED_PATH):
                logging.debug('Processed path doesn\'t exist. Creating processed path...')
                os.mkdir(PROCESSED_PATH)

        except OSError as e:
            logging.error(f'OS error occurred: {e}')

        try:
            logging.info('Exporting processed_team dataframe into team.csv file...')
            self.processed_team.to_csv(path_or_buf=f'{PROCESSED_PATH}team.csv', index=False)

            logging.info('Exporting intermediate dataframe into intermediate_player_data.csv file...')
            self.intermediate_player_data.to_csv(
                path_or_buf=f'{INTERMEDIATE_PATH}intermediate_player_data.csv', index=False
            )

            logging.info('Exporting processed_player dataframe into player.csv file...')
            self.processed_player.to_csv(path_or_buf=f'{PROCESSED_PATH}player.csv', index=False)

            logging.info('Exporting processed_player_position dataframe into player_position.csv file...')
            self.processed_player_position.to_csv(path_or_buf=f'{PROCESSED_PATH}player_position.csv', index=False)

            logging.info('Exporting processed_player_team dataframe into player_team.csv file...')
            self.processed_player_team.to_csv(path_or_buf=f'{PROCESSED_PATH}player_team.csv', index=False)

            logging.info('Exporting processed_fixture dataframe into fixture.csv file...')
            self.processed_fixture.to_csv(path_or_buf=f'{PROCESSED_PATH}fixture.csv', index=False)

            logging.info('Exporting processed_player_statistic dataframe into player_statistic.csv file...')
            self.processed_player_statistic.to_csv(path_or_buf=f'{PROCESSED_PATH}player_statistic.csv', index=False)

            # logging.info('Exporting compiled player stats dataframe into comprehensive_player_statistic.csv file...')
            # self.comprehensive_player_statistic.to_csv(
            #     path_or_buf=f'{INTERMEDIATE_PATH}comprehensive_player_statistic.csv', index=False
            # )

            logging.info('Exporting complete.')

        except OSError as e:
            logging.error(f'OS error occurred: {e}')
        except EmptyDataError as e:
            logging.error(f'Empty data error occurred: {e}')
        except AttributeError as e:
            logging.error(f'Attribute error occurred: {e}')

def main():
    """Calls on cleaner sub-modules in appropriate order to output CSV files with pertinent info that matches schema."""

    logger = logger_setup()

    parser = argparse.ArgumentParser(description='Fetch and export player data based on seasons of interest.')
    parser.add_argument(
        '--s',
        '--season',
        dest='season',
        metavar='<season>',
        type=int,
        default=2020,
        help='input oldest season/year of interest to filter API results from -- 2 or 4 digit'
    )
    args = parser.parse_args()
    if len(str(args.season)) == 2:
        from_season = int('20'+str(args.season))
    else:
        from_season = args.season

    compiler = ExecuteCleaners(from_season)
    compiler.load_raw_csv()
    compiler.call_cleaner()
    compiler.export_processed_csv()

    logging.info(f'Execution complete; game-info and player-stats were filtered to {from_season} season & onwards.')

if __name__ == '__main__':
    main()
