import logging
import pandas as pd

class PositionCleanser:
    """Utilizes intermediate_player_data to clean & generate player_position dataframe."""

    def __init__(self, intermediate_player_data):
        self.intermediate_player_data = intermediate_player_data
        self.processed_position_data = None

    def clean_position_data(self):
        """Cleans & shapes intermediate_player_data into desired format that matches schema for player_position.csv."""

        logging.debug('Cleaning the intermediate_player_data dataframe for 2020 player position information...')

        # Assigning local df attribute (only with necessary columns needed for processing) for 2020 players only
        position_2020_df = self.intermediate_player_data[['player_id', 'Pos']][0:432]

        # Split 'Pos' column into new columns 'position_primary', 'position_secondary', 'position_tertiary'
        position_2020_df[['position_primary', 'position_secondary', 'position_tertiary']] = position_2020_df[
            'Pos'].str.split('-', expand=True)

        # Creating season column to distinguish this position data is for the 2020 player data only
        position_2020_df['season'] = 2020
        position_2020_df = position_2020_df[[
            'player_id', 'season', 'position_primary', 'position_secondary', 'position_tertiary'
        ]]

        self.processed_position_data = position_2020_df

def main(intermediate_player_data):
    """Instantiates data cleanser object and executes appropriate methods to generate processed player_position df."""

    cleaner = PositionCleanser(intermediate_player_data)
    cleaner.clean_position_data()

    logging.debug(f'Finished processing 2020 player position dataframe.')
    return cleaner.processed_position_data
