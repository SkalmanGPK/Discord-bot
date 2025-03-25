# Discord Counting & Entertainment Bot

A multi-functional Discord bot featuring counting, YouTube video retrieval, jokes, and channel statistics.

## Features
- **Auto-counting**: Maintains a counting thread in specified channel (every 6 hours)
- **Video Commands**:
  - `!ddoi` - Random Daily Dose of Internet video
  - `!pewdiepie` - Random PewDiePie video
- **Entertainment**:
  - `!joke` - Random two-part joke
- **Statistics**:
  - `!stat most used words` - Top 10 words in channel
  - `!graph activity` - Message activity charts
  - `!graph toplist` - Top 10 most active users

## Setup

### Prerequisites
- Python 3.9+
- Discord Bot Token
- YouTube API Key (for video commands)

### Installation
1. Clone repository:
   ```bash
   git clone https://github.com/yourusername/discord-bot.git
   cd discord-bot
Install dependencies:

bash
pip install -r requirements.txt
Create required JSON files:

bash
touch channel_messages.json ddoi_videos.json last_post.json pewdiepie_videos.json youtube_cache.json
Create .env file:

ini
TOKEN=your_discord_bot_token
CHANNEL_ID=your_counting_channel_id
YOUTUBE_API_KEY=your_youtube_api_key
Configuration
Required JSON Files
Initialize empty JSON files:

bash
echo "{}" > channel_messages.json
echo "[]" > ddoi_videos.json
echo "[]" > pewdiepie_videos.json
echo "{\"content\":\"0\"}" > last_post.json
echo "{}" > youtube_cache.json
Bot Setup
Create a Discord bot at Discord Developer Portal

Get YouTube API key from Google Cloud Console

Invite bot to your server with proper permissions

Running the Bot
bash
python bot.py
For 24/7 operation (Linux):

bash
nohup python bot.py > bot.log 2>&1 &
Command Reference
Command	Description
!ping	Check bot latency
!ddoi	Random Daily Dose video
!pewdiepie	Random PewDiePie video
!joke	Random joke
!stat most used words	Top 10 words in channel
!graph activity	Hourly/daily activity charts
!graph toplist	Top 10 active users
Maintenance
The bot automatically saves data to JSON files

Analysis charts are saved in analysis_results/ directory

Counting function has 10-minute buffer to conserve API calls

License
MIT
