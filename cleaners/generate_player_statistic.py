import logging
import pandas as pd

class PlayerStatsCleanser:
    """Implements extensive cleaning & merging to generate processed player_statistic df from several raw sources."""

    def __init__(self, intermediate_player_data, raw_games, raw_games_details, filtered_fixtures):
        self.intermediate_player_data = intermediate_player_data
        self.games_df = raw_games
        self.games_details_data = raw_games_details
        self.filtered_fixtures = filtered_fixtures
        self.processed_player_statistic = None

    def clean_games_details(self):
        """Cleans games_details to match schema format & merges custom playerIDs from intermediate data set."""

        logging.debug('Cleaning the raw games_details_data dataframes...')

        # Assigning local attributes (only with necessary columns needed for processing)
        games_details_df = self.games_details_data[[
            'GAME_ID', 'PLAYER_NAME', 'COMMENT', 'START_POSITION', 'MIN', 'FGM', 'FGA',
            'FG3M', 'FG3A', 'FTM', 'FTA', 'OREB', 'DREB', 'REB', 'AST', 'STL', 'BLK', 'TO', 'PTS'
        ]]
        game_id_df = self.games_df[['GAME_ID']]

        # Remove rows from games_details with game IDs (fixtures) that doesn't exist in game_id_df
        games_details_df = games_details_df[games_details_df["GAME_ID"].isin(self.games_df.GAME_ID.unique())]

        # Edit game_id to new format (YYPNNNNN: YY=Season, P=Phase, NNNNN=GameNumber)
        games_details_df['GAME_ID'] = games_details_df['GAME_ID'].apply(
            lambda x: int(str(x)[1:3] + str(x)[0] + str(x)[3:])
        )

        # Call intermediary cleaning functions to convert column values in desired formats
        games_details_df = self.position_conversion(games_details_df)  # Convert start positions to bool
        games_details_df = self.time_played_conversion(games_details_df)  # Convert min to sec
        games_details_df = self.player_status_conversion(games_details_df)  # Convert to custom status
        games_details_df = self.name_id_conversion(games_details_df)  # Convert names to IDs

        # Reshape & reformat to match schema & get ready for export
        games_details_df.rename(columns={
            'FGM': 'field_goals_made', 'FGA': 'field_goals_attempted', 'FG3M': 'threes_made',
            'FG3A': 'threes_attempted', 'FTM': 'free_throws_made', 'FTA': 'free_throws_attempted',
            'OREB': 'offensive_rebounds', 'DREB': 'defensive_rebounds', 'AST': 'assists',
            'STL': 'steals', 'BLK': 'blocks', 'TO': 'turnovers', 'PTS': 'points', 'GAME_ID': 'fixture_id'
        }, inplace=True)
        games_details_df = games_details_df[[
            'player_id', 'fixture_id', 'player_status', 'is_starter', 'seconds_played', 'points', 'threes_attempted',
            'threes_made', 'field_goals_attempted', 'field_goals_made', 'free_throws_attempted', 'free_throws_made',
            'offensive_rebounds', 'defensive_rebounds', 'assists', 'steals', 'blocks', 'turnovers'
        ]]

        # Filter based on from_season passed in (uses filtered fixture_id from fixture dataframe to do this)
        fixture_df = pd.DataFrame(list(self.filtered_fixtures), columns=['fixture'])
        games_details_df = games_details_df[games_details_df['fixture_id'].isin(fixture_df.fixture.unique())]
        games_details_df = games_details_df.sort_values(
            by=['fixture_id'], ascending=True).reset_index(drop=True)

        logging.debug('Executed all necessary cleaning methods for player_statistic dataframe.')
        self.processed_player_statistic = games_details_df

    def position_conversion(self, games_details_df):
        """Intermediary cleaning step that can be called on to convert position info to is_starter boolean."""

        # Convert is_starter column with corresponding boolean values
        logging.debug('Classifying starters within games_details dataframe...')
        games_details_df.loc[(games_details_df['START_POSITION'] == 'G') | (games_details_df['START_POSITION'] == 'F') |
                             (games_details_df['START_POSITION'] == 'C'), 'START_POSITION'] = True
        games_details_df.loc[(games_details_df['START_POSITION'] != True), 'START_POSITION'] = False
        games_details_df.rename(columns={'START_POSITION': 'is_starter'}, inplace=True)

        return games_details_df

    def time_played_conversion(self, games_details_df):
        """Intermediary cleaning step that can be called on to convert play time from minutes to seconds."""

        # Iterates through each time_played and appropriately modifies & converts value into seconds
        logging.debug('Converting play-time in games_details dataframe...')
        games_details_df.rename(columns={'MIN': 'seconds_played'}, inplace=True)
        games_details_df['seconds_played'] = games_details_df['seconds_played'].fillna(0)

        new_times = []
        for time_played in games_details_df['seconds_played']:
            if isinstance(time_played, str) and ':' in time_played:
                min_sec = time_played.split(':')
                new_times.append(int(min_sec[0]) * 60 + int(min_sec[1]))
            elif isinstance(time_played, str) and ':' not in time_played:
                if '-' in time_played:
                    time_played = time_played.replace('-', '')
                new_times.append(int(time_played) * 60)
            elif isinstance(time_played, int) and time_played == 0:
                new_times.append(0)

        games_details_df['seconds_played'] = new_times

        return games_details_df

    def player_status_conversion(self, games_details_df):
        """Intermediary cleaning step that can be called on to convert & customize player_status data."""

        # Prep status column before making custom conversions
        # games_details_df = games_details_df.loc[:, ~games_details_df.columns.duplicated()]
        games_details_df['player_status'] = games_details_df['COMMENT'].fillna('N/A')

        # Create dictionary that standardizes player status column values to one of 7 corresponding status codes
        status_dict = {
            'DNP-CD': ('coach', 'decision', 'ineligible', 'inactive', 'did not dress', 'conditioning', 'dnp-cd'),
            'DNP-REST': ('rest', 'maintenance', 'load', 'precautionary', 'DNP-REST'),
            'NWT': (
                'personal', 'birth', 'family', 'trade', 'assign', 'signing', 'enroute', 'flight', 'training', 'nbdl',
                'excused', 'signed', 'development', 'g-league', 'self-isolating', 'not with team', 'bereavement',
                'pending', 'D-league', 'NWT-en route', 'NOT_WITH_TEAM', 'funeral', 'did not travel', 'NWT - Out',
                'weather', 'transaction', 'NBADL', 'DND -', 'visa', 'Self Isolating', 'Travel', 'NWT-Out',
                'DNP - NWT', 'NWT-pnuemonia', 'NWT - Pubic Symphysitis', 'NWT -                                   '),
            'SUS': ('suspend', 'suspension', 'suspenion', 'nba sus', 'SUS'),
            'DNP-ILL': ('illness', 'flu', 'migraine', 'infection', 'tonsilitis', 'ill', 'sick', 'strep', 'poisoning'
                                                                                                         'virus',
                        'sinus', 'pox', 'bronchitis', 'medication', 'vertigo', 'pneumonia', 'respiratory',
                        'cold', 'ilness', 'rash', 'fatigue', 'fever', 'VIRUS', 'dizziness', 'tummy', 'allergic', 'food',
                        'Migraine', 'migrane', 'gastroenteritis', 'gastroentritis', 'appendectomy', 'NWT - Migrane'),
            'INJ': ('injury', 'wrist', 'foot', 'ankle', 'knee', 'abdomen', 'abdominal', 'stomach', 'shoulder', 'head',
                    'toe', 'finger', 'elbow', 'strain', 'sprain', 'fracture', 'acl', 'mcl', 'rib', 'back', 'bone',
                    'achilles', 'rehab', 'recovery', 'muscle', 'hip', 'meniscus', 'torn', 'surgery', 'concussion',
                    'contusion', 'calf', 'sore', 'syndrome', 'groin', 'conjunctivitis', 'hematoma', 'recovery', 'lip',
                    'bruise', 'gastroenteritis', 'eye', 'dislocate', 'neck', 'bulging', 'pain', 'nose', 'irritation',
                    'hamstring', 'broke', 'tooth', 'inflammation', 'dental', 'Appendicitis', 'tendon', 'left', 'right',
                    'injured', 'gastric', 'plantar', 'factur', 'pelvic', 'cardiac', 'stitches', 'pubis', 'hernia',
                    'corneal', 'shin', 'medical', 'conussion', 'teeth', 'concussive', 'heart', 'laceration', 'ulnar',
                    'syndrom', 'cramps', 'symphisitis', 'pneumothorax', 'athletic', 'microdiscectomy', 'patella'),
            'PROTOCOL': ('protocol', 'health', 'covid')
        }

        def _map_substring(orig_str, dict_map):
            """Takes in original status value and maps it, based on partial strings, according to template."""
            for new_stat, old_stat in dict_map.items():
                # Iterates through each sub-string value from dict to identify and return corresponding modified status
                for sub_str in old_stat[0:]:
                    if sub_str.lower() in str(orig_str).lower():
                        return new_stat
            # Adjusts edge-case remains from the resulting statuses, using full string value instead of partial
            if orig_str in ('DNP', 'DND'):
                ret_val = 'DNP-CD'
            elif orig_str == 'NWT -':
                ret_val = 'NWT'
            # Returns status as is, if not caught by the dictionary filtering process
            else:
                ret_val = orig_str
            return ret_val

        # Applies function to map original statuses to adjusted codes as defined by map function & status dictionary
        logging.debug('Reorganizing player status info within games_details dataframe...')
        games_details_df['player_status'] = games_details_df['player_status'].apply(
            lambda x: _map_substring(x, status_dict)
        )

        return games_details_df

    def name_id_conversion(self, games_details_df):
        """Uses intermediary player data to replace names from games_details_df with their respective IDs."""

        player_id_df = self.intermediate_player_data[['player_id', 'Name']]

        logging.debug(f'games_details_df row length before merging: {len(games_details_df.index)}')  # 615626
        games_details_df = pd.merge(games_details_df, player_id_df, left_on='PLAYER_NAME', right_on='Name', how='left')
        logging.debug(f'games_details_copy row length after merging: {len(games_details_df.index)}')  # 615626

        return games_details_df

def main(intermediate_player_data, raw_games, raw_games_details, filtered_fixtures):
    """Instantiates data cleanser object and executes appropriate methods to generate processed player_statistic.csv."""

    cleaner = PlayerStatsCleanser(intermediate_player_data, raw_games, raw_games_details, filtered_fixtures)
    cleaner.clean_games_details()

    logging.debug(f'Finished processing games_details data. Export ready for player_statistic dataframe.')
    return cleaner.processed_player_statistic
