import asyncio

import discord
from discord import Guild, Member, Message, User

from config import config

token = config.get("discord")["token"]
server_id = config.get("discord")["server_id"]
channel_id = config.get("discord")["channel_id"]


def _run(client, coor):
    return asyncio.run_coroutine_threadsafe(coor, client.loop).result()


def send_message(client, sender, message):
    async def _send_message():
        channel = client.get_channel(channel_id)
        author: User = await client.fetch_user(sender)
        await channel.send(f"{author.mention} says,\n\n{message}")

    _run(client, _send_message())


def close(client):
    async def _quit():
        await client.close()

    _run(client, _quit())


class MyClient(discord.Client):
    def __init__(self, callback, **options):
        super().__init__(**options)
        self.callback = callback

    async def on_ready(self):
        print('Logged on as', self.user)

    async def on_message(self, message: Message):
        # don't respond to itself
        if message.author == self.user:
            return

        if message.guild is None or message.channel.id != channel_id:
            return

        self.callback(f"Discord message:\n\n{message.author.name}#{message.author.discriminator}: "
                      f"{message.content}")


if __name__ == '__main__':
    _client = MyClient(lambda x: print(x))
    _client.run(token)
