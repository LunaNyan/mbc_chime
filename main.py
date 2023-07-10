#!/usr/bin/python3

# =====
# Bot Token
bot_token = ""
# Guild ID
guild_id = 0
# Voice Channel ID
vc_id = 0
# =====

import discord
from asyncio import sleep
from discord.utils import get
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='$', intents=intents)

FFMPEG_OPTIONS = {'options': '-vn'}

async def play_chime(force=False):
    vc = get(client.get_all_channels(), id=vc_id)
    if len(vc.members) == 0 and not force:
        return
    guild = client.get_guild(guild_id)
    await vc.connect()
    vclient = guild.voice_client
    await vclient.play(discord.FFmpegPCMAudio("./mbctimer.wav", **FFMPEG_OPTIONS),
                       after=lambda e: client.loop.create_task(vclient.disconnect(force=False)))

@client.listen()
async def on_message(message: discord.Message):
    if message.content == "_test_chime":
        await play_chime(force=True)

@client.event
async def on_ready():
    print("bot is ready")
    while True:
        dt = datetime.now()
        if dt.minute == 59 and dt.second == 52:
            await play_chime()
        await sleep(1)

client.run(bot_token)
