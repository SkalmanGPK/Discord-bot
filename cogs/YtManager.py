import json
import discord
from discord.ext import commands
import aiohttp
import os
import random
from typing import Dict, List
from pathlib import Path
#constants
DATA_DIR = Path(__file__).parent.parent
os.makedirs(DATA_DIR, exist_ok=True)
CHANNEL_CONFIG={
    'ddoi': {
        'id': 'UCdC0An4ZPNr_YiFiYoVbwaw',
        'file': 'ddoi_videos.json',
        'api_url': 'https://www.googleapis.com/youtube/v3/search'
    },
    'pewdiepie': {
        'id': 'UC-lHJZR3Gqxm24_Vd_AJ5Yw',
        'file': 'pewdiepie_videos.json',
        'api_url': 'https://www.googleapis.com/youtube/v3/search'
    }
}

class YoutubeCog(commands.Cog):
    """Discord cog for youtube video lookup and caching"""

    def __init__(self, bot, api_key):
        self.bot = bot
        self.api_key = api_key
        self.bot_dir = Path(__file__).parent.parent
        self.cache_file = self.bot_dir / "youtube_cache.json"
        self.ddoi_file = self.bot_dir / "ddoi_videos.json"
        self.pewdiepie_file = self.bot_dir / "pewdiepie_videos.json"
        self.video_cache = self.load_cache()
        self.videos = {
            'ddoi':self.load_channel_videos('ddoi'),
            'pewdiepie': self.load_channel_videos('pewdiepie')
        }

    def load_cache(self) -> Dict:
        try:
            with open(self.cache_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def save_cache(self):
        with open(self.cache_file, "w") as f:
            json.dump(self.video_cache, f, indent=4)

    def load_channel_videos(self, file_path):
        try:
            with open(file_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_channel_videos(self, channel: str):
        file_path = self.ddoi_file if channel == 'ddoi' else self.pewdiepie_file
        with open(file_path, "w") as f:
            json.dump(self.videos[channel], f, indent=4)

    def get_random_video(self, channel: str) -> str:
        if not self.videos[channel]:
            return None
        return random.choice(self.videos[channel])
    
    async def fetch_videos(self, channel: str) -> bool:
        """Fetch lastest videos from youtube channel"""
        channel_id = CHANNEL_CONFIG[channel]['id']
        url = f"{CHANNEL_CONFIG[channel]['api_url']}?channelId={channel_id}&key={self.api_key}&part=snippet,id&order=date&maxResults=50"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self.videos[channel] = [item['id']['videoId'] for item in data.get('items', []) if item['id'].get('videoId')]
                        self.save_channel_videos(channel)
                        return True
                    return False
        except Exception:
            return False
    @commands.command(name="ytvideo")
    async def fetch_video_info(self, ctx, video_id: str):
        """Get information about a Youtube video.
           Usage: !ytvideo <video_id>        
        """
        video_data = await self.fetch_video_data(video_id, ctx)
        if video_data:
            embed = discord.Embed(
                title=video_data.get('title', 'Unknown title'),
                description=video_data.get('description', 'No description'),
                url=f"https://youtu.be/{video_id}"
            )
            if 'thumbnails' in video_data:
                embed.set_thumbnail(url=video_data['thumbnails']['default']['url'])
            await ctx.send(embed=embed)
    async def fetch_video_data(self, video_id, ctx):
        """Fetch video data from youtube API or cache."""
        #check cache first
        if video_id in self.video_cache:
            return self.video_cache[video_id]
        url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet&key={self.api_key}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data["items"]:
                        self.video_cache[video_id] = data["items"][0]["snippet"]
                        self.save_cache()
                        return self.video_cache[video_id]
                await ctx.send(f"Failed to fetch video data for {video_id}: HTTP {resp.status}")
                return None
    @commands.command(name="pewdiepie")
    async def pewdiepie_video(self, ctx):
        """Get a random PewDiePie video (playable in Discord)"""
        if not self.videos['pewdiepie']:
            msg = await ctx.send("Loading videos...")
            if await self.fetch_videos('pewdiepie'):
                await msg.delete()
            else:
                await msg.edit(content="Failed to load videos")
                return
        
        if video_id := self.get_random_video('pewdiepie'):
            media_link = f"https://www.youtube.com/watch?v={video_id}"
            await ctx.send(media_link)
        else:
            await ctx.send("No videos available")

    @commands.command(name="ddoi")
    async def daily_dose(self, ctx):
        """Get a random Daily Dose of Internet video (playable in Discord)"""
        if not self.videos['ddoi']:
            msg = await ctx.send("Loading DDOI videos...")
            if await self.fetch_videos('ddoi'):
                await msg.delete()
            else:
                await msg.edit(content="Failed to load DDOI videos")
                return
        
        if video_id := self.get_random_video('ddoi'):
            # Format for Discord's media player
            media_link = f"https://www.youtube.com/watch?v={video_id}"

            await ctx.send(media_link)  # This enables in-Discord playback
        else:
            await ctx.send("No DDOI videos available")
            
async def setup(bot):
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        raise ValueError("Youtube API key not configured")
    await bot.add_cog(YoutubeCog(bot, api_key))