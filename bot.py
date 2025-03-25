import asyncio
import datetime
from discord.ext import commands
from dotenv import load_dotenv
import discord
import os
import json

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
next_post_time = None

TOKEN = os.getenv('TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
class ChannelAnalyzer:
    def __init__(self, bot):
        self.bot = bot
        self.channel_messages_file = "channel_messages.json"
        self.last_post_file = "last_post.json"

    async def update_channel_messages(self, channel):
        try:
            # Fetch all messages from the channel
            print("Fetching messages from channel history")
            messages = []
            async for message in channel.history(limit=None):
                message_data = {
                    "author": str(message.author),
                    "content": message.content,
                    "timestamp": message.created_at.isoformat(),
                    "channel_id": str(channel.id)  # Channel ID
                }
                messages.append(message_data)
            
            with open(self.channel_messages_file, "w") as f:
                json.dump(messages, f, indent=4)
            print("Updated channel_messages.json with new messages.")

        except Exception as e:
            print(f"Error updatiung channel messages: {e}")
    
    async def save_last_post_content(self, channel):
        try:
            # Fetch the most recent message from the channel
            async for message in channel.history(limit=1):
                last_post_content = {
                    "content": message.content # Only save the content of the last message
                }

            try:
                with open(self.last_post_file, "w")as f:
                    json.dump(last_post_content, f, indent=4)
                print("last post content saved to last_post.json.")
            except Exception as e:
                print(f"Error saving last post content: {e}")
        except Exception as e:
            print(f"Error fetching last post content: {e}")
ca = ChannelAnalyzer(bot)
class CooldownManager:
    def __init__(self):
        self.next_post_time=None
        self.lock = asyncio.Lock()
    async def set_cooldown(self, channel):
        async with self.lock:
            last_message = await self.get_bot_last_message()
            if last_message:
                last_message_time = last_message["timestamp"]
                last_message_time = datetime.datetime.strptime(last_message_time, '%Y-%m-%dT%H:%M:%S.%f%z')
                self.next_post_time = last_message_time + datetime.timedelta(hours=6)
                print(f"Printing next message at {self.next_post_time}")

    async def can_post(self, current_time):
        async with self.lock:
            if current_time > self.next_post_time:
                return True
            else:
                print("Current time is less than next_post_time")
                return False
    async def get_bot_last_message(self):
        try:
            with open("channel_messages.json", "r") as f:
                channelMessages = json.load(f)
            for message in channelMessages:
                if message["author"] == "Counter#9958":
                    return message
        except (discord.DiscordException, FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error fetching messages: {e}")
        return None
    
    async def try_posting(self, channel):
        current_time = datetime.datetime.now(datetime.timezone.utc)
        if await self.can_post(current_time):
            await self.post(channel)
            await self.set_cooldown(channel)

    async def post(self, channel):
        try:
            with open("last_post.json", "r") as f:
                last_post = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading last_post.json: {e}")
            return
        
        if channel:
            new_number = int(last_post["content"]) + 1
            print(f"Posting new number:", {new_number})
            try:
                await channel.send(new_number)
                print(f"Message sent: {new_number}\nPost successfull")
            except Exception as e:
                print(f"Error sending message: {e}")
        else:
            print("Channel not found")
            

cm = CooldownManager()
async def monitor_channel(channel):
    while True:
        try:
            await ca.update_channel_messages(channel)
            await ca.save_last_post_content(channel)
            await cm.set_cooldown(channel)
        except Exception as e:
            print(f"Error: {e}")
            break
        try:
            await cm.try_posting(channel)
        except Exception as e:
            print(f"Error in posting loop: {e}")
        await asyncio.sleep(600)
    return

async def load_cogs(bot):
    """Load all cogs from the cogs directory"""
    cogs = [
        "cogs.joke",
        "cogs.graph",
        "cogs.YtManager",
        "cogs.statistics"
    ]

    successes = 0
    failures = 0

    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"Successfully loaded cog: {cog}")
            successes += 1
        except Exception as e:
            print(f"Failed to load cog {cog}: {e}")
            failures += 1
    print(f"\nCog loading summary: {successes} succeeded, {failures} failed")
@bot.command(name="ping")
async def ping(ctx):
    """Check the bot's latency"""
    latency = round(bot.latency * 1000) # in ms
    await ctx.send(f"Pong! latency: {latency}ms")
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    await load_cogs(bot)
    channel = bot.get_channel(int(CHANNEL_ID)) # Convert to integer
    if not channel:
        print(f"Error: Could not find channel with ID {CHANNEL_ID}")
        return
    bot.loop.create_task(monitor_channel(channel))


bot.run(TOKEN)