import discord
from discord.ext import tasks
import os
import subprocess
import asyncio

# Replace with your YouTube API key
YOUTUBE_API_KEY = os.environ["API_KEY"]
bot_token = os.environ["BOT_TOKEN"]

# Server and voice channel IDs
SERVER_ID = 1064091614793957396
VOICE_CHANNEL_ID = 1075153278410690711

# YouTube video URL
YOUTUBE_URL = "https://www.youtube.com/live/jfKfPfyJRdk?si=GDx3AgrQdB9CYTOP"

async def play_livestream(client, guild):
    """Joins the specified voice channel and plays the YouTube livestream."""

    voice_channel = guild.get_channel(VOICE_CHANNEL_ID)
    if not voice_channel:
        print("Voice channel not found!")
        return

    voice_client = await voice_channel.connect()

    # Use youtube-dl for advanced livestream extraction
    ytdl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': '%(id)s.%(ext)s',
        'download': False,
        'source_address': '0.0.0.0',  # Optional: fix IPv6 issues
    }

    # Install youtube-dl if not present
    try:
        import youtube_dl
    except ImportError:
        print("Installing youtube_dl...")
        os.system("pip install youtube_dl")
        import youtube_dl

    ydl = youtube_dl.YoutubeDL(ytdl_opts)

    with youtube_dl.YoutubeDL(ytdl_opts) as ydl:
        info = ydl.extract_info(YOUTUBE_URL, download=False)
        url = info['url']

    # Start FFmpeg process to convert and pipe audio to discord
    ffmpeg_cmd = ["ffmpeg", "-i", url, "-f", "s16le", "-ar", "48000", "-ac", "2", "pipe:1"]
    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    # Read audio chunks from FFmpeg and play them
    while True:
        data = ffmpeg_process.stdout.read(1024)
        if not data:
            break
        source = discord.PCMAudio(data)
        voice_client.play(source, after=None)
        source.wait()

    # Cleanup: stop FFmpeg process and wait for it to finish
    ffmpeg_process.terminate()
    ffmpeg_process.wait()

async def main():
    """Connects to the Discord server and starts the bot."""

    intents = discord.Intents.default()
    intents.voice_states = True  # Required for voice functionality

    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f"Logged in as {client.user}")

        guild = client.get_guild(SERVER_ID)
        if not guild:
            print("Server not found!")
            return

        await play_livestream(client, guild)

    await client.run(bot_token)

if __name__ == "__main__":
    asyncio.run(main())

