import logging
import pandas as pd

class TeamCleanser:
    """Implements cleaning & merging to generate processed_team df containing desired team info with team IDs."""

    def __init__(self, teams_df, nba_teams_df):
        self.raw_teams_kaggle = teams_df
        self.raw_teams_bm = nba_teams_df
        self.processed_team = None

    def clean_teams(self):
        """Performs cleaning/merging steps & assigns processed dataframe into class attribute."""

        logging.debug('Cleaning the raw teams dataframes...')

        # Assigning local df attributes (only with necessary columns needed for merge)
        team_df = self.raw_teams_bm  # (Cols: ['name', 'shortname', 'city', 'state', 'conference', 'division'])
        team_ids = self.raw_teams_kaggle[['TEAM_ID', 'ABBREVIATION']]

        # Convert all column headings to lowercase to facilitate consistent column access
        team_df.columns = team_df.columns.str.lower()
        team_ids.columns = team_ids.columns.str.lower()

        logging.debug('Merging raw teams dataframes to retrieve team IDs...')
        merged_teams_df = pd.merge(team_df, team_ids, left_on='shortname', right_on='abbreviation', how='outer')

        # Re-order the columns to match the schema
        merged_teams_df = merged_teams_df[['team_id', 'name', 'shortname', 'city', 'state', 'conference', 'division']]

        self.processed_team = merged_teams_df

def main(teams_df, nba_teams_df):
    """Instantiates data cleanser object and executes appropriate methods to generate processed team df."""

    cleaner = TeamCleanser(teams_df, nba_teams_df)
    cleaner.clean_teams()

    logging.debug(f'Finished processing NBA team information.')
    return cleaner.processed_team
