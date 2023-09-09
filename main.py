import discord
from discord import app_commands
import discord.ext.commands as commands
from dotenv import load_dotenv
import json
import os
import random

import ext_Archive

AUTHOR_ID = 474901193563570186
FOLDER_NAME = 'BWU_sussies'
TOKEN: str


bot = commands.Bot(intents=discord.Intents.all(), command_prefix='!')
tree = bot.tree


@bot.event
async def on_message(msg: discord.Message):
    global AUTHOR_ID, tree
    if msg.content == '/sync_cmds' and msg.author.id == AUTHOR_ID:
        await msg.reply('Syncing...', delete_after=3)
        await tree.sync()
        await msg.reply('Synced!', delete_after=3)






@bot.event
async def on_ready():
    if bot.get_cog("Archive") is None:
        cog_gd = await ext_Archive.setup(bot)




load_dotenv()

TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)
