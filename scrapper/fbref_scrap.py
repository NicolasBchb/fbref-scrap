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
        df.columns = [
            f"{a} {b}" if "level" not in a else f"{b}" for a, b in df.columns]
    df.fillna(0, inplace=True)
    return df


def merge(dict_df, on):
	
	for i, key in enumerate(dict_df):
		if i == 0:
			df = dict_df[key]
			df.columns = [f"{col} {key.upper()}" if col != on else on for col in df.columns]
		else:
			df = df.merge(dict_df[key], on=on, how="outer", suffixes=('', f' {key.upper()}'))
	return df


# %%
# TODO: choix de la langue
# TODO: quid ligues avec peu de datas ?
# TODO: travailler les classes pour optimiser leurs intéractions (for, attributs...)

class League:
    def __init__(self, id, year):
        """
        This function takes a string as an argument and generate a dictionary of the string as a key and the
        value as the corresponding ID for the league.

        "stats":          Statistiques basiques
        "keepers":        Gardien de but
        "keepersadv":     Stats de gardiens de but avancées
        "shooting":       Tirs
        "passing":        Passes
        "passing_types":  Types de passe
        "gca":            Préparation des tirs et des buts
        "defense":        Actions défensives
        "possession":     Possession
        "playingtime":    Temps de jeu
        "misc":           Statistiques diverses

        Args:
          champ: The name of the league you want to get data from.
        """
        self.season = f"{year-1}-{year}"
        self.id = id
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
        self.schedule = pd.read_html(
            f"https://fbref.com/fr/comps/{self.id}/{self.season}/calendrier/")[0].drop_duplicates(keep=False)

    def scrap_teams(self):
        self.teams = {}
        self.teams_against = {}
        dfs = pd.read_html(
            f"https://fbref.com/fr/comps/{self.id}/{self.season}/",
            skiprows=range(27, 10**6, 26),
        )
        self.teams["ranking"] = dfs[0].fillna(0)
        self.teams["home_away"] = clean(dfs[1].fillna(0))

        # for (i, stat), (j, bis) in itertools.product(enumerate(self.stats_type), enumerate(["", "_contre"])):
        for i, stat in enumerate(self.stats_type):
            for j in range(2):
                if j == 0:
                    self.teams[stat] = clean(dfs[2 + i*2 + j])
                else:
                    self.teams_against[stat] = clean(dfs[2 + i*2 + j])

        self.teams_complete = merge(self.teams, "Équipe")
        self.teams_against_complete = merge(self.teams_against, "Équipe")

    def scrap_players(self):
        self.players = {}
        for stat in tqdm(self.stats_type):
            html = requests.get(
                f"https://fbref.com/fr/comps/{self.id}/{self.season}/{stat}/")
            df = pd.read_html(
                html.text.replace("<!--", "").replace("-->", ""),
                skiprows=range(27, 10**6, 26)
            )[2]
            self.players[stat] = clean(df)

        self.players_complete = merge(self.players, "Joueur")


# %%
# !

class Cup:
    def __init__(self):
        False


# %%
class Big5:
    def __init__(self, year):
        """
        This function takes a string as an argument and generate a dictionary of the string as a key and the
        value as the corresponding ID for the league.

        "stats":          Statistiques basiques
        "keepers":        Gardien de but
        "keepersadv":     Stats de gardiens de but avancées
        "shooting":       Tirs
        "passing":        Passes
        "passing_types":  Types de passe
        "gca":            Préparation des tirs et des buts
        "defense":        Actions défensives
        "possession":     Possession
        "playingtime":    Temps de jeu
        "misc":           Statistiques diverses

        Args:
          champ: The name of the league you want to get data from.
        """
        self.season = f"{year-1}-{year}"
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

    def scrap_teams(self):
        self.teams = {}
        self.teams_against = {}
        self.teams["ranking"] = pd.read_html(
            f"https://fbref.com/fr/comps/Big5/{self.season}/Statistiques-Les-5-grands-championnats-europeens",
            skiprows=range(37, 10**6, 36),
        )[0].fillna(0)

        for i, stat in enumerate(self.stats_type):
            dfs = pd.read_html(
                f"https://fbref.com/fr/comps/Big5/{self.season}/{stat}/equipes/Statistiques-Les-5-grands-championnats-europeens",
                # skiprows=range(27, 10**6, 26),
            )
            for j in range(2):
                if j == 0:
                    self.teams[stat] = clean(dfs[i*2 + j])
                else:
                    self.teams_against[stat] = clean(dfs[i*2 + j])

        self.teams_complete = merge(self.teams, "Équipe")
        self.teams_against_complete = merge(self.teams_against, "Équipe")

    def scrap_players(self):
        self.players = {}
        for stat in tqdm(self.stats_type):
            df = pd.read_html(
                f"https://fbref.com/fr/comps/Big5/{self.season}/{stat}/joueurs/Statistiques-Les-5-grands-championnats-europeens",
                skiprows=range(27, 10**6, 26),
            )[0]
            self.players[stat] = clean(df)

        self.players_complete = merge(self.players, "Joueur")


# %%
# TODO: système ids
# TODO: scope competition (all_comps)

class Club:
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
        html_comps = requests.get(
            f"https://fbref.com/fr/equipes/{self.id}/{self.season}/all_comps/")
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
        dfs = pd.read_html(
            f"https://fbref.com/fr/equipes/{self.id}/{self.season}/all_comps/")
        self.schedule = dfs[len(self.comps)]
        del (dfs[len(self.comps)])
        for i, stat in enumerate(self.stats_type):
            for j, comp in enumerate(self.comps):
                self.stats[comp][stat] = clean(dfs[i*len(self.comps) + j])


# %%
# !

class Nation:
    def __init__(self):
        pass


# %%
class Player:
    def __init__(self):
        True


# %%
class Match:
    def __init__(self):
        True


# %%
