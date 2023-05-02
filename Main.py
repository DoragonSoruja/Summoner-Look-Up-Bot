import random
import math
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

@bot.event
async def on_member_join(member):
    channel = member.guild.system_channel
    await channel.send(f"{member.mention} Welcome to the server")

@bot.event
async def on_member_remove(member):
    channel = member.guild.system_channel
    await channel.send(f"Goodbye! {member.mention}")

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
    await ctx.send("**!help** - Brings up the help menu full of all the commands\n\n**!eightball** - A simple eightball command that gives back several different answer\n`Alias: 8ball`\n\n**!lolProfile <Summoner Name>** - Uses the Riot API to get the level and rank\n`Alias: lol`\n\n**!lastMatch <Summoner Name>** - Gives you stats on the last match played.\n`Alias: last`\n\nMore commands might be added soon. If you have any ideas, please suggest them to the bot creator.")

@bot.command(aliases=['lol'])
async def lolProfile(ctx, summonerName = None):
    if summonerName == None:
        await ctx.send("Please enter a Summoner Name.")
        return

    api = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={api_key}')
    info = api.text
    summonerInfo = json.loads(info)

    try:
        second_api = requests.get(f"https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerInfo['id']}?api_key={api_key}")
        second_info = second_api.text
        summonerInfoByID = json.loads(second_info)
    except:
        await ctx.send('Please enter in a valid summoner name.\n(If you summoner name contains a space, put it in double quotation marks `"Summoner Name"`)')
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

    api = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={api_key}')
    info = api.text
    summonerInfo = json.loads(info)

    try:
        second_api = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{summonerInfo['puuid']}/ids?start=0&count=20&api_key={api_key}")
        second_info = second_api.text
        matchRecords = json.loads(second_info)
    except:
        await ctx.send('Please enter in a valid summoner name.\n(If you summoner name contains a space, put it in double quotation marks `"Summoner Name"`)')
        return

    third_api = requests.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/{matchRecords[0]}?api_key={api_key}')
    third_info = third_api.text
    latestMatch = json.loads(third_info)

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

bot.run(Discord_Token)