import json
import requests
from bs4 import BeautifulSoup

html_comps = requests.get("https://fbref.com/fr/comps/")

soup = BeautifulSoup(html_comps.text, "html.parser")

# tbody -> tr -> th (data-stat="league_name") -> a -> content & href -> .split("/")[2] ("/fr/comps/12/historique/Saisons-La-Liga")

ids = {}

for tbody in soup.find_all("tbody"):
	for tr in tbody.find_all("tr"):
		th = tr.find("th")
		a = th.find("a")
		content = a.getText()
		href = a['href']
		num = href.split("/")[3]
		ids[content] = str(num)

with open("ids.json", 'w') as f:
	json.dump(ids, f)