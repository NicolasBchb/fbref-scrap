# %%
import fbref_scrap as fb
import pandas as pd
from tqdm import tqdm
import dtale


# %%
ligue1 = fb.League(13, 2023)

ligue1.scrap_teams()

# %%
dtale.show(ligue1.teams_complete)

# %%
ligue1.scrap_players()

# %%
dtale.show(ligue1.players_complete)

# %%
