import discord
import os
from discord.ext import commands

# Load your bot's token from environment variables
TOKEN = os.getenv('TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
    # Fetch the channel using the channel ID
    channel = bot.get_channel(int(CHANNEL_ID))  # Use the correct channel ID
    if channel:
        await channel.send("Hello!")
        print("Hello message sent!")
    else:
        print("Channel not found!")

bot.run(TOKEN)
