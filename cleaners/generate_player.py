import logging
import pandas as pd

class PlayerCleanser:
    """Utilizes intermediate_player_data to clean & generate player dataframe."""

    def __init__(self, intermediate_player_data):
        self.intermediate_player_data = intermediate_player_data
        self.processed_player_data = None

    def clean_player_data(self):
        """Cleans & shapes intermediate_player_data into desired format that matches schema for player.csv."""

        logging.debug('Cleaning the intermediate_player_data dataframe for player information...')

        # Assigning local df attribute (only with necessary columns needed for processing) & ensure no NaN values
        player_df = self.intermediate_player_data[['player_id', 'Name', 'Age', 'Draft']]
        player_df = player_df.where((pd.notnull(player_df)), None)

        # Split 'Name' column into new columns 'first_name' and 'last_name'
        player_df[['first_name', 'last_name']] = player_df['Name'].str.split(' ', 1, expand=True)

        # Split 'Draft' column into new columns 'draft_year' and 'draft_pick'
        player_df[['draft_year', 'draft_pick']] = player_df['Draft'].str.split(expand=True)

        # Use 'Age' column to calculate new column 'birth_year' (only for rows with existing values to prevent errors)
        player_df['Age'] = player_df['Age'].apply(lambda x: round(2021.55 - x) if x is not None else x)
        player_df.rename(columns={'Age': 'birth_year'}, inplace=True)

        # Fix faulty birth years for players born in Jan/Dec
        modified_birth_years = [
            ['Buddy', 'Hield', 1992], ['LeBron', 'James', 1984], ['De\'Aaron', 'Fox', 1997],
            ['Torrey', 'Craig', 1990], ['Edmond', 'Sumner', 1995], ['Gorgui', 'Dieng', 1990],
            ['Aleksej', 'Pokusevski', 2001], ['Eric', 'Gordon', 1988], ['Sekou', 'Doumbouya', 2000],
            ['Jahlil', 'Okafor', 1995], ['Wesley', 'Iwundu', 1994], ['Paul', 'Watson', 1994]
        ]
        for i in modified_birth_years:
            player_df.loc[(player_df['first_name'] == i[0]) & (player_df['last_name'] == i[1]), 'birth_year'] = i[2]

        # Reorder and keep only necessary columns per schema
        player_df = player_df[['player_id', 'first_name', 'last_name', 'birth_year', 'draft_year', 'draft_pick']]

        # Recast value types to match schema (changing floats or strings into ints, reverting nan values to None)
        player_df['birth_year'] = player_df['birth_year'].astype('Int64')
        player_df['draft_year'] = pd.to_numeric(player_df['draft_year'])  # Had to change string to numeric first
        player_df['draft_year'] = player_df['draft_year'].astype('Int64')
        player_df['draft_pick'] = pd.to_numeric(player_df['draft_pick'])  # Had to change string to numeric first
        player_df['draft_pick'] = player_df['draft_pick'].astype('Int64')
        player_df = player_df.fillna(0).replace([0], [None])  # Replace created int-N/A values into 0 then None

        self.processed_player_data = player_df

def main(intermediate_player_data):
    """Instantiates data cleanser object and executes appropriate methods to generate processed team.csv."""

    cleaner = PlayerCleanser(intermediate_player_data)
    cleaner.clean_player_data()

    logging.debug(f'Finished processing player dataframe.')
    return cleaner.processed_player_data
