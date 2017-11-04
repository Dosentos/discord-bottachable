from discord_bottachable import settings
from django.core.management.base import BaseCommand
from discord_bottachable.models import User, Link, Tag, Server
from pprint import pprint

import urllib.request
import asyncio
import discord
import logging
import re

# Create an instance of logger
logger = logging.getLogger(__name__)

# Create an instance of discord API
client = discord.Client()

class Command(BaseCommand):
    help = 'discord-bottachable runner management command'

    # This runs forever listening all the authorized servers
    def handle(self, *args, **kwargs):
        client.run(settings.DISCORD_BOT_TOKEN)

@client.event
async def on_ready():
    logger.info('%s ONLINE!' % client.user.name)

# This function is triggered whenever the authorized server captures any message
# In here happens all the magic...
@client.event
async def on_message(message):
    await handle_messages(message)

@client.event
async def on_message_edit(before, after):
    await handle_messages(after)

async def handle_messages(message):
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
        message_saved = False
        error_message = ''
        message_saved, error_message = handle_link(message)
        if message_saved:
            await client.send_message(message.channel, "Thank you, link published on discord-bottachable.discordapp.com")
        else:
            await client.send_message(message.channel, "Oops! Something went wrong:\n%s" % (error_message))

    elif message.content.startswith('!admin_dump_users'):
        objects = User.objects.all()
        logger.info("----------")
        for o in objects:
            logger.info("user: %s" % o.discord_id)
        logger.info("%s users in db" % len(objects))
        logger.info("----------")
        await client.send_message(message.channel, "Users dumped into console.")

    elif message.content.startswith('!admin_dump_links'):
        objects = Link.objects.all()
        logger.info("----------")
        for o in objects:
            logger.info("url: %s\nuser: %s\nchannel: %s\nserver: %s\ndescription: "
                  "%s\ntitle: %s\nimage: %s\ntagsLen: %s\ncreated: %s\n" % (
                o.source,
                    o.user_id, o.channel_id, o.server_id, o.description,
                    o.title, o.media_url, o.tags.count(), o.created_at))
            logger.info("********************")
        logger.info("%s links in db" % len(objects))
        logger.info("----------")
        await client.send_message(message.channel, "links dumped into console.")

    elif message.content.startswith('!admin_dump_tags'):
        objects = Tag.objects.all()
        for o in objects:
            logger.info("tag: %s" % o.name)
        logger.info("%s tags in db" % len(objects))
        logger.info("----------")
        await client.send_message(message.channel, "Tags dumped into console.")

    elif message.content.startswith('!admin_delete_all_users'):
        User.objects.all().delete()
        logger.info("All users deleted!")
        logger.info("----------")
        await client.send_message(message.channel, "Users deleted")

    elif message.content.startswith('!admin_delete_all_links'):
        Link.objects.all().delete()
        logger.info("All links deleted!")
        logger.info("----------")
        await client.send_message(message.channel, "Links deleted")

    elif message.content.startswith('!admin_delete_all_tags'):
        Tag.objects.all().delete()
        logger.info("All tags deleted!")
        logger.info("----------")
        await client.send_message(message.channel, "Tags deleted")

# This function handles all the messages containing '!link'
def handle_link(message):
    errors = ''
    msg = re.sub('\!link', '', message.content)
    if 'http://' in msg or 'https://' in msg or 'www.' in msg:
        message_dict = split_link_message(msg)
        message_dict.update(get_embeds(message.embeds))
        if message_dict['url'] != '':
            saved, errors = link_to_db(message.author.id, message.channel.id, message.server, message_dict)
            pass

            if saved:
                return (True, errors)
        else:
            logger.info("split_link_message function could not find the url")
            errors = "%sCould not find the url from the message\n" % (errors)
    else:
        logger.info("Link does not contain correct prefix")
        errors = "%sThere was no 'https:', 'http:' or 'www.' prefix in your link\n" % (errors)

    return (False, errors)

# This method splits user's message to url, title and tags.
# Returns a dictionary
def split_link_message(msg):
    message_dict = {'url':'', 'title':'', 'tags': ''}
    title = False
    tags = False
    url_set = False
    logger.info("Message: %s" % (msg))
    splitted_message = re.split('(tags:|title:)', msg)

    for part in splitted_message:
        if 'http://' in part or 'https://' in part or 'www.' in part:
            if not url_set:
                message_dict['url'] = part
                url_set = True
            else:
                logger.warn("Warning, user's message contains more than one link")

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
    return message_dict

# This function saves a link to database
def link_to_db(user_id, channel_id, server, message_dict):
    errors = ''
    if message_dict['tags'] == '':
        message_dict['tags'] = 'Untagged'

    if message_dict['title'] == '':
        message_dict['title'] = 'Lorem Ipsum Title'

    tags = message_dict['tags'].split(",")

    if message_dict['media_url'] = '':
        message_dict['media_url'] = '%s/pic/no_thumbnail.png' % (STATIC_URL)
    if message_dict['title'] = '':
        message_dict['title'] = findTitle(message_dict['url'])
    if message_dict['description'] = '':
        pass
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
                'description':message_dict['description'],
                'title': message_dict['title'],
                'media_url': message_dict['media_url'],
            }
        )

        # Create or retrieve tags and make connection to the link
        for tag in tags:
            tag = ''.join(e for e in tag if e.isalnum() or e == '-')

            if tag == '':
                continue

            link.tags.add(Tag.objects.get_or_create(name=tag)[0])

    except Exception as e:
        logger.error("Error at inserting or updating database fields\n%s" % (e))
        errors = ("%s%s\n" % (errors, e.message))
        return False, errors

    logger.info("Saved! url: %s\ntitle: %s\ntags: %s" %(message_dict['url'],message_dict['title'],message_dict['tags']))
    logger.info("----------")
    return True, errors

def get_embeds(embeds):
    embeds_dict = {'description':'', 'media_url':'','title':''}
    for e in embeds:
        if 'description'  in e:
            embeds_dict['description'] = e['description']
        else:
            logger.info('Embeds have no description!')
        if 'title' in e:
            embeds_dict['title'] = e['title']
        else:
            logger.info('Embeds have no title!')
        if 'thumbnail' in e and 'url' in e['thumbnail']:
            embeds_dict['media_url'] = e['thumbnail']['url']
        else:
            logger.info('Embeds have no thubnail or thubnail url!')
    return embeds_dict


# THIS FUNCTION IS VERY BAD!!!
# If there's no </title> tag on the site it returns all the html after starting tag
# If there's no start tag, it throws an indexError: list index out of range
# Maybe use something else
# IF THIS IS CHANGED TAKE OFF urllib.request IMPORT TOO

#TODO: Change the method or add handling in case there's no title in the link
# return 'Untitled' if no title is found!
def findTitle(url):
    webpage = urllib.request.urlopen(url).read()
    title = str(webpage).split('<title>')[1].split('</title>')[0]
    return title
