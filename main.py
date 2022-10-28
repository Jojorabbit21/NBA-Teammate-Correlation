import os
import sys
import time

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

base_url = 'https://www.basketball-reference.com{}'

teams = [
  'ATL',
  'BOS',
  'BKN',
  'CHA',
  'CHI',
  'CLE',
  'DET',
  'DAL',
  'TOR',
  'NYK',
  'PHI',
  'IND',
  'MIL',
  'MIA',
  'WAS',
  'ORL',
  'OKC',
  'POR',
  'UTA',
  'DEN',
  'MIN',
  'GSW',
  'LAC',
  'LAL',
  'SAC',
  'PHO',
  'SAS',
  'MEM',
  'HOU',
  'NOP',
]

full_to_abbr = {
  'Atlanta Hawks': 'ATL',
  'Boston Celtics': 'BOS',
  'Brooklyn Nets': 'BRK',
  'Charlotte Hornets': 'CHO',
  'Chicago Bulls': 'CHI',
  'Cleveland Cavaliers': 'CLE',
  'Detroit Pistons': 'DET',
  'Dallas Mavericks': 'DAL',
  'Toronto Raptors': 'TOR',
  'New York Knicks': 'NYK',
  'Philadelphia 76ers': 'PHI',
  'Indiana Pacers': 'IND',
  'Milwaukee Bucks': 'MIL',
  'Miami Heat': 'MIA',
  'Washington Wizards': 'WAS',
  'Orlando Magic': 'ORL',
  'Oklahoma City Thunder': 'OKC',
  'Portland Trail Blazers': 'POR',
  'Utah Jazz': 'UTA',
  'Denver Nuggets': 'DEN',
  'Minnesota Timberwolves': 'MIN',
  'Golden State Warriors': 'GSW',
  'Los Angeles Clippers': 'LAC',
  'Los Angeles Lakers': 'LAL',
  'Sacramento Kings': 'SAC',
  'Phoenix Suns': 'PHO',
  'San Antonio Spurs': 'SAS',
  'Memphis Grizzlies': 'MEM',
  'Houston Rockets': 'HOU',
  'New Orleans Pelicans': 'NOP',
}

abbr_to_full = {
  'ATL': 'Atlanta Hawks',
  'BOS': 'Boston Celtics',
  'BRK': 'Brooklyn Nets',
  'BKN': 'Brooklyn Nets',
  'CHA': 'Charlotte Hornets' ,
  'CHO': 'Charlotte Hornets' ,
  'CHI': 'Chicago Bulls',
  'CLE': 'Cleveland Cavaliers',
  'DET': 'Detroit Pistons',
  'DAL': 'Dallas Mavericks',
  'TOR': 'Toronto Raptors',
  'NYK': 'New York Knicks',
  'PHI': 'Philadelphia 76ers',
  'IND': 'Indiana Pacers',
  'MIL': 'Milwaukee Bucks',
  'MIA': 'Miami Heat',
  'WAS': 'Washington Wizards',
  'ORL': 'Orlando Magic',
  'OKC': 'Oklahoma City Thunder',
  'POR': 'Portland Trail Blazers',
  'UTA': 'Utah Jazz',
  'DEN': 'Denver Nuggets',
  'MIN': 'Minnesota Timberwolves',
  'GSW': 'Golden State Warriors',
  'LAC': 'Los Angeles Clippers',
  'LAL': 'Los Angeles Lakers',
  'SAC': 'Sacramento Kings',
  'PHO': 'Phoenix Suns',
  'SAS': 'San Antonio Spurs',
  'MEM': 'Memphis Grizzlies',
  'HOU': 'Houston Rockets',
  'NOP': 'New Orleans Pelicans',
}

def sanitize_abbr(abbr):
  if abbr == 'CHO':
    return 'CHA'
  if abbr == 'BRK':
    return 'BKN'
  else:
    return abbr

def sanitize_abbr_to_full(str):
  if str == 'BRK':
    str = 'BKN'
  elif str == 'CHO':
    str = 'CHA'
  return abbr_to_full[str]

def get_gamemonth():
  seasons_url = [
    'https://www.basketball-reference.com/leagues/NBA_2020_games.html',
    'https://www.basketball-reference.com/leagues/NBA_2021_games.html',
    'https://www.basketball-reference.com/leagues/NBA_2022_games.html'
  ]
  month_url = []
  for url in seasons_url:
    req = requests.get(url)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    
    tab = soup.select("#content > div.filter > div > a")
    for i in tab:
      month_url.append(i['href'])

  df = pd.DataFrame(month_url)
  df.to_csv('urllist.csv')
  
def get_boxscores_url():
  month_df = pd.read_csv('urllist.csv')
  boxscore_url = []
  for row in month_df.itertuples():
    req = requests.get(base_url.format(row[2]))
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    url = soup.select("#schedule > tbody > tr > td:nth-child(7) > a")
    for i in url:
      boxscore_url.append(i['href'])
  df = pd.DataFrame(boxscore_url)
  df.to_csv('boxscoreurl.csv')
  
def get_boxscore(url):
  req = requests.get(base_url.format(url))
  html = req.text
  soup = BeautifulSoup(html, 'html.parser')
  aname = soup.select_one("#content > div.scorebox > div:nth-child(1) > div:nth-child(1) > strong > a").text
  hname = soup.select_one("#content > div.scorebox > div:nth-child(2) > div:nth-child(1) > strong > a").text
  
  filename = url.split("/")[2].replace('.html','')
  filename = filename + "@" + full_to_abbr[aname]
  print(filename)
  dfs = pd.read_html(base_url.format(url))
  '''
    No OT (len: 16) 0,7,8,15
    1 OT (len: 18) 0,8,9,17
    2 OT (len: 20) 0,9,10,19
  '''
  away_b = dfs[0].droplevel(axis=1, level=0)
  away_a = dfs[int((len(dfs)/2))-1].droplevel(axis=1, level=0)
  home_b = dfs[int((len(dfs)/2))].droplevel(axis=1, level=0)
  home_a = dfs[int(len(dfs)-1)].droplevel(axis=1, level=0)
  
  away_b.drop(away_b[away_b['Starters'] == 'Reserves'].index, inplace=True)
  away_b.replace("Did Not Play", 0, inplace=True)
  away_b.replace("Did Not Dress", 0, inplace=True)
  away_b.replace("Not With Team", 0, inplace=True)
  away_b.fillna(0, inplace=True)
  away_b['Team'] = np.nan
  
  away_a.drop(away_a[away_a['Starters'] == 'Reserves'].index, inplace=True)
  away_a.replace("Did Not Play", 0, inplace=True)
  away_a.replace("Did Not Dress", 0, inplace=True)
  away_a.replace("Not With Team", 0, inplace=True)
  away_a.fillna(0, inplace=True)
  away_a = away_a[['MP', 'TS%', 'eFG%', '3PAr', 'FTr', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%', 'ORtg', 'DRtg']]
  
  home_b.drop(home_b[home_b['Starters'] == 'Reserves'].index, inplace=True)
  home_b.replace("Did Not Play", 0, inplace=True)
  home_b.replace("Did Not Dress", 0, inplace=True)
  home_b.replace("Not With Team", 0, inplace=True)
  home_b.fillna(0, inplace=True)
  home_b['Team'] = np.nan
  
  home_a.drop(home_a[home_a['Starters'] == 'Reserves'].index, inplace=True)
  home_a.replace("Did Not Play", 0, inplace=True)
  home_a.replace("Did Not Dress", 0, inplace=True)
  home_a.replace("Not With Team", 0, inplace=True)
  home_a.fillna(0, inplace=True)
  home_a = home_a[['MP', 'TS%', 'eFG%', '3PAr', 'FTr', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'STL%', 'BLK%', 'TOV%', 'USG%', 'ORtg', 'DRtg']]

  a = away_b.pop('Team')
  a.fillna(aname, inplace=True)
  away_b.insert(1, 'Team', a)
  
  h = home_b.pop('Team')
  h.fillna(hname, inplace=True)
  home_b.insert(1, 'Team', h)
  
  df_a = pd.concat([away_b, away_a], axis=1)
  df_h = pd.concat([home_b, home_a], axis=1)

  df = pd.concat([df_a, df_h], axis=0)
  df.to_csv(f'data/boxscore/{filename}.csv')
  
def split_boxscores(file:str):
  df = pd.read_csv(file)
  filename = file.split('data/boxscore/')[1].replace('.csv', '')
  print(filename)
  
  teaminfo = filename[9:].split('@')
  
  info = {
    'date': filename[:8],
    'home': sanitize_abbr_to_full(teaminfo[1]),
    'away': sanitize_abbr_to_full(teaminfo[0]),
    'home_abbr': sanitize_abbr(teaminfo[1]),
    'away_abbr': sanitize_abbr(teaminfo[0]),
  }
  
  home_df = df[df['Team'] == info['home']].drop('Unnamed: 0', axis=1)
  away_df = df[df['Team'] == info['away']].drop('Unnamed: 0', axis=1)
  home_df['Date'] = np.nan
  away_df['Date'] = np.nan
  home_df.fillna(info['date'], inplace=True)
  away_df.fillna(info['date'], inplace=True)

  home_filepath = f'data/boxscore_team/{info["home_abbr"]}.csv'
  away_filepath = f'data/boxscore_team/{info["away_abbr"]}.csv'
  
  if os.path.isfile(home_filepath):
    legacy = pd.read_csv(home_filepath, index_col=0)
    legacy = pd.concat([legacy, home_df], axis=0, ignore_index=True)
    legacy.to_csv(home_filepath)
  else:
    home_df.to_csv(home_filepath)     
  if os.path.isfile(away_filepath):
    legacy = pd.read_csv(away_filepath, index_col=0)
    legacy = pd.concat([legacy, away_df], axis=0, ignore_index=True)
    legacy.to_csv(away_filepath)
  else:
    away_df.to_csv(away_filepath) 
  
def get_correlation(file, away, home):
  df = pd.read_csv(file)
  df = df[df['Team'] == away]
  df = df[['Starters', 'Team', 'PTS']]
  df = df[df['Starters'] != 'Team Totals']
  df['PTS'] = df['PTS'].astype(int)
  df = df.rename(columns={'Starters':'Name', 'PTS':'Points'})
  df = df.reset_index(drop=True)
  df = df.pivot(index='Team', 
                columns='Name',
                values='Points')
  corr = df.corr()
  
def mean_playerpoints(file):
  print(file)
  df = pd.read_csv(file, index_col=0)
  team = file.split('data/boxscore_team/')[1].replace('.csv', '')
  df = df[df['Starters'] != 'Team Totals']
  df = df[['Starters', 'MP', 'PTS', 'Date']]
  df = df.sort_values(by='MP', ascending=False).groupby('Starters').head(10)
  df['PTS'] = df['PTS'].astype(int)
  print(df)
  df = df.pivot(index='Date',
                columns='Starters',
                values='PTS').fillna(0)
  corr = df.corr()
  corr.to_csv(f'data/correlation/{team}_B5.csv')
  
def save_heatmap(file):
  corr = pd.read_csv(file, index_col=0) 
  team = file.split('data/correlation/')[1].replace('.csv', '')
  f, ax = plt.subplots(figsize=(50, 50))
  sns.heatmap(corr, mask=np.zeros_like(corr, dtype=bool), cmap=sns.diverging_palette(220, 10, as_cmap=True), square=True, ax=ax, annot=True)
  plt.savefig(fname=f'data/imgs/{team}_B5.png')
  plt.close()
  
if __name__ == '__main__':
  # urls = pd.read_csv('boxscoreurl.csv')
  # for row in urls.itertuples():
  #   get_boxscore(row.url)
  
  # for filename in os.listdir('data/boxscore'):
  #   split_boxscores('data/boxscore/' + filename)
  
  for team in tqdm(teams):
    mean_playerpoints(f'data/boxscore_team/{team}.csv')
    save_heatmap(f'data/correlation/{team}.csv')
  
  print(':>')