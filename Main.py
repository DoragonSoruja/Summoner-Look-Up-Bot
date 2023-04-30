import random
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
    await ctx.send("**!help** - Brings up the help menu full of all the commands\n\n**!eightball** - A simple eightball command that gives back several different answer\n`Alias: 8ball`\n\n**!lolProfile <Summoner Name>** - Uses the Riot API to get the level and rank\n`Alias: lol`\n\nMore commands might be added soon. If you have any ideas, please suggest them to the bot creator.")

@bot.command(aliases=['lol'])
async def lolProfile(ctx, summonerName = None):
    if summonerName == None:
        await ctx.send("Please enter a Summoner Name.")

    api = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={api_key}')
    info = api.text
    summonerInfo = json.loads(info)

    try:
        second_api = requests.get(f"https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerInfo['id']}?api_key={api_key}")
        second_info = second_api.text
        summonerInfoByID = json.loads(second_info)
    except:
        await ctx.send("Please enter in a valid summoner name.")

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

@bot.command()
async def lastMatch(ctx, summonerName = None):
    if summonerName == None:
        await ctx.send("Please enter a Summoner Name.")

    api = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={api_key}')
    info = api.text
    summonerInfo = json.loads(info)

    second_api = requests.get(f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{summonerInfo['puuid']}/ids?start=0&count=20&api_key={api_key}")
    second_info = second_api.text
    matchRecords = json.loads(second_info)

    third_api = requests.get(f'https://americas.api.riotgames.com/lol/match/v5/matches/{matchRecords[0]}?api_key={api_key}')
    third_info = third_api.text
    latestMatch = json.loads(third_info)

    allPlayers = latestMatch['info']['participants']

    targetedPlayer = None

    for playerInfo in allPlayers:
        if playerInfo['summonerName'].lower() == summonerName.lower():
            targetedPlayer = playerInfo

    # Implement the rest of the command

    await ctx.send(targetedPlayer['championName'])

bot.run(Discord_Token)