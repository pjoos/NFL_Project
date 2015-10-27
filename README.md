# NFL_Project

This code generates .csv files for easy analysis of NFL data. This is done by webscraping the data from Pro-Football-Reference and storing it in .json files. All the user has to do is edit the variables listed below the header. These are:

## Variables to specify
- data_folder_loc: The folder location for your .json files
- model_folder_loc: The folder location for your .csv file
- model_filename: The name of your .csv file
- which years you want
- start and ending weeks
- team list - by default all teams are listed

## Example 1
The following produces a master file of all data for the 2013 and 2014 seasons. This is the same output as Sample_output.csv.
- data_folder_loc = '../NFL/Data'
- model_folder_loc = '../NFL/Models'
- model_filename = 'Master_13_14.csv' 
- years = [2013, 2014]
- start_week = [1, 1]
- end_week = [17, 17]
- team_list = ['crd', 'atl', 'rav', 'buf', 'car', 'chi', 'cin', 'cle', 'dal', 'den', 'det','gnb', 
'htx', 'clt', 'jax', 'kan', 'mia', 'min', 'nwe', 'nor', 'nyg', 'nyj', 'rai', 'phi', 'pit', 
'sdg', 'sfo', 'sea', 'ram', 'tam', 'oti', 'was']

## Example 2
The following would get 2015 NFL data for the first 6 weeks of the season:
- data_folder_loc = '../NFL/Data'
- model_folder_loc = '../NFL/Models'
- model_filename = 'data_15_w6.csv' 
- years = [2015]
- start_week = [1]
- end_week = [6]
- team_list = ['crd', 'atl', 'rav', 'buf', 'car', 'chi', 'cin', 'cle', 'dal', 'den', 'det','gnb', 
'htx', 'clt', 'jax', 'kan', 'mia', 'min', 'nwe', 'nor', 'nyg', 'nyj', 'rai', 'phi', 'pit', 
'sdg', 'sfo', 'sea', 'ram', 'tam', 'oti', 'was']
