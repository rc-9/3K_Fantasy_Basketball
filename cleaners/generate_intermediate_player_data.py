import logging
import pandas as pd

class IntermediatePDBuilder:
    """Implements cleaning & merging to generate intermediate_player_data containing comprehensive player info.
    Purpose: To create a standard 'one-stop' player dataframe to be used by other cleaners for further processing."""

    def __init__(self, raw_player_data, raw_games_details):
        self.raw_player_data_2020 = raw_player_data
        self.raw_games_details = raw_games_details
        self.intermediate_player_data = None

    def build_comprehensive_player_data(self):
        """Create comprehensive (2003-2020) player list in the shape of raw 2020 player_data csv, with IDs."""

        logging.debug('Building intermediate_player_data from raw player_data & games_details...')

        # Assigning local df attributes (only with necessary columns needed for the build)
        player_data_2020 = self.raw_player_data_2020  # (Cols: ['Name', 'Team', 'Pos', 'Age', 'Draft'])
        player_data_gd = self.raw_games_details[['PLAYER_NAME']]

        # Retrieve 03-20 player names from games_details csv missing from player_data csv (use lists to preserve order)
        raw_gd_player_list = player_data_gd.PLAYER_NAME.tolist()  # 615626 values, with repeats for each game
        unique_gd_player_list = []  # should get 2410 unique players values
        [unique_gd_player_list.append(x) for x in raw_gd_player_list if x not in unique_gd_player_list]

        # Remove duplicate names from unique_gd_player_list that are already in 2020 player_data
        player_list_2020 = player_data_2020.Name.tolist()  # 432 players in player_data
        difference_players = [x for x in unique_gd_player_list if x not in player_list_2020]  # 2000 left

        # Build df containing all 2432 players in same shape of the original player_data.csv (raw_player_data_2020 df)
        intermediate_df = self.raw_player_data_2020  # (Cols: ['Name', 'Team', 'Pos', 'Age', 'Draft'])
        intermediate_df = pd.concat([intermediate_df, pd.DataFrame({'Name': difference_players})], ignore_index=True)

        # Creating player IDs based on index (order of the first 432 players is retained)
        intermediate_df['player_id'] = intermediate_df.index + 1

        # Fixing TEAM 'NOR' to 'NOP' for New Orleans Pelicans
        intermediate_df['Team'].replace('NOR', 'NOP', inplace=True)

        # Re-order columns of intermediate_df & assign to class attribute (now ready to be used by other cleaners)
        intermediate_df = intermediate_df[['player_id', 'Name', 'Team', 'Pos', 'Age', 'Draft']]
        
        # Fill any nan values with None (direct approach fillna(None) didn't work; used fillna('') & replace)
        intermediate_df = intermediate_df.fillna('').replace([''], [None])

        self.intermediate_player_data = intermediate_df

def main(raw_player_data, raw_games_details):
    """Instantiates data cleanser object and executes appropriate methods to generate intermediate_player_data df."""

    builder = IntermediatePDBuilder(raw_player_data, raw_games_details)
    builder.build_comprehensive_player_data()

    logging.debug('Built intermediate player dataframe. Ready to export & to be used by other cleaning modules.')
    return builder.intermediate_player_data
