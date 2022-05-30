import datetime

# Define constants
CURRENT_YEAR = datetime.date.today().year

def generate_season(year= CURRENT_YEAR):
	"""Generates a string representing an NBA season to be used in API requests. 2-digit
		year assumes 21st century (e.g. 2000's).

	Args:
		year (int): The starting year for an NBA season.

	Returns:
		str: The season string representation; e.g., 2020-21
	"""
	formatted_season = None
	if len(str(year)) == 4 and year is not None and year != '':
		formatted_season = f'{year}-{str(year + 1)[-2: len(str(year))]}'
	elif len(str(year)) == 2 and year is not None and year != '':
		formatted_season = f'20{year}-{str(year + 1)[-2: len(str(year))]}'
	else:
		formatted_season = f'{CURRENT_YEAR}-{str(CURRENT_YEAR + 1)[-2: len(str(CURRENT_YEAR))]}'
	return formatted_season
