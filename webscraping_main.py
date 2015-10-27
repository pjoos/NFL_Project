import requests
import bs4
import json
import datetime
import os
import csv
from random import randint
from math import pi
from time import sleep

'''
Webscrapes data for specified year(s) into .json files located in 'data_folder_loc' and 
generates .csv file into 'model_folder_loc' location. 

The webscraping has a 5-10 second delay per game to avoid spamming the website, so
it takes some time to run.

Each row is a matchup for a given week. Variables for home team begin with 'H_' and 
variables for away team begin with 'A_'.

Includes data for each current week for each variable, as well as year-to-date 
values(exclusive) and yearly averages(except 2015). 

Can also generate up-to-date 2015 results as long as they are on pro-football-reference. 

Variable list is printed by default.
'''

#Change the following as desired
data_folder_loc = '../NFL/Data'
model_folder_loc = '../NFL/Models'
model_filename = 'Master_file_13_14.csv' 
years = [2013, 2014]
start_week = [1, 1]
end_week = [17, 17]
team_list = ['crd', 'atl', 'rav', 'buf', 'car', 'chi', 'cin', 'cle', 'dal', 'den', 'det','gnb', 
'htx', 'clt', 'jax', 'kan', 'mia', 'min', 'nwe', 'nor', 'nyg', 'nyj', 'rai', 'phi', 'pit', 
'sdg', 'sfo', 'sea', 'ram', 'tam', 'oti', 'was']
print_variables = True





def team_rename(team_s):
	if team_s == 'Arizona Cardinals':
		ts = 'crd'
	elif team_s == 'Atlanta Falcons':
		ts = 'atl'
	elif team_s == 'Baltimore Ravens':
		ts = 'rav'
	elif team_s == 'Buffalo Bills':
		ts = 'buf'
	elif team_s == 'Carolina Panthers':
		ts = 'car'
	elif team_s == 'Chicago Bears':
		ts = 'chi'
	elif team_s == 'Cincinnati Bengals':
		ts = 'cin'
	elif team_s == 'Cleveland Browns':
		ts = 'cle'
	elif team_s == 'Dallas Cowboys':
		ts = 'dal'
	elif team_s == 'Denver Broncos':
		ts = 'den'
	elif team_s == 'Detroit Lions':
		ts = 'det'
	elif team_s == 'Green Bay Packers':
		ts = 'gnb'
	elif team_s == 'Houston Texans':
		ts = 'htx'
	elif team_s == 'Indianapolis Colts':
		ts = 'clt'
	elif team_s == 'Jacksonville Jaguars':
		ts = 'jax'
	elif team_s == 'Kansas City Chiefs':
		ts = 'kan'
	elif team_s == 'Miami Dolphins':
		ts = 'mia'
	elif team_s == 'Minnesota Vikings':
		ts = 'min'
	elif team_s == 'New England Patriots':
		ts = 'nwe'
	elif team_s == 'New Orleans Saints':
		ts = 'nor'
	elif team_s == 'New York Giants':
		ts = 'nyg'
	elif team_s == 'New York Jets':
		ts = 'nyj'
	elif team_s == 'Oakland Raiders':
		ts = 'rai'
	elif team_s == 'Philadelphia Eagles':
		ts = 'phi'
	elif team_s == 'Pittsburgh Steelers':
		ts = 'pit'
	elif team_s == 'San Diego Chargers':
		ts = 'sdg'
	elif team_s == 'San Francisco 49ers':
		ts = 'sfo'
	elif team_s == 'Seattle Seahawks':
		ts = 'sea'
	elif team_s == 'St. Louis Rams':
		ts = 'ram'
	elif team_s == 'Tampa Bay Buccaneers':
		ts = 'tam'
	elif team_s == 'Tennessee Titans':
		ts = 'oti'
	elif team_s == 'Washington Redskins':
		ts = 'was'
	else:
		raise NameError('Invalid team name')
	return ts


def get_win_percentages(team_data, Week, Home):
	'''
		Inputs: team_data: dict, Week: game weeks to include (1-17), Home: bool
	'''
	W_L = [0, 0]
	Local_W_L = [0, 0]
	for iter in range(len(team_data['Week'])):
		if team_data['Week'][iter] <= Week:
			if team_data['W/L'][iter] == 'W' and ((Home and team_data['Home'][iter]) or (not Home and not team_data['Home'][iter])):
				W_L[0] += 1
				Local_W_L[0] += 1
			elif team_data['W/L'][iter] == 'W':
				W_L[0] += 1
			elif team_data['W/L'][iter] == 'L' and ((Home and team_data['Home'][iter]) or (not Home and not team_data['Home'][iter])):
				W_L[1] += 1
				Local_W_L[1] += 1
			elif team_data['W/L'][iter] == 'L':
				W_L[1] += 1
			elif team_data['W/L'][iter] == 'T' and ((Home and team_data['Home'][iter]) or (not Home and not team_data['Home'][iter])):
				W_L[0] += 0.5
				W_L[1] += 0.5
				Local_W_L[0] += 0.5
				Local_W_L[1] += 0.5
			elif team_data['W/L'][iter] == 'T':
				W_L[0] += 0.5
				W_L[1] += 0.5
			else:
				raise ValueError('Doesnt work')
	# print W_L, Local_W_L
	if sum(Local_W_L) == 0:
		local_win_p = 'NA'
	else:
		local_win_p = float(Local_W_L[0]) / sum(Local_W_L)
	win_p = float(W_L[0]) / sum(W_L)
	
	return [win_p, local_win_p]


def colsum(stat, weeks, week):
	return sum([val for count, val in enumerate(stat) if weeks[count] <= week])


def get_date(year, date):
	combined_date = year + date
	if combined_date[-2] == ' ':
		combined_date = combined_date[:-1] + '0' + combined_date[-1]
	# print combined_date

	d1 = datetime.datetime.strptime(combined_date, '%Y%B %d')
	d2 = datetime.datetime.strftime(d1, '%Y%m%d0')
	return d2


def official_names(team_name):
	'''
	Replaces some Pro football reference abbreviations with their usual abbreviations
	'''
	teams_to_replace_dict = {'crd':'ARI', 'rav':'BAL', 'htx':'HOU', 'clt':'IND', 'rai':'OAK', 'ram':'STL', 'oti':'TEN'}
	if team_name in ['crd', 'rav', 'htx', 'clt', 'rai', 'ram', 'oti']:
		new_name = teams_to_replace_dict[team_name]
	else:
		new_name = team_name
	return new_name.upper()


def scrape_boxscore(home_str, away_str, date_str, home, opp_full, year):

	result = requests.get('http://www.pro-football-reference.com/boxscores/' + date_str + home_str + '.htm')
	soup = bs4.BeautifulSoup(result.text)

	away_team_official = official_names(away_str)
	home_team_official = official_names(home_str)

	away_dict = {}
	home_dict = {}

	table_linescore = soup.find('table', id='linescore')
	try:
		if table_linescore.find_next('tr').contents[6].text == 'OT':
			OT_game = True
		else:
			OT_game = False
	except:
		OT_game = False
	away_row = table_linescore.find_next('tr').find_next('tr')
	home_row = table_linescore.find_next('tr').find_next('tr').find_next('tr')

	away_dict['Q1'] = int(away_row.contents[1].text)
	away_dict['Q2'] = int(away_row.contents[2].text)
	away_dict['Q3'] = int(away_row.contents[3].text)
	away_dict['Q4'] = int(away_row.contents[4].text)
	if OT_game:
		away_dict['OTpts'] = int(away_row.contents[5].text)
		away_dict['PtsS'] = int(away_row.contents[6].text)
		away_dict['PtsA'] = int(home_row.contents[6].text)
	else:
		away_dict['OTpts'] = 'NA'
		away_dict['PtsS'] = int(away_row.contents[5].text)
		away_dict['PtsA'] = int(home_row.contents[5].text)

	home_dict['Q1'] = int(home_row.contents[1].text)
	home_dict['Q2'] = int(home_row.contents[2].text)
	home_dict['Q3'] = int(home_row.contents[3].text)
	home_dict['Q4'] = int(home_row.contents[4].text)
	if OT_game:
		home_dict['OTpts'] = int(home_row.contents[5].text)
		home_dict['PtsS'] = int(home_row.contents[6].text)

		home_PtsA = int(away_row.contents[6].text)

	else:
		home_dict['OTpts'] = 'NA'

		home_PtsA = int(away_row.contents[5].text)

		# home_dict['PtsA'] = int(away_row.contents[5].text)
		home_dict['PtsS'] = int(home_row.contents[5].text)
	table_team_stats = soup.find('table', id='team_stats')
	for rownum, row in enumerate(table_team_stats.find_all("tr")[1:]):
		if rownum == 0:
			away_dict['O1stD'] = int(row.contents[1].text)
			away_dict['D1stD'] = int(row.contents[2].text)
			home_dict['D1stD'] = int(row.contents[1].text)
			home_dict['O1stD'] = int(row.contents[2].text)
		elif rownum == 1:
			away_rush_vals = row.contents[1].text.split('-')
			home_rush_vals = row.contents[2].text.split('-')
			away_dict['ORushAtt'] = int(away_rush_vals[0])
			away_dict['DRushAtt'] = int(home_rush_vals[0])
			away_dict['ORushYd'] = int(away_rush_vals[1])
			away_dict['DRushYd'] = int(home_rush_vals[1])
			away_dict['ORushTD'] = int(away_rush_vals[2])
			away_dict['DRushTD'] = int(home_rush_vals[2])
			home_dict['DRushAtt'] = int(away_rush_vals[0])
			home_dict['ORushAtt'] = int(home_rush_vals[0])
			home_dict['DRushYd'] = int(away_rush_vals[1])
			home_dict['ORushYd'] = int(home_rush_vals[1])
			home_dict['DRushTD'] = int(away_rush_vals[2])
			home_dict['ORushTD'] = int(home_rush_vals[2])
		elif rownum == 2:
			away_pass_vals = row.contents[1].text.split('-')
			home_pass_vals = row.contents[2].text.split('-')

			home_OPassAtt = int(home_pass_vals[1])
			home_DPassAtt = int(away_pass_vals[1])
			# home_OINT = int(home_pass_vals[4])

			away_dict['OPassComp'] = int(away_pass_vals[0])
			away_dict['DPassComp'] = int(home_pass_vals[0])
			away_dict['OPassAtt'] = int(away_pass_vals[1])
			away_dict['DPassAtt'] = int(home_pass_vals[1])
			home_dict['DPassComp'] = int(away_pass_vals[0])
			home_dict['OPassComp'] = int(home_pass_vals[0])
			#The following try/except blocks correct for when teams have negative total passing yards (see boxscores/200910180nwe.htm)
			try:
				away_dict['OPassYd'] = int(away_pass_vals[2])
				home_dict['DPassYd'] = int(away_pass_vals[2])
				away_dict['OPassTD'] = int(away_pass_vals[3])
				home_dict['DPassTD'] = int(away_pass_vals[3])
				away_dict['OINT'] = int(away_pass_vals[4])
				home_dict['DINT'] = int(away_pass_vals[4])
			except:
				away_dict['OPassYd'] = -int(away_pass_vals[3])
				home_dict['DPassYd'] = -int(away_pass_vals[3])
				away_dict['OPassTD'] = int(away_pass_vals[4])
				home_dict['DPassTD'] = int(away_pass_vals[4])
				away_dict['OINT'] = int(away_pass_vals[5])
				home_dict['DINT'] = int(away_pass_vals[5])
			try:
				away_dict['DPassYd'] = int(home_pass_vals[2])
				away_dict['DPassTD'] = int(home_pass_vals[3])
				away_dict['DINT'] = int(home_pass_vals[4])
				home_dict['OPassYd'] = int(home_pass_vals[2])
				home_dict['OPassTD'] = int(home_pass_vals[3])
				home_OINT = int(home_pass_vals[4])
			except:
				away_dict['DPassYd'] = -int(home_pass_vals[3])
				away_dict['DPassTD'] = int(home_pass_vals[4])
				away_dict['DINT'] = int(home_pass_vals[5])
				home_dict['OPassYd'] = -int(home_pass_vals[3])
				home_dict['OPassTD'] = int(home_pass_vals[4])
				home_OINT = int(home_pass_vals[5])
		elif rownum == 3:
			away_sack_vals = row.contents[1].text.split('-')
			home_sack_vals = row.contents[2].text.split('-')
			away_dict['OSack'] = int(away_sack_vals[0])
			away_dict['DSack'] = int(home_sack_vals[0])
			away_dict['OSackYd'] = int(away_sack_vals[1])
			away_dict['DSackYd'] = int(home_sack_vals[1])
			home_dict['DSack'] = int(away_sack_vals[0])
			home_dict['OSack'] = int(home_sack_vals[0])

			home_OSackYd = int(home_sack_vals[1])

			home_dict['DSackYd'] = int(away_sack_vals[1])
		elif rownum == 4:
			away_dict['ONetPassYd'] = int(row.contents[1].text)
			away_dict['DNetPassYd'] = int(row.contents[2].text)

			home_ONetPassYd = int(row.contents[2].text)

			home_dict['DNetPassYd'] = int(row.contents[1].text)
		elif rownum == 5:
			away_dict['OTotalYd'] = int(row.contents[1].text)
			away_dict['DTotalYd'] = int(row.contents[2].text)
			home_dict['DTotalYd'] = int(row.contents[1].text)
			home_dict['OTotalYd'] = int(row.contents[2].text)
		elif rownum == 6:
			away_fum_vals = row.contents[1].text.split('-')
			home_fum_vals = row.contents[2].text.split('-')
			away_dict['Fum'] = int(away_fum_vals[0])
			away_dict['OFumLost'] = int(away_fum_vals[1])

			home_OFumLost = int(home_fum_vals[1])

			home_dict['Fum'] = int(home_fum_vals[0])
		elif rownum == 7:
			away_dict['OTO'] = int(row.contents[1].text)
			away_dict['DTO'] = int(row.contents[2].text)
			home_dict['DTO'] = int(row.contents[1].text)
			home_dict['OTO'] = int(row.contents[2].text)
		elif rownum == 8:
			away_pen_vals = row.contents[1].text.split('-')
			home_pen_vals = row.contents[2].text.split('-')
			away_dict['Pen'] = int(away_pen_vals[0])
			away_dict['PenYd'] = int(away_pen_vals[1])
			home_dict['Pen'] = int(home_pen_vals[0])
			home_dict['PenYd'] = int(home_pen_vals[1])
		elif rownum == 9:
			away_third_vals = row.contents[1].text.split('-')
			home_third_vals = row.contents[2].text.split('-')
			away_dict['O3rdConv'] = int(away_third_vals[0])
			away_dict['D3rdConv'] = int(home_third_vals[0])
			away_dict['O3rdAtt'] = int(away_third_vals[1])
			away_dict['D3rdAtt'] = int(home_third_vals[1])
			home_dict['D3rdConv'] = int(away_third_vals[0])
			home_dict['O3rdConv'] = int(home_third_vals[0])
			home_dict['D3rdAtt'] = int(away_third_vals[1])
			home_dict['O3rdAtt'] = int(home_third_vals[1])
		elif rownum == 10:
			away_fourth_vals = row.contents[1].text.split('-')
			home_fourth_vals = row.contents[2].text.split('-')
			away_dict['O4thConv'] = int(away_fourth_vals[0])
			away_dict['D4thConv'] = int(home_fourth_vals[0])
			away_dict['O4thAtt'] = int(away_fourth_vals[1])
			away_dict['D4thAtt'] = int(home_fourth_vals[1])
			home_dict['D4thConv'] = int(away_fourth_vals[0])
			home_dict['O4thConv'] = int(home_fourth_vals[0])
			home_dict['D4thAtt'] = int(away_fourth_vals[1])
			home_dict['O4thAtt'] = int(home_fourth_vals[1])
		elif rownum == 11 and 'Total Plays' in row.text:
			away_dict['OPlays'] = int(row.contents[1].text)
			away_dict['DPlays'] = int(row.contents[2].text)
			home_dict['DPlays'] = int(row.contents[1].text)
			home_dict['OPlays'] = int(row.contents[2].text)
		elif rownum == 11:
			away_dict['OPlays'] = away_dict['OPassAtt'] + away_dict['ORushAtt'] + away_dict['OSack']
			away_dict['DPlays'] = away_dict['DPassAtt'] + away_dict['DRushAtt'] + away_dict['DSack']
			home_dict['DPlays'] = home_DPassAtt + home_dict['DRushAtt'] + home_dict['DSack']
			home_dict['OPlays'] = home_OPassAtt + home_dict['ORushAtt'] + home_dict['OSack']
			away_time_vals = row.contents[1].text.split(':')
			home_time_vals = row.contents[2].text.split(':')
			away_dict['ToP'] = float(away_time_vals[0]) + float(away_time_vals[1]) / 60.0
			home_dict['ToP'] = float(home_time_vals[0]) + float(home_time_vals[1]) / 60.0			
		elif rownum == 12:
			away_time_vals = row.contents[1].text.split(':')
			home_time_vals = row.contents[2].text.split(':')
			away_dict['ToP'] = float(away_time_vals[0]) + float(away_time_vals[1]) / 60.0
			home_dict['ToP'] = float(home_time_vals[0]) + float(home_time_vals[1]) / 60.0
	
	if year > 2007:
		table_def_stats = soup.find('table', id='def_stats')
		away_dict['FF'] = 0
		home_dict['FF'] = 0
		away_dict['DTdsS'] = 0
		home_dict['DTdsS'] = 0
		for rownum, row in enumerate(table_def_stats.find_all("tr")):
			if len(row.attrs['class']) == 1:
				if year < 2015:
					if row.contents[3].text.lower() == away_team_official.lower() and row.contents[11].text != '':
						away_dict['DTdsS'] += int(row.contents[11].text)
					elif row.contents[3].text.lower() == home_team_official.lower() and row.contents[11].text != '':
						home_dict['DTdsS'] += int(row.contents[11].text)
					if row.contents[3].text.lower() == away_team_official.lower() and row.contents[19].text != '':
						away_dict['DTdsS'] += int(row.contents[19].text)
					elif row.contents[3].text.lower() == home_team_official.lower() and row.contents[19].text != '':
						home_dict['DTdsS'] += int(row.contents[19].text)
					if row.contents[3].text.lower() == away_team_official.lower() and row.contents[21].text != '':
						away_dict['FF'] += int(row.contents[21].text)
					elif row.contents[3].text.lower() == home_team_official.lower() and row.contents[21].text != '':
						home_dict['FF'] += int(row.contents[21].text)
				else:
					if row.contents[3].text.lower() == away_team_official.lower() and row.contents[23].text != '':
						away_dict['DTdsS'] += int(row.contents[23].text)
					elif row.contents[3].text.lower() == home_team_official.lower() and row.contents[23].text != '':
						home_dict['DTdsS'] += int(row.contents[23].text)
					if row.contents[3].text.lower() == away_team_official.lower() and row.contents[9].text != '':
						away_dict['DTdsS'] += int(row.contents[9].text)
					elif row.contents[3].text.lower() == home_team_official.lower() and row.contents[9].text != '':
						home_dict['DTdsS'] += int(row.contents[9].text)
					if row.contents[3].text.lower() == away_team_official.lower() and row.contents[25].text != '':
						away_dict['FF'] += int(row.contents[25].text)
					elif row.contents[3].text.lower() == home_team_official.lower() and row.contents[25].text != '':
						home_dict['FF'] += int(row.contents[25].text)
	try:
		# VALID AFTER 1997 ONLY!
		table_drive_stats = soup.find_all('table', class_='sortable  stats_table')
		if year > 2014:
			table_drive_away_stats = table_drive_stats[2]
			table_drive_home_stats = table_drive_stats[3]
		else:
			table_drive_away_stats = table_drive_stats[0]
			table_drive_home_stats = table_drive_stats[1]
		away_drives = 0
		away_scores = 0
		away_tds = 0
		for rownum, row in enumerate(table_drive_away_stats.find_all("tr")[1:]):
			away_drives += 1
			if row.contents[15].text == 'Touchdown':
				away_scores += 1
				away_tds += 1
			elif row.contents[15].text == 'Field Goal':
				away_scores += 1
		away_dict['OScores'] = away_scores
		away_dict['OTds'] = away_tds
		away_dict['ODrives'] = away_drives
		home_dict['DScoresA'] = away_scores
		home_dict['DTdsA'] = away_tds
		home_dict['DDrives'] = away_drives
		home_drives = 0
		home_scores = 0
		home_tds = 0
		for rownum, row in enumerate(table_drive_home_stats.find_all("tr")[1:]):
			home_drives += 1
			if row.contents[15].text == 'Touchdown':
				home_scores += 1
				home_tds += 1
			elif row.contents[15].text == 'Field Goal':
				home_scores += 1
		home_dict['OScores'] = home_scores
		away_dict['DScoresA'] = home_scores
		away_dict['DTdsA'] = home_tds

		home_OTds = home_tds
		home_ODrives = home_drives

		away_dict['DDrives'] = home_drives
	except:	#Error in Det/GNB game on 2014-12-28
		if date_str == '201412280' and home_str == 'gnb':
			away_dict['OScores'] = 3
			away_dict['OTds'] = 3
			away_dict['ODrives'] = 12
			home_dict['DScoresA'] = 3
			home_dict['DTdsA'] = 3
			home_dict['DDrives'] = 12
			home_dict['OScores'] = 3
			away_dict['DScoresA'] = 3
			away_dict['DTdsA'] = 3
			home_OTds = 3
			home_ODrives = 10
			away_dict['DDrives'] = 10
		else:
			raise ValueError('Drive tables not working for: %s, %s @ %s' %(date_str, away_str.upper(), home_str.upper())) 

	table_game_info = soup.find('table', id='game_info')
	for count, row in enumerate(table_game_info.find_all("tr")[1:]):
		# Sometimes no weather data...bullshit!
		# if count in [3, 4, 7]:
		# 	away_dict[row.find_next("td").text] = row.find_next("td").find_next("td").text.strip()
		# 	home_dict[row.find_next("td").text] = row.find_next("td").find_next("td").text.strip()
		col_name = row.find_next("td").text
		
		if col_name == 'Vegas Line' and row.find_next("td").find_next("td").text == 'Pick':
			home_dict[row.find_next("td").text] = 0.0
			away_dict[row.find_next("td").text] = 0.0
		elif col_name == 'Vegas Line' and opp_full in row.find_next("td").find_next("td").text.strip():
			if team_rename(opp_full) == home_str:
				home_dict[row.find_next("td").text] = -1 * float(row.find_next("td").find_next("td").text.split('-')[-1])
				away_dict[row.find_next("td").text] = float(row.find_next("td").find_next("td").text.split('-')[-1])
			else:
				home_dict[row.find_next("td").text] = float(row.find_next("td").find_next("td").text.split('-')[-1])
				away_dict[row.find_next("td").text] = -1 * float(row.find_next("td").find_next("td").text.split('-')[-1])
		elif col_name == 'Vegas Line':
			if team_rename(opp_full) == home_str:
				home_dict[row.find_next("td").text] = float(row.find_next("td").find_next("td").text.split('-')[-1])
				away_dict[row.find_next("td").text] = -1 * float(row.find_next("td").find_next("td").text.split('-')[-1])
			else:
				home_dict[row.find_next("td").text] = -1 * float(row.find_next("td").find_next("td").text.split('-')[-1])
				away_dict[row.find_next("td").text] = float(row.find_next("td").find_next("td").text.split('-')[-1])
		elif col_name == 'Over/Under':
			away_dict[row.find_next("td").text] = float(row.find_next("td").find_next("td").text.split('(')[0].strip())
			home_dict[row.find_next("td").text] = float(row.find_next("td").find_next("td").text.split('(')[0].strip())


	# print home_dict
	# print len(home_dict.keys())
	# print home_dict.keys()
	# print away_dict

	# print home_DPassAtt, home_OSackYd, home_OFumLost, home_OINT, home_ONetPassYd, home_OPassAtt, home_PtsA, home_OTds, home_ODrives
	home_dict.update({'DPassAtt': home_DPassAtt, 'OSackYd': home_OSackYd, 'OFumLost': home_OFumLost, 'OINT': home_OINT, 'ONetPassYd': home_ONetPassYd, 'OPassAtt': home_OPassAtt, 'PtsA': home_PtsA, 'OTds': home_OTds, 'ODrives': home_ODrives})

	if home:
		return_dict = home_dict
	else:
		return_dict = away_dict

	return return_dict


def scrape_gamelog(team, year, max_week):
	result = requests.get('http://www.pro-football-reference.com/teams/' + team + '/' + year + '.htm')
	# print result.encoding
	soup = bs4.BeautifulSoup(result.text)

	table_gamelog = soup.find('table', id = 'team_gamelogs')

	dict1 = {}
	ordered_keys = []
	for count, row in enumerate(table_gamelog.find_all("th")[5:]):
		# print count, row.text
		if count in [1, 3, 21, 22,23] + range(9, 21):
			ordered_keys.append('Skip')
			continue
		elif count in [0, 2, 5, 6, 8]:
			dict1[row.text] = []
			ordered_keys.append(row.text)
		elif count == 4:
			dict1['W/L'] = []
			ordered_keys.append('W/L')
		elif count == 7:
			dict1['Home'] = []
			ordered_keys.append('Home')
	# print dict1.keys()
	# print ordered_keys
	# print dict1

	first_row = True
	for count, row in enumerate(table_gamelog.find_all("tr")):
		# row_data = row.find_all("td")
		# print len(row_data), row_data
		# print count
		if (count - 1) <= max_week and row.text.split('\n')[1].isdigit() and row.text.split('\n')[ordered_keys.index('Opp') + 1] != 'Bye Week':
			for count, col in enumerate(row.find_all("td")):
				if count == 0:
					if col.text == '':
						dict1[ordered_keys[count]].append(0)
						week = int(col.text)
					else:
						week = int(col.text)
						dict1[ordered_keys[count]].append(int(col.text))
				elif count in [4, 6]:
					dict1[ordered_keys[count]].append(col.text)
				elif count == 8:
					opp = col.text
					dict1[ordered_keys[count]].append(col.text)
				elif count == 2:
					if 'January' in col.text or 'February' in col.text:
						date_str = get_date(str(int(year) + 1), col.text)
					else:
						date_str = get_date(year, col.text)
					dict1[ordered_keys[count]].append(date_str)
				elif count == 5:
					if col.text == 'OT':
						dict1[ordered_keys[count]].append(True)
					else:
						dict1[ordered_keys[count]].append(False)
				elif count == 7:
					if col.text == '@':
						home = False
						dict1[ordered_keys[count]].append(False)
					else:
						home = True
						dict1[ordered_keys[count]].append(True)

			if home:
				home_str = team
				away_str = team_rename(opp)
			else:
				away_str = team
				home_str = team_rename(opp)
			# print dict1
			# print home, week, home_str, away_str, opp, date_str

			# Now get boxscore for each row (home_str, away_str, date_str, home, opp_full, year):\
			print 'Webscraping boxscore for week ' +  str(week) + ' for team ' + team + ' for year ' + str(year)			
			boxscore_dict = scrape_boxscore(home_str, away_str, date_str, home, opp, int(year))
			sleep(randint(80,150) / 7.0 / pi)
			# print boxscore_dict
			if first_row:
				first_row = False
				for key, value in boxscore_dict.items():
					dict1[key] = [value]
			else:
				for key, value in boxscore_dict.items():
					dict1[key].append(value)


	with open(os.path.join(data_folder_loc, data_name + team + '_' + year + '.json'), 'w') as game_file:
		json.dump(dict1, game_file)		        	
	return dict1


def create_row_data_train(home_game_data, away_team, Week, year, Model, measure, max_week):

	away_str = team_rename(away_team)

	if not os.path.isfile(os.path.join(data_folder_loc, data_name + away_str + '_' + year + '.json')):
		print 'Webscraping game log for away team (with a short delay)'
		scrape_gamelog(away_str, year, max_week)
		sleep(randint(80,150) / 7.0 / pi)

	away_file = open(os.path.join(data_folder_loc, data_name + away_str + '_' + year + '.json'),'r')
	away_game_data = json.load(away_file)


	#First add home data
	row_data = []

	if measure == 'single game':
		for category in Model:
			week_index = home_game_data['Week'].index(Week)
			row_data.append(home_game_data[category][week_index])
		for category in Model:
			week_index = away_game_data['Week'].index(Week)
			row_data.append(away_game_data[category][week_index])
	elif measure == 'avg_ytd':
		home_total_games_played = sum([1 for i in home_game_data['Week'] if i < Week])
		away_total_games_played = sum([1 for i in away_game_data['Week'] if i < Week])
		for category in Model:
			if Week == 1:
				row_data.append('NA')
			elif category == 'WinP':
				row_data.append(get_win_percentages(home_game_data, Week-1, True)[0])
			elif category == 'LocWinP':
				row_data.append(get_win_percentages(home_game_data, Week-1, True)[1])
			else:
				row_data.append(colsum(home_game_data[category], home_game_data['Week'], Week-1) / float(home_total_games_played))
		#Now add away data
		for category in Model:
			if Week == 1:
				row_data.append('NA')
			elif category == 'WinP':
				row_data.append(get_win_percentages(away_game_data, Week-1, False)[0])
			elif category == 'LocWinP':
				row_data.append(get_win_percentages(away_game_data, Week-1, False)[1])
			else:
				row_data.append(colsum(away_game_data[category], away_game_data['Week'], Week-1) / float(away_total_games_played))
	elif measure == 'avg_yr':
		for category in Model:
			if category == 'WinP':
				row_data.append(get_win_percentages(home_game_data, 17, True)[0])
			elif category == 'LocWinP':
				row_data.append(get_win_percentages(home_game_data, 17, True)[1])
			else:
				row_data.append(colsum(home_game_data[category], home_game_data['Week'], 17) / 16.0)
		#Now add away data
		for category in Model:
			if category == 'WinP':
				row_data.append(get_win_percentages(away_game_data, 17, False)[0])
			elif category == 'LocWinP':
				row_data.append(get_win_percentages(away_game_data, 17, False)[1])
			else:
				row_data.append(colsum(away_game_data[category], away_game_data['Week'],17) / 16.0)

	# print row_data
	away_file.close()
	return row_data



master_variable_list_to_avg = ['Q1', 'Q3', 'Q2', 'DTO', 'Q4', 'DNetPassYd', 
'DRushAtt', 'Pen', 'DINT', 'FF', 'DPassYd', 'OTotalYd', 'DSackYd', 
'D3rdAtt', 'OPassTD', 'DRushTD', 'ToP', 'DRushYd', 
'ORushAtt', 'DTotalYd', 'PenYd', 'DDrives', 'O1stD', 'O4thConv', 'OPassComp',
 'ORushYd', 'OPassYd', 'OScores', 'ORushTD', 'DPassTD', 'OSack', 'OFumLost', 
 'O3rdConv', 'DScoresA', 'DPassComp', 'O4thAtt', 'Fum', 'DTdsA', 
  'OTO', 'DPlays', 'D1stD', 'PtsS', 'DSack', 'O3rdAtt', 'D4thConv', 'D3rdConv', 
  'D4thAtt', 'DTdsS', 'DPassAtt', 'OINT', 'OSackYd', 'PtsA', 'OPassAtt',
   'OPlays', 'ODrives', 'OTds', 'ONetPassYd']


master_variable_list = master_variable_list_to_avg
master_variable_list_avg_ytd = ['WinP', 'LocWinP'] + master_variable_list
master_variable_list_avg_yr = ['WinP', 'LocWinP'] + master_variable_list


variables = ['H_' + i for i in master_variable_list] + ['A_' + i for i in master_variable_list] + ['H_' + i + '_Avg_YTD' for i in master_variable_list_avg_ytd] + ['A_' + i + '_Avg_YTD' for i in master_variable_list_avg_ytd] + ['H_' + i + '_Avg_Yr' for i in master_variable_list_avg_yr] + ['A_' + i + '_Avg_Yr' for i in master_variable_list_avg_yr]
variables_15 = ['H_' + i for i in master_variable_list] + ['A_' + i for i in master_variable_list] + ['H_' + i + '_Avg_YTD' for i in master_variable_list_avg_ytd] + ['A_' + i + '_Avg_YTD' for i in master_variable_list_avg_ytd]

if print_variables:
	print variables

header = ['Year', 'Week', 'Home', 'Away', 'Result', 'Vegas_Line', 'Over/Under'] + variables
header_15 = ['Year', 'Week', 'Home', 'Away', 'Result', 'Vegas_Line', 'Over/Under'] + variables_15


model_file = os.path.join(model_folder_loc, model_filename)
with open(model_file, 'wb') as myfile:
	wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
	if years != [2015]:
		wr.writerow(header)
	else:
		wr.writerow(header_15)
	for count, year in enumerate(years):
		if year == 2015:
			data_name = 'data_w' + str(end_week[-1]) + '_'
		else:
			data_name = 'all_data_'
		for team in team_list:
			if not os.path.isfile(os.path.join(data_folder_loc, data_name + team + '_' + str(year) + '.json')):
				print 'Webscraping game log for home team (with a short delay)'
				scrape_gamelog(team, str(year), end_week[count])
				sleep(randint(80,150) / 7.1 / pi)
			with open(os.path.join(data_folder_loc, data_name + team + '_' + str(year) + '.json'),'r') as team_file:
				team_data = json.load(team_file)
				for week_num in range(start_week[count], end_week[count] + 1):
					if week_num in team_data['Week'] and team_data['Home'][team_data['Week'].index(week_num)]: #if not a bye week and a home game
						week_index = team_data['Week'].index(week_num)
						vegas_index = team_data['Vegas Line'][week_index]
						over_under_index = team_data['Over/Under'][week_index]
						away_team_name = team_data['Opp'][week_index]
						if team_data['W/L'][week_index] == 'W':
							result = 1
						elif team_data['W/L'][week_index] == 'T':
							result = 0.5
						else:
							result = 0
						if year != 2015:
							row_data_single = create_row_data_train(team_data, away_team_name, week_num, str(year), master_variable_list, 'single game', end_week[count])
							row_data_avg_ytd = create_row_data_train(team_data, away_team_name, week_num, str(year), master_variable_list_avg_ytd, 'avg_ytd', end_week[count])
							row_data_avg_yr = create_row_data_train(team_data, away_team_name, week_num, str(year), master_variable_list_avg_yr, 'avg_yr', end_week[count])
							wr.writerow([str(year), str(week_num), team, team_rename(away_team_name), result, vegas_index, over_under_index] + row_data_single + row_data_avg_ytd + row_data_avg_yr)
						else:
							row_data_single = create_row_data_train(team_data, away_team_name, week_num, str(year), master_variable_list, 'single game', end_week[count])
							row_data_avg_ytd = create_row_data_train(team_data, away_team_name, week_num, str(year), master_variable_list_avg_ytd, 'avg_ytd', end_week[count])
							wr.writerow([str(year), str(week_num), team, team_rename(away_team_name), result, vegas_index, over_under_index] + row_data_single + row_data_avg_ytd)