
import discord
from discord.ext import commands
import yt_dlp
import os
import asyncio

intents = discord.Intents.all()

bot = commands.Bot(command_prefix="+", intents=intents)

# Directory to store downloaded audio
DOWNLOAD_DIR = "downloads/"

# Ensure download directory exists
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# Function to download audio from YouTube
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        mp3_filename = filename.replace('.webm', '.mp3')  # Change extension to .mp3
        return mp3_filename


# Play command
@bot.command(name="play")
async def play(ctx, url: str):
    voice_channel = ctx.author.voice.channel
    if not voice_channel:
        await ctx.send("You need to be in a voice channel to play music.")
        return

    # Connect to the voice channel
    vc = await voice_channel.connect()

    # Get the filename for the .mp3
    filename = os.path.join(DOWNLOAD_DIR, url.split("v=")[-1] + '.mp3')

    # Check if the .mp3 file exists
    if not os.path.isfile(filename):
        # Download the audio file
        filename = download_audio(url)

    # Play the audio file
    vc.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=filename))

    while vc.is_playing():
        await asyncio.sleep(1)

    await vc.disconnect()


# Stop command
@bot.command(name="stop")
async def stop(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send("Music stopped.")
    else:
        await ctx.send("No music is playing.")


# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')



Token = "Your Token Here"
bot.run(Token)
