import discord
from discord.ext import tasks
import youtube_dl
import asyncio
import os
from discord import app_commands
from discord.ext import commands

bot = commands.Bot(command_prefix="g.", intents=discord.Intents.all())
# Replace with your bot token
BOT_TOKEN = os.environ['BOT_TOKEN']

# Replace with your target voice channel ID
VOICE_CHANNEL_ID = 1075153278410690711

# Replace with your target server ID
SERVER_ID = 1064091614793957396

# Live stream URL
LIVE_STREAM_URL = 'https://www.youtube.com/live/jfKfPfyJRdk?si=GDx3AgrQdB9CYTOP'

ydl_opts = {
    'format': 'bestaudio/best',
    'download': False,
    'no_warnings': True,
    'quiet': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # Prevent potential IPv6 issues
}

async def connect_to_voice_channel(bot):
    """Connects the bot to the specified voice channel and starts playing the live stream."""
    guild = bot.get_guild(SERVER_ID)
    if not guild:
        print(f"Server with ID {SERVER_ID} not found.")
        return

    voice_channel = guild.get_channel(VOICE_CHANNEL_ID)
    if not voice_channel:
        print(f"Voice channel with ID {VOICE_CHANNEL_ID} not found.")
        return

    try:
        voice_client = await voice_channel.connect()
        print("Connected to voice channel.")

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(LIVE_STREAM_URL, download=False)
            url = info['formats'][0]['url']

            source = discord.FFmpegOpusAudio(url, options='-vn')  # Use audio-only stream
            voice_client.play(source, after=None)

            while voice_client.is_playing():
                await asyncio.sleep(1)  # Check playback status at intervals

            print("Live stream playback finished.")
            await voice_client.disconnect()
            print("Disconnected from voice channel.")

    except Exception as e:
        print(f"Error occurred: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    connect_to_voice_channel.start(bot)  # Start playback on bot readiness

bot = discord.Bot()
bot.run(BOT_TOKEN)
