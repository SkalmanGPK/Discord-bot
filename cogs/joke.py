import discord
from discord.ext import commands
import aiohttp
import json


class JokeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.joke_api_url = "https://v2.jokeapi.dev/joke/Any?type=twopart"
    @commands.command(name="joke")
    async def tell_joke(self, ctx):
        """Get a random joke"""
        async with aiohttp.ClientSession() as session:
            async with session.get(self.joke_api_url) as response:
                if response.status == 200:
                    data = await response.json()

                    if data["type"] == "single":
                        joke = data["joke"]
                    else: # Two-part joke
                        joke = f"{data['setup']}\n\n||{data['delivery']}||"
                    await ctx.send(joke)
                else:
                    await ctx.send("Couldn't fetch a joke right now. Try again later!")
async def setup(bot):
    await bot.add_cog(JokeCog(bot))