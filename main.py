import discord
from discord.ext import commands
import youtube_dl
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    channel = bot.get_channel(1075153278410690711)
    if not channel:
        print("Unable to find the channel.")
        return

    voice_channel = await channel.connect()

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'download': False
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info("https://www.youtube.com/live/jfKfPfyJRdk?si=GDx3AgrQdB9CYTOP", download=False)
        URL = info['formats'][0]['url']
        voice_channel.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=URL))

bot.run(BOT_TOKEN)
