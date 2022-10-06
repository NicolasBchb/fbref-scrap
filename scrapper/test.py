# %%
import json
import dtale
import requests
import pandas as pd
from tqdm import tqdm
import plotly.express as px
from bs4 import BeautifulSoup


# %%
def clean(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [f"{a} {b}" if "level" not in a else f"{b}" for a, b in df.columns]	
    df.fillna(0, inplace=True)
    return df


# %%
class Match:
	def __init__(self, id, year):
		self.season = f"{year-1}-{year}"
		self.id = id
		self.stats = {}
		self.stats_type = [
			"stats",
			"keepers",
			"keepersadv",
			"shooting",
			"passing",
			"passing_types",
			"gca",
			"defense",
			"possession",
			"playingtime",
			"misc"
		]
		html_comps = requests.get(f"https://fbref.com/fr/equipes/{self.id}/{self.season}/all_comps/")
		soup = BeautifulSoup(html_comps.text, "html.parser")
		mydivs = soup.find_all("div", {"class": "filter"})
		self.comps = [a.getText() for a in mydivs[0].find_all("a")]
		if 'Toutes les compétitions' not in self.comps:
			self.comps = [soup.find_all("h2")[0].getText().split(":")[-1][1:]]
		for comp in self.comps:
			self.stats[comp] = {}
		self.players = {
			a[0]: a[1].split("/")[-2]
			for a in clean(
				pd.read_html(
					f"https://fbref.com/fr/equipes/{self.id}/{self.season}/all_comps/",
					extract_links="body"
				)[0])["Joueur"].to_list()}

	def scrap_data(self):
		dfs = pd.read_html(f"https://fbref.com/fr/equipes/{self.id}/{self.season}/all_comps/")
		self.schedule = dfs[len(self.comps)]
		del(dfs[len(self.comps)])
		for i, stat in enumerate(self.stats_type):
			for j, comp in enumerate(self.comps):
				self.stats[comp][stat] = clean(dfs[i*len(self.comps) + j])