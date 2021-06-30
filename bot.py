#!/usr/bin/env python3
import os
import discord
import datetime
import re
from os.path import join, dirname
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
from discord import Member

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

babiesList = []

bedtimeMap = {

    "start": datetime.time(1, 0, 0),
    "end"  : datetime.time(12, 0, 0)
}

@bot.event
async def on_ready():
    await babysitLoop.start()

@bot.command()
@commands.has_role('Babysitter')
async def babysit(ctx, member: discord.Member):
    babiesList.append(str(member))

@bot.command()
@commands.has_role('Babysitter')
async def daddyshome(ctx, member: discord.Member):
    babiesList.remove(str(member))

@bot.command()
async def bedtime(ctx, start=None, end=None):

    # Check if start and end time were provided
    if start is not None and end is not None:

        # Regex to determine if bedtime was provided in correct format
        regex = re.search('^(2[0-3]|1[0-9]|[0-9]|[^0-9][0-9]):([0-5][0-9]|[0-9])$', start)
        if regex is not None:
            start += ":00" # Needed for strptime() function
            regex = re.search('^(2[0-3]|1[0-9]|[0-9]|[^0-9][0-9]):([0-5][0-9]|[0-9])$', end)

        if regex is not None:
            end += ":00"

            # Check the format of the start and end time
            startTime = datetime.datetime.strptime(start,"%H:%M:%S").time()
            endTime = datetime.datetime.strptime(end,"%H:%M:%S").time()
            bedtimeMap["start"] = startTime
            bedtimeMap["end"]   = endTime

    # Send message with bedtime (doesn't update if format was provided incorrectly)
    message = "Bedtime starts at " + str(bedtimeMap["start"]) + " and ends at " + str(bedtimeMap["end"])
    await ctx.send(message)

@bot.command()
async def babies(ctx):
    message = "Current babies:\n"
    if len(babiesList) == 0:
        message += "No babies"
    else:
        for baby in babiesList:
            message = message + baby + '\n'
    await ctx.send(message)

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

@tasks.loop(seconds=1)
async def babysitLoop():
    for guild in bot.guilds:
        if guild.id == int(GUILD):
            for member in guild.members:

                # Start and end time that babysitting should occur
                # Current time for comparison
                start = datetime.time(12, 0, 0)
                end = datetime.time(14, 0, 0)
                now = datetime.datetime.now().time()

                # Find the baby that needs to go to bed
                if ((str(member) in babiesList) and (member.voice is not None) and (time_in_range(bedtimeMap["start"], bedtimeMap["end"], now))):
                    
                    # Server deafen the member
                    await member.edit(mute=True)
                    await member.edit(deafen=True)

                    # Disconnect the user from any voice channel they're connected to
                    await member.move_to(channel=None, reason=None)
                
                # Wake up the baby
                elif ((str(member) in babiesList) and (not time_in_range(bedtimeMap["start"], bedtimeMap["end"], now)) and (member.voice is not None)):
                    if member.voice.mute:
                        await member.edit(mute=False)
                    if member.voice.deaf:
                        await member.edit(deafen=False)

bot.run(TOKEN)
