# bot.py
import os
import discord
import datetime
from dotenv import load_dotenv
from discord.ext import commands
from discord.ext import tasks
from discord import Member

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()
intents = discord.Intents().all()
bot = commands.Bot(command_prefix='!', intents=intents)

global babies
babies = []

@bot.event
async def on_ready():
    await babysitLoop.start()

@bot.command()
async def babysit(ctx, member: discord.Member):
    global babies
    babies.append(str(member))

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

@tasks.loop(seconds=1)
async def babysitLoop():
    global babies
    for guild in bot.guilds:
        if guild.id == int(GUILD):
            for member in guild.members:

                # Start and end time that babysitting should occur
                # Current time for comparison
                start = datetime.time(12, 0, 0)
                end = datetime.time(14, 0, 0)
                now = datetime.datetime.now().time()

                # Find the baby that needs to go to bed
                # TODO: start task from command and pass desired member to babysit from there
                if (str(member) in babies) and (member.voice is not None) and (time_in_range(start, end, now)):
                    
                    # Server deafen the member
                    await member.edit(mute=True)
                    await member.edit(deafen=True)

                    # Disconnect the user from any voice channel they're connected to
                    await member.move_to(channel=None, reason=None)
                
                # Wake up the baby
                elif not time_in_range(start, end, now) and (member.voice is not None):
                    if member.voice.mute:
                        await member.edit(mute=False)
                    if member.voice.deaf:
                        await member.edit(deafen=False)

bot.run(TOKEN)
