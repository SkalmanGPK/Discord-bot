import discord
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import datetime
import discord
from discord.ext import commands
class GraphCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.messages = None
        self.analysis_dir = "analysis_results"
    @commands.command(name="graph")
    async def graph(self, ctx, arg: str):
        """Generate message activity graphs
        Usage: !graph activity - shows hourly/daily activity
               !graph toplist - shows top users
        """

        target_channel = ctx.channel
        try:
            with open('channel_messages.json', 'r')as f:
                messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            await ctx.send(f"Error loading message data: {str(e)}")
            return
        df = pd.DataFrame(messages)
        try:
        
        # Convert timestamp to datetime and extract date/hour
            df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')
            df['date'] = df['timestamp'].dt.date
            df['hour'] = df['timestamp'].dt.hour

            today = datetime.datetime.today()
            monthly_folder = today.strftime('%Y-%m')
            os.makedirs(f'analysis_results/{monthly_folder}', exist_ok=True)

            if arg == "activity":
                await self.handle_activity(ctx, df, monthly_folder, today)
            elif arg == "toplist":
                await self.handle_toplist(ctx, df, monthly_folder)
            else:
                await ctx.send("Invalid command. Use '!graph activity' or '!graph toplist'.")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
    async def handle_activity(self, ctx, df, monthly_folder, today):
        # Plot hourly activity
        plt.figure(figsize=(12, 6))
        sns.histplot(df['hour'], bins=24, kde=True)
        plt.title('Message Activity by Hour of Day')
        plt.xlabel('Hour of Day')
        plt.ylabel('Number of Messages')
        plt.xticks(range(0, 24))
        hourly_file = f'analysis_results/{monthly_folder}/hourly_activity_{today.strftime("%Y-%m-%d")}.png'
        plt.savefig(hourly_file)
        plt.close()

            # Plot daily activity
        plt.figure(figsize=(14, 6))
        daily = df.groupby('date').size()
        daily.plot(kind='line', marker='o')
        plt.title('Daily Message Activity')
        plt.xlabel('Date')
        plt.ylabel('Number of Messages')
        plt.grid(True)
        daily_file = f'analysis_results/{monthly_folder}/daily_activity_{today.strftime("%Y-%m-%d")}.png'
        plt.savefig(daily_file)
        plt.close()

        # Send results
        most_active_hour = df['hour'].value_counts().idxmax()
        most_active_day = df['date'].value_counts().idxmax()
        await ctx.send(
            f"Most active hour: {most_active_hour}:00\n"
            f"Most active day: {most_active_day}"
        )
        await ctx.send(file=discord.File(hourly_file))
        await ctx.send(file=discord.File(daily_file))

    async def handle_toplist(self, ctx, df, monthly_folder):
        # Plot user activity
        plt.figure(figsize=(12, 6))
        user_counts = df['author'].value_counts().head(10)
        sns.barplot(x=user_counts.values, y=user_counts.index, 
                hue=user_counts.index, palette='viridis', legend=False)
        plt.title('Top 10 Active Users')
        plt.xlabel('Number of Messages')
        plt.ylabel('User')
        plt.tight_layout()
        user_file = f'analysis_results/{monthly_folder}/user_activity.png'
        plt.savefig(user_file)
        plt.close()

        # Send results
        await ctx.send(file=discord.File(user_file))

async def setup(bot):
    await bot.add_cog(GraphCog(bot))