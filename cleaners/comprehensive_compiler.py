import logging
import pandas as pd

class Compiler:
    """Implements merging & minor cleaning to generate a compiled CSV containing comprehensive player-game-stats data.
    Purpose: To serve as a go-to reference for analytic modules, rather than compiling individual data every time."""

    def __init__(self, processed_player_statistic, processed_fixture, intermediate_player_data):
        self.processed_player_statistic = processed_player_statistic
        self.processed_fixture = processed_fixture
        self.intermediate_player_data = intermediate_player_data
        self.comprehensive_player_statistic = None

    def compile_data(self):
        """Add player names, game dates info via merge to games details & statistics."""

        stats_df = self.processed_player_statistic
        fixture_df = self.processed_fixture[['fixture_id', 'played_on']]
        player_df = self.intermediate_player_data[['player_id', 'Name']]

        # Use player_id to retrieve player names
        stats_df = pd.merge(stats_df, player_df, on='player_id', how='outer')

        # Use fixture_id to retrieve game dates
        stats_df = pd.merge(stats_df, fixture_df, on='fixture_id', how='outer')

        self.comprehensive_player_statistic = stats_df

    def clean_compiled_data(self):
        """Add any columns of interest & perform minor cleaning measures to finalize comprehensive dataframe."""

        stats_df = self.comprehensive_player_statistic

        # Compute values for extra categories for easier analysis
        stats_df['rebounds'] = stats_df['offensive_rebounds'] + stats_df['defensive_rebounds']
        stats_df['fg%'] = round(stats_df['field_goals_made'] / stats_df['field_goals_attempted'] * 100, 2)
        stats_df['ft%'] = round(stats_df['free_throws_made'] / stats_df['free_throws_attempted'] * 100, 2)
        stats_df['3pt%'] = round(stats_df['threes_made'] / stats_df['threes_attempted'] * 100, 2)

        stats_df.rename(columns={'Name': 'player_name'}, inplace=True)
        stats_df = stats_df[[
            'player_id', 'player_name', 'fixture_id', 'played_on', 'player_status', 'is_starter', 'seconds_played',
            'points', 'offensive_rebounds', 'defensive_rebounds', 'rebounds', 'assists', 'steals', 'blocks',
            'field_goals_made', 'field_goals_attempted', 'fg%', 'free_throws_made', 'free_throws_attempted', 'ft%',
            'threes_made', 'threes_attempted', '3pt%', 'turnovers'
        ]]
        stats_df = stats_df.sort_values(by=['fixture_id'], ascending=True).reset_index(drop=True)

        self.comprehensive_player_statistic = stats_df

def main(processed_player_statistic, processed_fixture, intermediate_player_data):
    """Instantiates compiler object and executes appropriate methods to generate comprehensive_player_statistic df."""

    compiler = Compiler(processed_player_statistic, processed_fixture, intermediate_player_data)
    compiler.compile_data()
    compiler.clean_compiled_data()

    logging.debug('Built comprehensive_player_statistic dataframe. Ready to export & to be used as a reference.')
    return compiler.comprehensive_player_statistic
