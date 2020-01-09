import datetime
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
CHANNEL = os.getenv('DISCORD_CHANNEL')

bot = commands.Bot(command_prefix='!')

# Timeout control
enabled = True
timeout = datetime.timedelta(minutes=30)

guild = None
channel = None
# Keep track of state as globals? In my code? It's more likely than you think.
# We'll be fine as long as we update these atomically between async operations.
last_timestamp = None
last_user = None


async def is_officer(ctx):
    good = discord.utils.find(lambda r: r.name == 'GM' or r.name == 'Captain', ctx.author.roles)
    return good is not None


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('`ERROR--ERROR-user-lacks-sufficient-authority.`')


@bot.event
async def on_ready():
    global guild, channel

    guild = discord.utils.get(bot.guilds, name=GUILD)
    logging.info(
        f'{bot.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})\n'
    )

    channel = discord.utils.get(guild.channels, name=CHANNEL)
    print(f'{bot.user} is watching channel: {channel}')


@bot.command()
@commands.check(is_officer)
async def golemoff(ctx):
    global enabled, last_timestamp, last_user
    if not enabled:
        return
    enabled = False
    await ctx.send('`Shutting-doooowwwwwn....`')


@bot.command()
@commands.check(is_officer)
async def golemon(ctx):
    global enabled
    if enabled:
        return
    enabled = True
    await ctx.send('`*BZZZZZT!* Art-enforcement-golem-now-online--Beware-spammers-of-creativity`')


@bot.event
async def on_message(message):
    global last_timestamp, last_user
    if message.guild != guild or message.channel != channel:
        # Ignore everything outside of our targeted guild + channel.
        return
    if not message.embeds and not message.attachments:
        # No art here. Ignore comments.
        await bot.process_commands(message)
        return
    if (not last_timestamp
        or last_timestamp + timeout < message.created_at
        or last_user == message.author):
        # Legal. Update the info.
        last_user = message.author
        last_timestamp = message.created_at
    else:
        # Don't update the user or timestamp
        if enabled:
            logging.warning(f'Sending warning message to {message.author.name}')
            await message.author.send(f"`*BZZZT!*--Warning!-Courtesy-Infraction!-Please-wait-{minutes.minutes}-minutes-before-posting-art-after-someone-else!--Have-a-nice-day.`"
                                      "\n(This is an experimental golem created by Lagos. If you think this message is in error or if you find it obnoxious, please give feedback to them.)")
    await bot.process_commands(message)


bot.run(TOKEN)
