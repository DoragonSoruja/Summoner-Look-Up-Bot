import random
from datetime import datetime
import discord
from version import GetLatestVersion
from discord.ext import commands
from dotenv import load_dotenv
import os
import requests
import json


load_dotenv()

Discord_Token = os.getenv("Discord_Token")
api_key = os.getenv("Riot_Key")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot.remove_command('help')

@bot.event
async def on_ready():
    print(f"{bot.user} Is Online")

@bot.command()
async def ping(ctx):
    await ctx.reply(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command(aliases=['8ball'])
async def eightball(ctx, *, question = None):
    if question == None:
        await ctx.send("Please put in a question.")
        return

    responses = ["As I see it, yes.", "Ask again later.", "Better not tell you now.", "Can't predict now.", "Concentrate and ask again.",
                 "Don't count on it.", "It is certain.", "It is decidedly so.", "Most likely.", "My reply is no.", "My sources say no.",
                 "Outlook not so good.", "Outlook good.", "Reply hazy, try again.", "Signs point to yes.", "Very doubtful.", "Without a doubt.",
                 "Yes.", "Yes - definitely.", "You may rely on it."]
    await ctx.send(f"**Question: **{question}\n**Answer:** {random.choice(responses)}")

@bot.command()
async def help(ctx):
    await ctx.send("**!help** - Brings up the help menu with all the commands\n\n**!eightball** - A simple eightball command that gives back several different answer\n`Alias: 8ball`\n\n**!lolProfile <Summoner Name>** - Uses the Riot API to get the level and rank\n`Alias: lol`\n\n**!lastMatch <Summoner Name>** - Gives you stats on the last match played.\n`Alias: last`\n\n**!mastery <Summoner Name>** - Gives back a list of a summoner's top five champions played organized by mastery points.\n`Alias: top5`\n\nMore commands might be added soon. If you have any ideas, please suggest them to the bot creator.")

@bot.command(aliases=['lol'])
async def lolProfile(ctx, summonerName = None):
    if summonerName == None:
        await ctx.send("Please enter a Summoner Name.")
        return

    summonerapi = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={api_key}')
    info = summonerapi.text
    summonerInfo = json.loads(info)

    try:
        summonerstatsapi = requests.get(f"https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerInfo['id']}?api_key={api_key}")
        info = summonerstatsapi.text
        summonerInfoByID = json.loads(info)
    except:
        await ctx.send('Please enter in a valid summoner name.\n(If your summoner name contains a space, put it in double quotation marks `"Summoner Name"`)')
        return

    embed = discord.Embed(title=summonerInfo['name'], description=f"The League profile of {summonerInfo['name']}", color=discord.Color.random())
    embed.set_thumbnail(url=f"https://ddragon.leagueoflegends.com/cdn/{GetLatestVersion()}/img/profileicon/{summonerInfo['profileIconId']}.png")
    embed.add_field(name="__Level__", value=summonerInfo['summonerLevel'], inline=False)

    try:
        embed.add_field(name="__Solo Rank__", value=f"{summonerInfoByID[0]['tier']} {summonerInfoByID[0]['rank']}", inline=True)
    except:
        embed.add_field(name="__Solo Rank__", value="Unranked", inline=True)

    try:
        embed.add_field(name="__Flex Rank__", value=f"{summonerInfoByID[1]['tier']} {summonerInfoByID[1]['rank']}", inline=True)
    except:
        embed.add_field(name="__Flex Rank__", value="Unranked", inline=True)

    embed.set_footer(text=f"{ctx.author} has requested this information")

    await ctx.send(embed=embed)

@bot.command(aliases=['last', 'lastlol'])
async def lastMatch(ctx, summonerName = None):
    if summonerName == None:
        await ctx.send("Please enter a Summoner Name.")
        return

    summonerapi = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={api_key}')
    info = summonerapi.text
    summonerInfo = json.loads(info)

    try:
        matchesapi = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{summonerInfo['puuid']}/ids?start=0&count=20&api_key={api_key}")
        info = matchesapi.text
        matchesinfo = json.loads(info)
    except:
        await ctx.send('Please enter in a valid summoner name.\n(If your summoner name contains a space, put it in double quotation marks `"Summoner Name"`)')
        return

    matchapi = requests.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/{matchesinfo[0]}?api_key={api_key}')
    matchinfo = matchapi.text
    latestMatch = json.loads(matchinfo)

    allPlayers = latestMatch['info']['participants']

    targetedPlayer = None

    for playerInfo in allPlayers:
        if playerInfo['summonerName'].lower() == summonerName.lower():
            targetedPlayer = playerInfo

    datetime_Start = datetime.fromtimestamp(latestMatch['info']['gameCreation'] / 1000)
    date = datetime_Start.strftime("%m/%d")
    timeStart = datetime_Start.strftime("%H:%M")

    datetime_End = datetime.fromtimestamp(latestMatch['info']['gameEndTimestamp'] / 1000)
    timeEnd = datetime_End.strftime("%H:%M")

    match_duration = targetedPlayer['challenges']['gameLength'] / 60

    embedColor = discord.Color.green() if targetedPlayer['win'] else discord.Color.red()
    matchStatus = "Victory" if targetedPlayer['win'] else "Defeat"

    KDA = f"{targetedPlayer['kills']}/{targetedPlayer['deaths']}/{targetedPlayer['assists']}"

    embed = discord.Embed(title="Last Match", description=f"This match happened at {date}", color=embedColor)
    embed.set_thumbnail(url=f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{targetedPlayer['championId']}.png")
    embed.add_field(name="__Champion__", value=f"{targetedPlayer['championName']}", inline=False)
    embed.add_field(name="__Match Duration__", value=f"{round(match_duration)} minutes", inline=True)
    embed.add_field(name="__Time Started__", value=f"{timeStart}", inline=True)
    embed.add_field(name="__Time Ended__", value=f"{timeEnd}", inline=True)
    embed.add_field(name="__KDA__", value=f"{KDA}", inline=True)
    embed.add_field(name="__Damage Dealt__", value=f"{targetedPlayer['totalDamageDealtToChampions']}", inline=True)
    embed.add_field(name="__Match Status__", value=f"{matchStatus}", inline=False)

    await ctx.send(embed=embed)

@bot.command(aliases=['top5'])
async def mastery(ctx, summonerName = None):
    if summonerName == None:
        await ctx.send("Please enter in a summoner name")
        return

    summonerAPI = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={api_key}')
    info = summonerAPI.text
    summonerInfo = json.loads(info)

    try:
        masteryAPI = requests.get(f"https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summonerInfo['id']}?api_key={api_key}")
        info = masteryAPI.text
        masteryInfo = json.loads(info)
    except:
        await ctx.send('Please enter in a valid summoner name.\n(If your summoner name contains a space, put it in double quotation marks `"Summoner Name"`)')
        return

    championAPI = requests.get(f"http://ddragon.leagueoflegends.com/cdn/{GetLatestVersion()}/data/en_US/champion.json")
    data = championAPI.text
    championInfo = json.loads(data)

    embed = discord.Embed(title="Top 5 Mastery", description=f"{summonerName}'s top 5 champions", color=discord.Color.blue())
    embed.set_thumbnail(url=f"https://ddragon.leagueoflegends.com/cdn/{GetLatestVersion()}/img/profileicon/{summonerInfo['profileIconId']}.png")

    for x in range(5):
        for champ in championInfo['data']:
            if championInfo['data'][champ]["key"] == f"{masteryInfo[x]['championId']}":
                 embed.add_field(name="__Champion__", value=champ)

        embed.add_field(name="__Mastery__", value=f"M{masteryInfo[x]['championLevel']} - {masteryInfo[x]['championPoints']}pts")

        date = datetime.fromtimestamp(masteryInfo[x]['lastPlayTime'] / 1000).strftime("%m/%d/%y")

        embed.add_field(name="__Last Played__", value=f"{date}")

    await ctx.send(embed=embed)

bot.run(Discord_Token)