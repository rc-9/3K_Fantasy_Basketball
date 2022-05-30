import logging
import pandas as pd

class PlayerTeamCleanser:
    """Cleans & merges to generate processed player_team df from intermediate player & processed team info."""

    def __init__(self, intermediate_player_data, processed_team):
        self.intermediate_player_data = intermediate_player_data
        self.team_data = processed_team
        self.processed_player_team_2020 = None

    def clean_player_team(self):
        """Cleans & merges 2020 player & team info into desired format that matches schema for player_team.csv."""

        logging.debug('Cleaning the intermediate_player_data dataframe for player_team information...')

        # Assigning local df attribute (only with necessary columns needed for processing) for 2020 players only
        player_team_2020 = self.intermediate_player_data[['player_id', 'Team']][0:432]
        team_df = self.team_data[['shortname', 'team_id']]

        # Create dict of team_id:name & map corresponding IDs to players (MERGE not used due to type conversion issues)
        team_id_dict = {team_df.shortname.values.tolist()[i]: team_df.team_id.values.tolist()[i] for i in range(30)}
        player_team_2020['Team'].replace(team_id_dict, inplace=True)

        # Reshape & reformat column order to match schema (changing 'FA' values to 0 so its an int value)
        player_team_2020['Team'].replace('FA', 0, inplace=True)
        player_team_2020.rename(columns={'Team': 'team_id'}, inplace=True)
        player_team_2020 = player_team_2020[['team_id', 'player_id']]

        self.processed_player_team_2020 = player_team_2020

def main(intermediate_player_data, processed_team):
    """Instantiates data cleanser object and executes appropriate methods to generate processed player_team.csv."""

    cleaner = PlayerTeamCleanser(intermediate_player_data, processed_team)
    cleaner.clean_player_team()

    logging.debug(f'Finished processing 2020 player-team information.')
    return cleaner.processed_player_team_2020
