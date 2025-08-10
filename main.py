#!/usr/bin/env -S python3 -O
# -*- coding = utf-8 -*-
"""bridgebot main script.
"""

import sys
import asyncio

# pip install discord.py python-telegram-bot
import telegram
import discord
from discord.ext.commands import Bot as DiscordBot

# pip install python-dotenv
from dotenv import dotenv_values
_env = dotenv_values()

import logging
logging.basicConfig(
    level = logging.DEBUG if __debug__ else logging.INFO,
    stream = sys.stdout,
    style = '{',
    format = '{levelname}:{name}:{message}',
)
log = logging.getLogger(__name__)

DISCORD_TOKEN = _env.get('DISCORD_TOKEN') or 'No-Token'
DISCORD_CHANNEL_IDS = [
    int(i)
    for i in (_env.get('DISCORD_CHANNEL_IDS') or '').split(',')
    if i
]
# Additional filters. Disabled if (False)
ALLOWED_MENTION_IDS = []
ALLOWED_AUTHOR_IDS = []

TELEGRAM_TOKEN = _env.get('TELEGRAM_TOKEN') or 'No-Token'
TELEGRAM_CHAT_ID = int(_env.get('TELEGRAM_CHAT_ID') or 0)

intents = discord.Intents.default()
intents.message_content = True
dc_bot = DiscordBot(command_prefix='!', intents=intents)

tg_bot = telegram.Bot(token=TELEGRAM_TOKEN)


async def transfer_message(message: str):
    #await tg_bot.send_message(TELEGRAM_CHAT_ID, message)
    #'''
    await asyncio.get_running_loop().run_in_executor(
        None,
        tg_bot.send_message,
        TELEGRAM_CHAT_ID,
        message,
    )
    #'''


@dc_bot.event
async def on_ready():
    log.info('Logged in as %s', dc_bot.user)


@dc_bot.event
async def on_message(message: discord.Message):

    if message.author == dc_bot.user or message.guild is None:
        # Ignore made by bot and private messages
        return
    
    if message.channel.id in DISCORD_CHANNEL_IDS:
        
        mention_ok = not ALLOWED_MENTION_IDS or any(
            user.id in ALLOWED_MENTION_IDS
            for user in message.mentions
        )
        author_ok = not ALLOWED_AUTHOR_IDS or (
            message.author.id in ALLOWED_AUTHOR_IDS
        )

        if mention_ok or author_ok:
            guild = message.guild.name
            channel = message.channel.name # pyright: ignore[reportAttributeAccessIssue]
            author = message.author.display_name
            content = message.content
            text = f'{guild}.{channel}: {author}: {content}'
            log.info('Got message: %s', text)
            #await transfer_message(text)

    await dc_bot.process_commands(message)


##  MAIN ENTRY POINT
def main(args=None):
    token = DISCORD_TOKEN
    if args and len(args) == 2:
        token = args[1]
    dc_bot.run(token)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
