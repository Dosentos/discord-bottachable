from discord_bottachable import settings
from django.core.management.base import BaseCommand
from discord_bottachable.models import User, Link, Tag, Server
from pprint import pprint

import asyncio
import discord
import re

client = discord.Client()
class Command(BaseCommand):
    help = 'discord-bottachable runner management command'

    def handle(self, *args, **kwargs):
        client.run(settings.DISCORD_BOT_TOKEN)



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

    elif message.content.startswith('!link'):
        message_saved, error_message = handle_link(message)
        if message_saved:
            await client.send_message(message.channel, "Thank you, link published on discord-bottachable.discordapp.com")
        else:
            print(error_message)
            await client.send_message(message.channel, "Something went wrong, check logs")

    elif message.content.startswith('!admin_dump_users'):
        objects = User.objects.all()
        for o in objects:
            print("user: %s" % o.discord_id)
        print("%s users in db" % len(objects))
        print("----------")
        await client.send_message(message.channel, "Users dumped into console.")

    elif message.content.startswith('!admin_dump_links'):
        objects = Link.objects.all()
        for o in objects:
            print("url: %s\nuser: %s\nchannel: %s\nserver: %s\ndescription: "
                  "%s\ntitle: %s\nimage: %s\ntagsLen: %s\ncreated: %s\n" % (
                o.source,
                    o.user_id, o.channel_id, o.server_id, o.description,
                    o.title, o.media_url, o.tags.count(), o.created_at))
            print("********************")
        print("%s links in db" % len(objects))
        print("----------")
        await client.send_message(message.channel, "links dumped into console.")

    elif message.content.startswith('!admin_dump_tags'):
        objects = Tag.objects.all()
        for o in objects:
            print("tag: %s" % o.name)
        print("%s tags in db" % len(objects))
        print("----------")
        await client.send_message(message.channel, "Tags dumped into console.")

    elif message.content.startswith('!admin_delete_all_users'):
        User.objects.all().delete()
        print("All users deleted!")
        print("----------")
        await client.send_message(message.channel, "Users deleted")

    elif message.content.startswith('!admin_delete_all_links'):
        Link.objects.all().delete()
        print("All links deleted!")
        print("----------")
        await client.send_message(message.channel, "Links deleted")

    elif message.content.startswith('!admin_delete_all_tags'):
        Tag.objects.all().delete()
        print("All tags deleted!")
        print("----------")
        await client.send_message(message.channel, "Tags deleted")

# This function handles all the messages containing '!link'
def handle_link(message):
    errors = '-----------ERRORS-----------\n'
    msg = re.sub('\!link', '', message.content)
    # msg = message.content.strip('!link')
    if 'http://' in msg or 'https://' in msg or 'www.' in msg:
        message_dict = split_link_message(msg)

        if message_dict['url'] != '':
            saved, errors = link_to_db(message.author.id, message.channel.id, message.server, message_dict, errors)

            if saved:
                print("url: %s\ntitle: %s\ntags: %s" %(message_dict['url'],message_dict['title'],message_dict['tags']))
                print("----------")
                return (True, errors)
        else:
            errors = "%ssplit_link_message function did not find the link\n" % (errors)
    else:
        errors = "%sLinks should contain 'https:', 'http:' or 'www.' prefix\n" % (errors)

    return (False, errors)

# This method splits user's message to url, title and tags.
# Returns a dictionary
def split_link_message(msg):
    message_dict = {'url':'', 'title':'', 'tags': ''}
    title = False
    tags = False
    url_set = False
    print(msg)
    splitted_message = re.split('(tags:|title:)', msg)

    for part in splitted_message:
        if 'http://' in part or 'https://' in part or 'www.' in part:
            if not url_set:
                message_dict['url'] = part
                url_set = True
            else:
                print("Warning, user's message contains more than one link")

        elif 'title:' in part:
            title = True
            tags = False

        elif 'tags:' in part:
            title = False
            tags = True

        else:
            if title:
                message_dict['title'] = "%s %s" %(message_dict['title'], part)

            elif tags:
                if message_dict['tags'] == '':
                    message_dict['tags'] = part
                else:
                    message_dict['tags'] = "%s,%s" %(message_dict['tags'], part)

    message_dict['url'] = message_dict['url'].strip(" ")
    message_dict['title'] = message_dict['title'].strip(' ')
    message_dict['tags'] = message_dict['tags'].strip(' ')
    print(message_dict['tags'])
    return message_dict

# This function saves a link to database
def link_to_db(user_id, channel_id, server, message_dict, errors):

    tags = message_dict['tags'].split(",")

    if len(tags) == 0:
        tags = ['Untagged']
    if message_dict['title'] == '':
        message_dict['title'] = 'Lorem Ipsum Title'

    try:
        # Create or retrieve user
        user, created_user = User.objects.get_or_create(discord_id=user_id)

        # Create or retrieve server
        server, created_server = Server.objects.get_or_create(
            discord_id=server.id,
            defaults={
                'name': server.name
            }
        )

        # Create or retrieve link
        link, created_link = Link.objects.get_or_create(
            server_id=server,
            source=message_dict['url'],
            defaults={
                'user_id': user,
                'channel_id': channel_id,
                'server_id': server,
                'description': "Vivamus imperdiet ligula a lacus congue eleifend id at dui. Cras nec tempor dui. Donec urna neque, pulvinar et felis eu, hendrerit dignissim urna. Donec consequat rutrum diam, tincidunt vulputate augue. Quisque lobortis condimentum hendrerit. Praesent id nulla id erat convallis molestie. Praesent risus ante, euismod nec massa id, pharetra commodo sapien.",
                'title': message_dict['title'],
                'media_url': 'https://media.mustijamirri.fi/media/wysiwyg/Musti_ja_Mirri/Artikkelit/kissa2.jpg',
            }
        )

        # Create or retrieve tags and make connection to the link
        for tag in tags:
            tag = ''.join(e for e in tag if e.isalnum() or e == '-')

            if tag == '':
                continue

            link.tags.add(Tag.objects.get_or_create(name=tag)[0])

    except Exception as e:
        errors = "%sError at inserting or updating database fields\n" % errors
        print(e)
        return False, errors

    return True, errors
