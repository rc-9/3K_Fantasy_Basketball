from datetime import datetime

def generate_game_id(games):
	"""Generates a string representation for a game with the format SS-P-DDD-GG where S: 2-year season identifier, 
	P: season phase (1: pre-season, 2: regular season, 3: post-season), DDD: day in year, GG: game number 
	
	Args:
		games (list): A list of games for which game ids should be generated

	Returns:
		str: The game id string representation
	"""

	game_number = 1
	for g in games:
		#TODO: Use list indexing to get the correct values
		# trim the season to 2-digit (last 2)
		# obtain the season phase from mapping
		# convert the game date to true date and calculate the day in the year from the date
		game_day = datetime.strptime(games[X])
	# 
	pass