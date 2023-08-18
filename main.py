import random

import discord
from discord import app_commands
import discord.ext.commands as commands
from dotenv import load_dotenv
import os

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


@tree.command(name='archive', description='TBA')
async def archive(intr: discord.Interaction, user: str | None):
    await intr.response.defer()

    if user == None:
        e = discord.Embed(colour=discord.Colour.from_rgb(114, 40, 204),
                          title='The Sussies Archive',
                          description='List of all available people:')

        for name in os.listdir(f"./{FOLDER_NAME}"):
            path = f"./{FOLDER_NAME}/{name}"
            num_files = len([f for f in os.listdir(path)
                             if os.path.isfile(os.path.join(path, f))])


            e.add_field(name=name, value=f'{num_files} entries', inline=False)
        await intr.followup.send(content='Here you go! Run the command with a name to get one of their entries at random!', embed=e)
        return
    path = f"./{FOLDER_NAME}/{user}"
    if not os.path.exists(path):
        await intr.followup.send(
            embed=discord.Embed(colour=discord.Colour.red(),
                                title="Error:",
                                description="Could not find username!\nPlease run \"/archive\" to get a list of all available users"
                                )
        )
    files = [os.path.join(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    f = random.choice(files)

    await intr.followup.send(files=[discord.File(f)])




load_dotenv()

TOKEN = os.getenv("TOKEN")

bot.run(TOKEN)
