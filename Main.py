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

@bot.command(aliases=['8ball', 'test'])
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
async def embed(ctx, member:discord.Member = None):
    if member == None:
        member = ctx.author

    name = member.display_name
    pfp = member.display_avatar

    embed = discord.Embed(title="This is my Embed", description="This is a test embed, I'm gonna change the information later", color=discord.Color.random())
    embed.set_author(name=f"{name}")
    embed.set_thumbnail(url=f"{pfp}")
    embed.add_field(name="This is 1 field", value="This field is just a value")
    embed.add_field(name="This is 2 field", value="This field is inline True", inline=True)
    embed.add_field(name="This is 3 field", value="This field is inline False", inline=False)
    embed.set_footer(text=f"{name} made this Embed")

    await ctx.send(embed=embed)

@bot.command(aliases=['lol'])
async def lolProfile(ctx, summonerName = None):
    if summonerName == None:
        await ctx.send("Please enter a Summoner Name.")

    api = requests.get(f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summonerName}?api_key={api_key}')
    info = api.text
    summonerInfo = json.loads(info)

    second_api = requests.get(f"https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerInfo['id']}?api_key={api_key}")
    second_info = second_api.text
    summonerInfoByID = json.loads(second_info)

    embed = discord.Embed(title=summonerInfo['name'], description="A simple League of Legends profile", color=discord.Color.random())
    embed.set_thumbnail(url=f"https://ddragon.leagueoflegends.com/cdn/{GetLatestVersion()}/img/profileicon/{summonerInfo['profileIconId']}.png")
    embed.add_field(name="__Level__", value=summonerInfo['summonerLevel'], inline=True)
    embed.add_field(name="__Rank__", value=f"{summonerInfoByID[0]['tier']} {summonerInfoByID[0]['rank']}", inline="true")
    embed.set_footer(text=f"{ctx.author} has requested this information")

    await ctx.send(embed=embed)

bot.run(Discord_Token)