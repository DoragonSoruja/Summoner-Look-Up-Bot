import requests
import json

def GetLatestVersion():
    response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")

    data = response.text

    game_versions = json.loads(data)

    return game_versions[0]