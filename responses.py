import random
import requests
from dotenv import load_dotenv
import os

load_dotenv()
API_Key = os.getenv("RIOT_Key")


def get_response(message: str) -> str:
    p_message = message.lower()

    if p_message == "hello":
        return 'Hey there!'

    if p_message == "roll":
        return str(random.randint(1, 6))

    if p_message == "api":
        response = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/DoragonSoruja?api_key={API_Key}")
        playerInfo = response.json()
        return playerInfo['name'] + " is Level " + str(playerInfo['summonerLevel'])

    if p_message == "help":
        return '`This is a help message that can be modified.`'

    return "I didn't understand what you wrote. Try typing `!help`"