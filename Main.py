import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

Discord_Token = os.getenv("Discord_Token")

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


bot.run(Discord_Token)