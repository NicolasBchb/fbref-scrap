# %%
import pandas as pd
import dtale
import fbref_scrap as fb

# %%
ligue1 = fb.League("13", 2023)

# %%
ligue1.scrap_teams()

# %%
ligue1.scrap_players()

# %%
df = ligue1.teams["stats"].copy()
for stat in ["shooting", "passing", "defense", "passing_types", "possession"]:
    df = df.merge(ligue1.teams[stat], on="Équipe", suffixes=("", stat))

dtale.show(df)

# %%
df.to_csv("ligue1.csv", index=False)

# %%
import plotly.express as px

df["%passes réussies"] = (df["Résultats Cmp"] / df["Att"]) *100

df["Passes tentées"] = df["Att"]

# z = "Par 90 minutes PD"
y = "Standard Buts"
x = "Attendu xG"

shoot = px.scatter(
    df,
    x=x,
    y=y,
    # z=z,
    color="Attendu npxG/Sh",
    text="Équipe",
    template="plotly_dark",
)

shoot.update_traces(textposition="top center")
shoot.update_layout(
    title=f"{x} vs {y}",
    xaxis_title=x,
    yaxis_title=y,
)

# add line at meanx for each axis
shoot.add_shape(
    type="line",
    x0=df[x].mean(),
    y0=df[y].min(),
    x1=df[x].mean(),
    y1=df[y].max(),
    line=dict(color="Seagreen", width=2, dash="dash"),
)

# add line at meany for each axis
shoot.add_shape(
    type="line",
    x0=df[x].min(),
    y0=df[y].median(),
    x1=df[x].max(),
    y1=df[y].median(),
    line=dict(color="Seagreen", width=2, dash="dash"),
)



# square height and width
shoot.update_layout(
    autosize=False,
    width=800,
    height=800,
)


shoot.show()
shoot.write_html("xg_2d.html")
# %%
