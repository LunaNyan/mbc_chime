#!/usr/bin/python3

import discord
import nacl
import sys
import os
from asyncio import sleep
from discord.utils import get
from discord.ext import commands
from datetime import datetime
from pathlib import Path
from config import *

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='$', intents=intents)

playing = False
enabled = True

async def disconnect(vc, filename):
    global playing
    await vc.disconnect(force=False)
    if filename != "./mbctimer.wav":
        os.remove(filename)
    print("done")
    playing = False

async def play_chime(force=False, filename="./mbctimer.wav"):
    global playing
    global enabled
    print(f"enabled : {enabled}, playing : {playing}")
    if playing:
        return
    vc = get(client.get_all_channels(), id=vc_id)
    if len(vc.members) == 0 and not force:
        return
    elif not enabled and not force:
        return
    guild = client.get_guild(guild_id)
    playing = True
    print("establishing vc connection")
    await vc.connect()
    vclient = guild.voice_client
    vclient.play(discord.FFmpegPCMAudio(filename),
                 after=lambda e: client.loop.create_task(disconnect(vclient, filename)))

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
            await message.channel.send("sound is playing; try again after few moments")
        else:
            await play_chime(force=True)
    elif message.content == "_play_this":
        if playing:
            await message.channel.send("sound is playing; try again after few moments")
            return
        if len(message.attachments) != 1:
            await message.channel.send("attach 1 audio file to play")
        else:
            msg = await message.channel.send("downloading")
            await message.attachments[0].save(Path(message.attachments[0].filename))
            await msg.edit(content="downloaded, playing")
            await play_chime(force=True, filename=message.attachments[0].filename)

async def chime_tick():
    while True:
        dt = datetime.now()
        if dt.minute == 59 and dt.second == 52:
            print("calling chime (auto)")
            await play_chime()
        await sleep(.5)

@client.event
async def on_ready():
    print("bot is ready")
    await client.change_presence(activity=discord.Game(name="_help"))
    client.loop.create_task(chime_tick())

client.run(bot_token)
