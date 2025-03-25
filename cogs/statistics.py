import discord
from discord.ext import commands
import json
from collections import Counter
import re

class StatCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="stat")
    async def stat(self, ctx, *, arg):
        """commands that lets users see stats in specific channels"""
        channel = ctx.channel
        if str(arg).lower() == "most used word" or str(arg).lower == "most used words":
            await self.most_used_word(ctx, channel)
        else:
            await ctx.send("Invalid stat type. Currently only 'most used word' is supported.")
    async def most_used_word(self, ctx, channel):
        await ctx.send(f"🔍 Analyzing messages in {channel.mention}... (This may take a while)")

        word_counter = Counter()
        common_words = {"the", "and", "a", "to", "of", "is", "in", "it", "that", "for", "https", "com", "watch", "youtube"}

        try:
            async for message in channel.history(limit=None):
                if not message.content:
                    continue
                
                content_no_urls = re.sub(r'https?://\S+|www\.\S+', '', message.content)
                words = re.findall(r'\b\w+\b', content_no_urls.lower())
                
                # Filter out common words and short words
                filtered_words = [
                    word for word in words
                    if (word not in common_words and
                        len(word) > 2 and
                        not word.isnumeric())
                ]

                word_counter.update(filtered_words)

            if not word_counter:
                return await ctx.send("❌ No valid words found in recent messages.")
            top_words = word_counter.most_common(10)
            # Save results
            data = {
                "channel_id": channel.id,
                "channel_name": channel.name,
                "top_words": [{"word": word, "count": count} for word, count in top_words],
                "analyzed_messages": sum(word_counter.values())
            }

            #save to json
            with open(f"word_stats_{channel.id}.json", "w") as f:
                json.dump(data, f, indent=4)

            # Format the output message
            result_message = f"📊 **Top 10 most used words in #{channel.name}:**\n"
            result_message += "\n".join(
                f"{i+1}. **{word}** - {count} times" 
                for i, (word, count) in enumerate(top_words)
            )
            result_message += f"\n\nTotal messages analyzed: {data['analyzed_messages']}"
            await ctx.send(result_message)

        except Exception as e:
            await ctx.send(f"⚠️ Error: {str(e)}")
            print(f"Error in most_used_word: {e}")
async def setup(bot):
    await bot.add_cog(StatCog(bot))