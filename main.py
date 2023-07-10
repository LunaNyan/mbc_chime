#!/usr/bin/python3

import discord
import nacl
import sys
from asyncio import sleep
from discord.utils import get
from discord.ext import commands
from datetime import datetime
from config import *

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='$', intents=intents)

FFMPEG_OPTIONS = {'options': '-vn'}

playing = False
enabled = True

async def disconnect(vc):
    global playing
    await vc.disconnect(force=False)
    playing = False

async def play_chime(force=False):
    global playing
    if playing:
        return
    vc = get(client.get_all_channels(), id=vc_id)
    if len(vc.members) == 0 and not force:
        return
    elif not enabled and not force:
        return
    guild = client.get_guild(guild_id)
    playing = True
    await vc.connect()
    vclient = guild.voice_client
    await vclient.play(discord.FFmpegPCMAudio("./mbctimer.wav", **FFMPEG_OPTIONS),
                       after=lambda e: client.loop.create_task(disconnect(vclient)))

@client.listen()
async def on_message(message: discord.Message):
    global enabled
    if message.content == "_help":
        t = "**_help** : you seeing this\n"
        t += "**_test_chime** : Test Chime\n"
        t += "**_status** : show bot status\n"
        t += "**_toggle** : toggle bot enabled status"
        await message.channel.send(t)
    elif message.content == "_status":
        vc = get(client.get_all_channels(), id=vc_id)
        t = f"**Python version** : {sys.version} @ {sys.platform}\n"
        t += f"**discord.py** : {discord.__version__}\n"
        t += f"**nacl** : {nacl.__version__}\n"
        t += f"**Channel** : {vc.name} ({vc.id})\n"
        t += f"**Enabled** : {enabled}"
        await message.channel.send(t)
    elif message.content == "_toggle":
        if enabled:
            enabled = False
            await message.channel.send("bot disabled")
        else:
            enabled = True
            await message.channel.send("bot enabled")
    elif message.content == "_test_chime":
        if playing:
            await message.channel.send("sound is playing; try again after few seconds")
        else:
            await play_chime(force=True)

@client.event
async def on_ready():
    print("bot is ready")
    await client.change_presence(activity=discord.Game(name="_help"))
    while True:
        dt = datetime.now()
        if dt.minute == 59 and dt.second == 52:
            await play_chime()
        await sleep(1)

client.run(bot_token)
