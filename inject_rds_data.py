import argparse
import logging
import os
import sys
import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime
from psycopg2 import Error
from psycopg2.extensions import register_adapter, AsIs
from dotenv import load_dotenv
from progress.bar import Bar

# Register adapter for int64 data types
psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)
# Load environment variables
load_dotenv()

PROCESSED_PATH = './data/processed'
DATASETS = {
	'team': PROCESSED_PATH + '/team.csv',
	'player': PROCESSED_PATH + '/player.csv',
	'player_team': PROCESSED_PATH + '/player_team.csv',
	'player_position': PROCESSED_PATH + '/player_position.csv',
	'fixture': PROCESSED_PATH + '/fixture.csv',
	'player_statistic': PROCESSED_PATH + '/player_statistic.csv'
}

class DBClient:
	"""Creates a database client for handling all database operations."""

	def __init__(self, mode):
		self.connection = None
		self.team = None
		self.player = None
		self.player_team = None
		self.fixture = None
		self.player_statistic= None
		self.player_position = None
		self.is_data = False

		if mode == 'dev': self.dev_mode = True
		else: self.dev_mode = False

		self._create_connection()
		self._load_datasets()

	def _load_datasets(self):
		"""Loads all processed datasets from the corresponding processed directory and loads each into a Pandas
			dataframe. Invokes the _processed_datasets() method for any specific data cleaning based on the default
			Pandas DataFrame creation behavior."""

		logging.error('Loading datasets...')
		for dataset, path in DATASETS.items():
			logging.info('Loading %s data...' % dataset)
			# Dynamically set the class attribute from keys
			setattr(self, dataset, pd.read_csv(
				filepath_or_buffer=path,
				header=0,
				doublequote=False
			))

		# Conduct any cleansing needed for inserts
		self._process_datasets()

	def _process_datasets(self):
		"""Handle any breaking Pandas behavior for the datasets.
			* Fill empty player positions (typically secondary and teriary ) with an empty string
			* Fill empty team_id row data with None to facilitate insert into a nullable numeric field
			* Fill empty player statistic data with 'N/A'
		"""

		logging.error('Pre-processing datasets...')
		try:
			# Fix type conversion errors
			# self.player.birth_year.astype('int32')
			# self.player.draft_year.astype('int32')
			#TODO: Add this to clean module
			self.fixture.drop_duplicates(subset=['fixture_id'], keep='first', inplace=True)

			# Fill empty strings
			self.player_position = self.player_position.fillna('')
			# Fill emtpy numerics
			self.player = self.player.where(pd.notnull(self.player), None)
			# self.player_team = self.player_team.where(pd.notnull(self.player_team), None)
			self.player_team.replace(0, None, inplace=True)
			self.player_statistic = self.player_statistic.where(pd.notnull(self.player_statistic), None)
			self.player_team.team_id.values.astype(int)
		except (Exception, AttributeError) as e:
			self.close_connection()
			raise(e)

	def _clear_tables(self):
		"""Clears any old data from the database and resets the indentities."""

		logging.info('Clearing tables...')
		with self.connection.cursor() as cursor:
			cursor.execute('TRUNCATE TABLE nba3k.player_statistic RESTART IDENTITY CASCADE')
			cursor.execute('TRUNCATE TABLE nba3k.fixture RESTART IDENTITY CASCADE')
			cursor.execute('TRUNCATE TABLE nba3k.player_position RESTART IDENTITY CASCADE')
			cursor.execute('TRUNCATE TABLE nba3k.player RESTART IDENTITY CASCADE')
			cursor.execute('TRUNCATE TABLE nba3k.team RESTART IDENTITY CASCADE')
			cursor.execute('TRUNCATE TABLE nba3k.league RESTART IDENTITY CASCADE')
			self.connection.commit()
		logging.info('Database cleared.')

	def build_database(self):
		"""Builds and seeds the initial database."""

		if self.is_data:
			logging.error('Missing datasets; bailing')
		else:
			logging.info('Building & seeding the initial database...')

			# Insert league
			league_id = self._insert_league()
			self.connection.commit()

			# Insert teams
			logging.info('Inserting teams...')
			bar = Bar('Inserting teams', max= len(self.team))
			for idx, row in self.team.iterrows():
				self._insert_team((
					row['team_id'],
					league_id,
					row['name'],
					row['shortname'],
					row['city'],
					row['state'],
					row['conference'],
					row['division']
				))
				bar.next()
			bar.finish()
			self.connection.commit()

			# Insert players
			logging.info('Inserting players...')
			bar = Bar('Inserting players', max= len(self.player))
			for idx, row in self.player.iterrows():
				self._insert_player((
					int(row['player_id']),
					row['first_name'],
					row['last_name'],
					row['birth_year'],
					row['draft_year'],
					row['draft_pick']
				))
				bar.next()
			bar.finish()
			self.connection.commit()

			# Insert player positions
			logging.info('Inserting player_position...')
			bar = Bar('Inserting player positions', max= len(self.player_position))
			for idx, row in self.player_position.iterrows():
				self._insert_player_position((
					int(row['player_id']),
					row['season'],
					row['position_primary'],
					row['position_secondary'],
					row['position_tertiary']
				))
				bar.next()
			bar.finish()
			self.connection.commit()

			# Insert player teams
			logging.info('Inserting player teams...')
			bar = Bar('Inserting player teams', max= len(self.player_team))
			for idx, row in self.player_team.iterrows():
				self._insert_player_team((
					row['team_id'],
					int(row['player_id'])
				))
				bar.next()
			bar.finish()
			self.connection.commit()

			# Insert fixtures
			logging.info('Inserting fixtures...')
			bar = Bar('Inserting fixtures', max= len(self.fixture))
			for idx, row in self.fixture.iterrows():
				self._insert_fixture((
					row['fixture_id'],
					row['home_team_id'],
					row['away_team_id'],
					row['season'],
					row['played_on'],
					row['game_type'],
					row['home_team_score'],
					row['away_team_score'],
					row['home_team_win'],
					row['away_team_win'],
				))
				bar.next()
			bar.finish()
			self.connection.commit()

			# Insert player_statistic
			logging.info('Inserting player statistics...')
			bar = Bar('Inserting player statistics', max= len(self.player_statistic))
			for idx, row in self.player_statistic.iterrows():
				self._insert_player_statistic((
					row['player_id'],
					row['fixture_id'],
					row['player_status'],
					row['is_starter'],
					row['seconds_played'],
					row['points'],
					row['threes_attempted'],
					row['threes_made'],
					row['field_goals_attempted'],
					row['field_goals_made'],
					row['free_throws_attempted'],
					row['free_throws_made'],
					row['offensive_rebounds'],
					row['defensive_rebounds'],
					row['assists'],
					row['steals'],
					row['blocks'],
					row['turnovers']
				))
				bar.next()
			bar.finish()
			self.connection.commit()

	def _insert_league(self):
		"""Inserts a new league into the database."""
		query = 'INSERT INTO nba3k.league VALUES (%s, %s, %s, %s)'

		with self.connection.cursor() as cursor:
			try:
				cursor.execute(
					query,
					(
						1, 
						'national basketball league', 
						'nba', 
						datetime.now())
				)
				# Get league id for team inserts
				cursor.execute('SELECT league_id FROM nba3k.league')
				league_id = cursor.fetchone()[0]
				logging.info(f'League created with id [{league_id}]')
				self.connection.commit()
				return league_id
			except (Exception, Error) as e:
				logging.error(f'The error \'{e}\' occurred')

	def _insert_team(self, data):
		"""Inserts teams into the database."""
		query = 'INSERT INTO nba3k.team VALUES (%s, %s, %s, %s, %s, %s ,%s, %s, %s)'

		with self.connection.cursor() as cursor:
			try:
				cursor.execute(
					query,
					(
						data[0],
						data[1],
						data[2],
						data[3],
						data[4],
						data[5],
						data[6],
						data[7],
						datetime.now())
				)
			except (Exception, Error) as e:
				logging.error(f'The error \'{str(e).strip()}\' occurred; bailing')
				logging.debug(f'Record was \'{data}\'')
				sys.exit(1)

	def _insert_player(self, data):
		"""Inserts teams into the database."""
		query = 'INSERT INTO nba3k.player VALUES (%s, %s, %s, %s, %s, %s, %s)'

		with self.connection.cursor() as cursor:
			try:
				cursor.execute(
					query,
					(
						data[0],
						data[1],
						data[2],
						data[3],
						data[4],
						data[5],
						datetime.now())
				)
			except (Exception, Error) as e:
				logging.error(f'The error \'{str(e).strip()}\' occurred; bailing')
				logging.debug(f'Record was \'{data}\'')
				sys.exit(1)

	def _insert_player_position(self, data):
		"""Inserts teams into the database."""
		query = 'INSERT INTO nba3k.player_position VALUES (%s, %s, %s, %s, %s, %s)'

		with self.connection.cursor() as cursor:
			try:
				cursor.execute(
					query,
					(
						data[0],
						data[1],
						data[2],
						data[3],
						data[4],
						datetime.now())
				)
			except (Exception, Error) as e:
				logging.error(f'The error \'{e}\' occurred')

	def _insert_player_team(self, data):
		"""Inserts player teams into the database."""
		query = 'INSERT INTO nba3k.player_team (team_id, player_id, created_at) VALUES (%s, %s, %s)'

		with self.connection.cursor() as cursor:
			try:
				cursor.execute(
					query,
					(	data[0],
						data[1],
						datetime.now())
				)
			except (Exception, Error) as e:
				logging.error(f'The error \'{str(e).strip()}\' occurred; bailing')
				logging.debug(f'Record was \'{data}\'')
				sys.exit(1)

	def _insert_fixture(self, data):
		"""Inserts fixtures into the database."""
		query = 'INSERT INTO nba3k.fixture VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

		with self.connection.cursor() as cursor:
			try:
				cursor.execute(
					query,
					(
						data[0],
						data[1],
						data[2],
						data[3],
						data[4],
						str(data[5]),
						data[6],
						data[7],
						data[8],
						data[9],
						datetime.now())
				)
			except (Exception, Error) as e:
				logging.error(f'The error \'{str(e).strip()}\' occurred; bailing')
				logging.debug(f'Record was \'{data}\'')
				sys.exit(1)

	def _insert_player_statistic(self, data):
		"""Inserts player statistics into the database."""
		query = '''INSERT INTO nba3k.player_statistic (
			player_id,
			fixture_id,
			player_status,
			is_starter,
			seconds_played,
			points,
			threes_attempted,
			threes_made,
			field_goals_attempted,
			field_goals_made,
			free_throws_attempted,
			free_throws_made,
			offensive_rebounds,
			defensive_rebounds,
			assists,
			steals,
			blocks,
			turnovers,
			created_at
		)
			VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'''

		with self.connection.cursor() as cursor:
			try:
				cursor.execute(
					query,
					(
						data[0],
						data[1],
						data[2],
						data[3],
						data[4],
						data[5],
						data[6],
						data[7],
						data[8],
						data[9],
						data[10],
						data[11],
						data[12],
						data[13],
						data[14],
						data[15],
						data[16],
						data[17],
						datetime.now())
				)
			except (Exception, Error) as e:
				logging.error(f'The error \'{str(e).strip()}\' occurred; bailing')
				logging.debug(f'Record was \'{data}\'')
				sys.exit(1)

	def _create_connection(self):
		connection = None
		logging.info('Creating connection...')
		try:
			if self.dev_mode:
				connection = psycopg2.connect(
					database='nba3k',
					user='postgres',
					password='#Adm1nistr@t0r',
					host='localhost',
					port=5432
				)
			else:
				connection = psycopg2.connect(
					database= os.getenv('RDS_DB_NAME'),
					user= os.getenv('RDS_USERNAME'),
					password= os.getenv('RDS_PASSWORD'),
					host= os.getenv('RDS_HOSTNAME'),
					port= os.getenv('RDS_PORT')
				)
			print('Connection to PostgreSQL database created')
			self.connection = connection
		except (Exception, Error) as e:
			logging.error(f'The error \'{e}\' occurred during connection creation')

	def close_connection(self):
		"""Closes a database connection."""
		try:
			logging.info('Closing connection...')
			self.connection.close()
			logging.info('Connection to PostgreSQL database closed.')
		except Error as e:
			logging.error(f'The error \'{e}\' occurred')

def logger_setup():
	# Logging setup to appropriate handlers & formatters
	logger = logging.getLogger()
	sh, fh = logging.StreamHandler(), logging.FileHandler('../logs_nba3k.log', 'a')
	sh.setFormatter(logging.Formatter('LOG|%(levelname)s|%(lineno)d: %(message)s'))
	fh.setFormatter(logging.Formatter('%(module)s (%(lineno)d): %(asctime)s | %(levelname)s | %(message)s'))
	logger.setLevel(logging.DEBUG), sh.setLevel(logging.INFO), logger.addHandler(fh), logger.addHandler(sh)
	return logger

def main():
	parser = argparse.ArgumentParser(description='Handle all database transactions for NBA3K')
	parser.add_argument('-d', '--dev-mode', action='store_true', dest='dev_mode')
	parser.add_argument('-c', '--clear', action='store_true', dest='clear_db')
	args = parser.parse_args()

	logger = logger_setup()

	# Handle dev-mode
	if args.dev_mode:
		client = DBClient(mode='dev')
	else:
		client = DBClient(mode='aws')

	# Handle clear
	if args.clear_db:
		client._clear_tables()

	client.build_database()
	client.close_connection()

if __name__ == '__main__':
	main()
