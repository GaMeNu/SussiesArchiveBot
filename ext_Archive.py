import asyncio
import json
import random
from pathlib import Path

import discord
import discord.ext.commands.cog as cog
import discord.ext.commands as commands
from discord import app_commands
import os
from typing import Union

from dotenv import load_dotenv


class UserData:
    def __init__(self, name, num):
        self.name = name
        self.entryNum = num

class Archive(cog.GroupCog):
    def __init__(self, bot):
        load_dotenv()

        self.bot: discord.Client = bot
        self.FOLDER_NAME: str = os.getenv("ARCHIVE_FOLDER")
        self.SUBMISSION_CHANNEL_ID: int = int(os.getenv("SUBMISSION_CHANNEL"))
        self.SUBMISSION_CHANNEL = self.bot.get_channel(self.SUBMISSION_CHANNEL_ID)
        self.SUBMISSION_FOLDER = os.getenv("SUB_FOLDER")
        self.AUTHOR_ID = int(os.getenv("AUTHOR_ID"))

    @app_commands.command(name='list', description='List archive users')
    async def cmd_archive_list(self, intr: discord.Interaction):
        await intr.response.defer()
        e = discord.Embed(colour=discord.Colour.from_rgb(114, 40, 204),
                          title='The Sussies Archive',
                          description='List of all available people:')
        entries: list[UserData] = []
        for name in os.listdir(f"./{self.FOLDER_NAME}"):
            path = f"./{self.FOLDER_NAME}/{name}"
            num_files = len(os.listdir(path))
            new_data = UserData(name, num_files)
            i = 0
            while i < len(entries) and new_data.entryNum < entries[i].entryNum:
                i += 1
            entries.insert(i, new_data)

        for data in entries:
            e.add_field(name=data.name, value=f'{data.entryNum} entries', inline=False)
        await intr.followup.send(
            content='Here you go!', embed=e)

    @app_commands.command(name='getname', description='get a user\'s random archive entry')
    async def archive(self, intr: discord.Interaction, name: str):
        await intr.response.defer()

        path = f"./{self.FOLDER_NAME}/{name}"
        if not os.path.exists(path):
            await intr.followup.send(
                embed=discord.Embed(colour=discord.Colour.red(),
                                    title="Error:",
                                    description="Could not find username!\nPlease run \"/archive\" to get a list of all available users"
                                    )
            )
            return

        files = [os.path.join(path, f) for f in os.listdir(path)]
        f = random.choice(files)

        await intr.followup.send(files=[discord.File(f)])

    @app_commands.command(name='items', description='List archive users')
    async def cmd_archive_items(self, intr: discord.Interaction, name: str):
        await intr.response.defer()

        path = f"./{self.FOLDER_NAME}/{name}"
        if not os.path.exists(path):
            await intr.followup.send(
                embed=discord.Embed(colour=discord.Colour.red(),
                                    title="Error: Could not find username!",
                                    description="Please run \"/archive\" to get a list of all available users"
                                    )
            )
            return


        num_files = len(os.listdir(path))
        e = discord.Embed(colour=discord.Colour.from_rgb(114, 40, 204),
                          title='The Sussies Archive',
                          description=f'Total of {num_files} entries for user {name}:')
        for name in os.listdir(path):
            e.add_field(name=name, value='', inline=False)

        await intr.followup.send(
            content='Here you go!', embed=e)

    @app_commands.command(name='random', description='Get a random quote from the entire archive. (True random - biased towards users with more entries)')
    async def cmd_archive_random(self, intr: discord.Interaction, true_random: bool = False):
        await intr.response.defer()
        path = os.path.join('.', self.FOLDER_NAME)
        if true_random is False:
            users = [f for f in os.listdir(path)]
            user = random.choice(users)
            path = os.path.join(path, user)

            files = [f for f in os.listdir(path)]
            file = random.choice(files)
            path = os.path.join(path, file)

            await intr.followup.send(content=f'{user}\\{file}: (True random: off)', files=[discord.File(path)])
            return

        files = {}
        for user in os.listdir(path):
            for file in os.listdir(os.path.join(path, user)):
                files[file] = user

        file = random.choice(list(files.keys()))
        user = files[file]

        path = os.path.join(path, user, file)

        await intr.followup.send(content=f'{user}\\{file}: (True random: on)', files=[discord.File(path)])

    async def save_submission(self, msg: discord.Message):
        if msg.content.startswith('#!') and msg.author.id == self.AUTHOR_ID:
            return

        if len(msg.attachments) == 0:
            await msg.delete()
            return


        for att in msg.attachments:
            if 'image' in att.content_type:
                print(f'Saving item {att.filename}')
                await att.save(Path(os.path.join('.', self.SUBMISSION_FOLDER, att.filename)))

        await msg.delete()
    @app_commands.command(name='sync_submissions', description='Sync the submission channel (Allowed only for author)')
    async def cmd_archive_sync_submissions(self, intr: discord.Interaction):
        if intr.user.id != self.AUTHOR_ID:
            await intr.response.send_message('Error: no permission!', ephemeral=True)
            return
        await intr.response.send_message('Started syncing...', ephemeral=True)
        async for message in self.SUBMISSION_CHANNEL.history(limit = 1000, oldest_first=True):
            await self.save_submission(message)
            await asyncio.sleep(0.1)

        await intr.followup.send('Finished syncing!', ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.channel.id == self.SUBMISSION_CHANNEL_ID:
            await self.save_submission(msg)



    async def setup(bot):
        archive_cog = Archive(bot)
        await bot.add_cog(archive_cog)
        return archive_cog


def setup(bot):
    return Archive.setup(bot)
