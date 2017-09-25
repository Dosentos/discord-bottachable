from discord_bottachable import settings
from django.core.management.base import BaseCommand
# from discord_bottachable.models import User, Attachment, Tag

import discord
import asyncio

client = discord.Client()
class Command(BaseCommand):
    help = 'discord-bottachable runner management command'

    @client.event
    async def on_ready():
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('------')

    @client.event
    async def on_message(message):
        if message.content.startswith('!test'):
            counter = 0
            tmp = await client.send_message(message.channel, 'Calculating messages...')
            async for log in client.logs_from(message.channel, limit=100):
                if log.author == message.author:
                    counter += 1

            await client.edit_message(tmp, 'You have {} messages.'.format(counter))
        elif message.content.startswith('!sleep'):
            await asyncio.sleep(5)
            await client.send_message(message.channel, 'Done sleeping')

    def handle(self, *args, **kwargs):
        client.run(settings.DISCORD_BOT_TOKEN)