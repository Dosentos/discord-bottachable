from bs4 import BeautifulSoup
from discord_bottachable import settings
from django.core.management.base import BaseCommand
from discord_bottachable.models import User, Role, Link, Tag, Server, Channel
from datetime import datetime

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



# Creates appropriate Discord message from given query set.
def create_log_msg(message, querySet, server = None):
    d = datetime.now()
    msg = (
        "```RESULTS FOR \"{0}:{1}\" ({2})\n"
    ).format(message.author.name,message.content,d.strftime("%d/%m/%Y %H:%M"))
    msg += "---------------------------------------------------\n"

    for obj in querySet:
        msg += "{0}".format(str(obj))
        if isinstance(obj, User):
            # If listing user instances: find user rank in the server
            roles = Role.objects.filter(
                server_id=server,
                user_id=obj
            )
            if len(roles) > 0:
                msg += "{0}".format(str(roles[0]))
        msg += "----------\n"

    msg += "---------------------------------------------------\n"
    msg += "{0} total matches in the database.".format(len(querySet))
    msg += "```"
    return msg


# Handles admin command checks and functionality.
async def handle_admin_commands(rows, message):
   
    # Check has the message sender admin privileges in the server
    if rows["role"].rank < 1:
        return False

    dest = message.channel
    verbose = False
    chann_msg = (
        "\n``Note: Some details omitted. Please specify !log_channel "
        "for the bot for more data.``"
    )

    if rows['server'].log_channel is not None:
        chann = client.get_channel(rows['server'].log_channel.discord_id)
        if chann is not None:
            dest = chann
            verbose = True
    
    if message.content.startswith('!log_channel'):
        msg = (
            "Please specify valid channel in the server. "
            "``!log_channel (#channel-name)``"
        )
        if message.channel_mentions:
            chann = message.channel_mentions[0]
            # Create or retrieve the database row of the channel
            channel, created_channel = Channel.objects.get_or_create(
                discord_id=chann.id,
                server_id=rows['server'],
                defaults={
                    'listen': 0,
                    'name': chann.name
                }
            )
            rows['server'].log_channel = channel
            rows['server'].save()
            msg = "Log channel is set to {0}".format(chann.mention)
        await client.send_message(dest, msg)
        return True
    elif message.content.startswith('!dump_users'):
        member_ids = [m.id for m in message.server.members]
        users = User.objects.filter(discord_id__in=member_ids)
        msg = (
            "There are {0} users in the database "
            "for this server. {1}"
        ).format(len(users), chann_msg)
        if verbose:
            msg = create_log_msg(message, users, rows["server"])
        await client.send_message(dest, msg)
        return True
    elif message.content.startswith('!dump_links'):
        links = Link.objects.filter(server_id=rows['server'])
        msg = (
            "There are {0} links in the database "
            "for this server. {1}"
        ).format(len(links), chann_msg)
        if verbose:
            msg = create_log_msg(message, links)
        await client.send_message(dest, msg)
        return True
    elif message.content.startswith('!dump_tags'):
        tags = Tag.objects.filter(
            tags__in=Link.objects.filter(server_id=rows["server"])
        ).distinct()
        msg = (
            "There are {0} tags in the database "
            "for this server. {1}"
        ).format(len(tags), chann_msg)
        if verbose:
            msg = create_log_msg(message, tags)
        await client.send_message(dest, msg)
        return True
    elif message.content.startswith('!delete_all_links'):
        Link.objects.filter(server_id=rows['server']).delete()
        await client.send_message(
            dest,
            "<@{0}> deleted all saved links.".format(message.author.id)
        )
        return True
    elif message.content.startswith('!delete_all_tags'):
        tags = Tag.objects.filter(
            tags__in=Link.objects.filter(server_id=rows["server"])
        ).delete()
        await client.send_message(
            dest,
            "<@{0}> deleted all tags.".format(message.author.id)
        )
        return True

    return False


# Creates or retrieves database rows related to the message in the server.
# Returns dictionary of the data and success flag
def get_database_rows(message):
    
    data = {"success": True}
    try:
        
        # Create or retrieve server row from the database
        data["server"], data["created_server"] = Server.objects.get_or_create(
            discord_id=message.server.id,
            defaults={
                'name': message.server.name
            }
        )

        # Create or retrieve sender's row from the database
        data["user"], data["created_user"] = User.objects.get_or_create(
            discord_id=message.author.id,
            defaults={
                'username': message.author.name
            }
        )

        # Update username if it's changed
        if not data["created_user"]\
        and data["user"].username != message.author.name:
            data["user"].username = message.author.name
            data["user"].save()
        
        is_owner = message.author.id == message.server.owner.id
        
        # Create or retrieve sender's role row from the database
        # Server's owner gets automatically higher rank 
        data["role"], data["created_role"] = Role.objects.get_or_create(
            server_id=data["server"],
            user_id=data["user"],
            defaults={
                "rank": 2 if is_owner else 0
            }
        )

    except Exception as e:
        logger.error("Error at fetching db rows:\n{0}".format(e))
        data["success"] = False
    
    
    return data


async def handle_messages(message):

    # Exit if message is DM
    if message.server is None:
        return

    # Exit if not command
    if not message.content[0] == "!":
        return

    rows = get_database_rows(message)
    # Exit if there's an error getting db rows
    if not rows["success"]:
        logger.error("Message not processed because error in db fetch")
        return

    if await handle_admin_commands(rows, message):
        return

    # Other normie commands:
    elif message.content.startswith('!link'):
        message_saved = False
        error_message = ''
        message_saved, error_message = handle_link(message, rows)
        if message_saved and error_message == 'updated':
            await client.send_message(message.channel, "Thanks! Link updated on %s%s" %(settings.WEBSITE_URL, message.server.id))
        elif message_saved:
            await client.send_message(message.channel, "Thanks! See your link on %s%s" %(settings.WEBSITE_URL, message.server.id))
        else:
            await client.send_message(message.channel, "Oops! Something went wrong:\n%s" % (error_message))


# This function handles all the messages containing '!link'
def handle_link(message, rows):
    errors = ''
    msg = re.sub('\!link', '', message.content)
    if 'http://' in msg or 'https://' in msg or 'www.' in msg:
        message_dict = split_link_message(msg)
        message_dict.update(get_embeds(message.embeds))
        if message_dict['url'] != '':
            saved, errors = link_to_db(
                message.author.id,
                message.channel.id,
                message.server,
                message_dict,
                rows,
                message
            )
            if saved:
                return (True, errors)
        else:
            logger.info("split_link_message function could not find the url")
            errors = "%sCould not find the url from the message\n" % (errors)
    else:
        logger.info("Link does not contain correct prefix")
        errors = "%sThere was no 'https:', 'http:' or 'www.' prefix in your link\n" % (errors)

    return (False, errors)

# Find possible url in a string
def find_url(msg):
    return re.search('http(|s):\/\/|www\.', msg)


# Finds title and tags from the !link command message's words
# Return list of the words found
def get_words(words, start_word, stop_word, url):
    results = []
    # Loop through all given words
    for word in words:
        # If the word is just the start_word, continue
        if word == start_word: continue

        # If start_word is tied to the word without space, remove it
        if start_word in word: word = word.replace(start_word, '')
        # Break if stop word is found
        if stop_word in word: break
        # Title and tags can have url if another url is found already
        if not find_url(word) or url:
            if start_word == 'tags:':
                # Finding tags, there might be ',' in the word/tag, remove that
                results.append(word.strip(','))
                continue
            results.append(word)

    return results


# This method splits user's message to url, title and tags.
# Returns a dictionary
def split_link_message(msg):
    data = {'url': '', 'title': '', 'tags': []}
    words = msg.split()
    # Loop through command message's words
    for index, word in enumerate(words):
        # If word contains url and there is no url set yet, set this as our url
        if find_url(word) and not data['url']:
            data['url'] = word
        elif 'title:' in word and not data['title']:
            data['title'] = ' '.join(
                get_words(words[index:], 'title:', 'tags:', data['url'])
            )
        elif 'tags:' in word and not data['tags']:
            data['tags'] = get_words(words[index:], 'tags:', 'title:', data['url'])
    
    return data


# This function saves a link to database
def link_to_db(user_id, channel_id, server, message_dict, rows, message):
    errors = ''
    updated = False
    verified, verified_url = verifyUrl(message_dict['url'])

    if not verified:
        errors = "%sYour link could not be validated\n" % (errors)
        logger.info("Could not verify url: %s"% verified_url)
        return False, errors
    else:
        message_dict['url'] = verified_url

    if message_dict['provider'] not in message_dict['tags'] and message_dict['provider'] != '':
        message_dict['tags'].append(message_dict['provider'])
    elif len(message_dict['tags']) == 0:
        message_dict['tags'].append('untagged')

    if message_dict['title'] == '':
        message_dict['title'] = findTitle(message_dict['url'])
    if message_dict['description'] == '':
        pass
    try:
        # Create or update/retrieve message's channel row from the database
        channel, created_channel = Channel.objects.update_or_create(
            discord_id=message.channel.id,
            server_id=rows['server'],
            defaults={
                'listen': 0,
                'name': message.channel.name
            }
        )
    except Exception as e:
        logger.error("Error at inserting or updating channel fields\n%s" % (e))
        errors = ("%s%s\n" % (errors, e.message))
        return False, errors

    try:
        # Create or update/retrieve link
        link, created_link = Link.objects.update_or_create(
            server_id=rows['server'],
            source=message_dict['url'],
            defaults={
                'user_id': rows['user'],
                'channel_id': channel,
                'description': message_dict['description'],
                'title': message_dict['title'],
                'media_url': message_dict['media_url'],
                'media_type': message_dict['media_type']
            }
        )
    except Exception as e:
        logger.error("Error at inserting or updating Link fields\n%s" % (e))
        errors = ("%s%s\n" % (errors, e.message))
        return False, errors

    # Create or update/retrieve tags and make connection to the link
    for tag in message_dict['tags']:
        tag = ''.join(e for e in tag if e.isalnum() or e == '-')
        if tag == '':
            continue
        try:
            link.tags.add(Tag.objects.get_or_create(name=tag)[0])
        except Exception as e:
            logger.error("Error at inserting or updating Link fields\n%s" % (e))
            errors = ("%s%s\n" % (errors, e.message))
            return False, errors

    if not created_link:
        updated = True

    logger.info("Saved!\n url: '%s', title: '%s', tags: '%s', description: '%s', media_url: '%s', " %(message_dict['url'],message_dict['title'],message_dict['tags'],message_dict['description'],message_dict['media_url']))
    logger.info("----------")

    if updated and errors == '':
        errors = 'updated'
        return True, errors

    return True, errors

# This function saves the specific embeds to embeds_dicts and returns them
def get_embeds(embeds):
    logger.info(embeds)
    embeds_dict = {'description':'', 'media_url':'','title':'', 'provider':'', 'media_type': 'no_media'}
    for e in embeds:
        if 'description'  in e:
            embeds_dict['description'] = e['description']
        else:
            logger.info('Embeds have no description!')

        if 'title' in e:
            embeds_dict['title'] = e['title']
        else:
            logger.info('Embeds have no title!')

        if 'video' in e and 'url' in e['video']:
            embeds_dict['media_url'] = e['video']['url']
            embeds_dict['media_type'] = 'video'
        elif 'thumbnail' in e and 'url' in e['thumbnail']:
            embeds_dict['media_url'] = e['thumbnail']['url']
            embeds_dict['media_type'] = 'picture'
        else:
            logger.info('Embeds have no thumbnail or thumbnail url!')

        if 'provider' in e and  'name' in e['provider']:
            embeds_dict['provider'] = e['provider']['name'].lower().strip(' ')
        else:
            logger.info('Embeds have no provider name')

    return embeds_dict

# This function is called if no title has been found elsewhere. 
# It simply tries to find the title from the website in the url
def findTitle(url):
    # Get the html from the url
    webpage = urllib.request.urlopen(url).read()

    # Create an instance of beautifulSoup
    soup = BeautifulSoup(webpage, 'html.parser')

    # Find title tag
    if soup.title:
        title = soup.title.string
    else:
        title = 'Untitled'
    return title

def verifyUrl(url):
    verified = False
    new_url = url
    if new_url.startswith('www.'):
        new_url = "http://%s" % (url)
    try:
        urllib.request.urlopen(new_url)
        verified = True
    except Exception as e:
        logger.info(e)
        if new_url.startswith('http://'):
            new_url = new_url[:4] + "s" + new_url[4:]
        elif new_url.startswith('https://'):
            new_url = new_url[:4] + new_url[5:]
        try:
            urllib.request.urlopen(new_url)
            verified = True
        except Exception as e:
            logger.info(e)
            logger.info("Invalid url given")
            new_url = url
    if new_url.endswith('/'):
        new_url = new_url[:-1]
    return (verified, new_url)
