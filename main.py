#!/usr/bin/env -S python3 -O
# -*- coding: utf-8 -*-
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "python-dotenv",
#   "discord.py",
#   "python-telegram-bot",
# ]
# ///
"""redirector.bot main script."""

import os
import sys
import logging
import asyncio

from typing import (
    List,
)

import telegram
import discord
from discord.ext.commands import Bot as DiscordBot
from dotenv import load_dotenv

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG if __debug__ else logging.INFO)

try:
    load_dotenv()
except Exception as ecx:
    log.exception('Error occured in load_dotenv(): %r.', exc)

LOG_FORMAT = os.getenv('LOG_FORMAT') or '%(levelname)s:%(name)s:%(message)s'

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN') or 'No-Token'
DISCORD_COMMAND_PREFIX = os.getenv('DISCORD_COMMAND_PREFIX') or '!'
DISCORD_CHANNEL_IDS: List[int] = [
    int(i.strip())
    for i in (os.getenv('DISCORD_CHANNEL_IDS') or '').split(',')
    if i.strip()
]
# Additional filters. Disabled if empty
DISCORD_ALLOWED_AUTHOR_IDS: List[int] = [
    int(i.strip())
    for i in (os.getenv('DISCORD_ALLOWED_AUTHOR_IDS') or '').split(',')
    if i.strip()
]
DISCORD_ALLOWED_MENTION_IDS: List[int] = [
    int(i.strip())
    for i in (os.getenv('DISCORD_ALLOWED_MENTION_IDS') or '').split(',')
    if i.strip()
]

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN') or 'No-Token'
TELEGRAM_CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID') or 0)

intents = discord.Intents.default()
intents.message_content = True
dc_bot = DiscordBot(command_prefix=DISCORD_COMMAND_PREFIX, intents=intents)

tg_bot = telegram.Bot(token=TELEGRAM_TOKEN)


async def transfer_message(message: str):
    log.info('Transferring message %r...', message)
    await tg_bot.send_message(TELEGRAM_CHAT_ID, message)


@dc_bot.event
async def on_ready():
    log.info('Logged in as %s.', dc_bot.user)


@dc_bot.event
async def on_message(message: discord.Message):
    if message.author == dc_bot.user or message.guild is None:
        # Ignore made by bot and private messages
        return

    tasks = [asyncio.create_task(dc_bot.process_commands(message))]

    if message.channel.id in DISCORD_CHANNEL_IDS:
        author_ok = not ALLOWED_AUTHOR_IDS or (
            message.author.id in ALLOWED_AUTHOR_IDS
        )
        mention_ok = not ALLOWED_MENTION_IDS or any(
            user.id in ALLOWED_MENTION_IDS for user in message.mentions
        )

        if author_ok and mention_ok:
            # Form and transfer message in new async task
            guild = message.guild.name
            channel = message.channel.name  # pyright: ignore[reportAttributeAccessIssue]
            author = message.author.display_name
            content = message.content
            text = f'{guild}.{channel}: {author}: {content}'

            log.debug('Got message: %r.', text)
            # tasks.append(asyncio.create_task(transfer_message(text)))

    await asyncio.gather(*tasks)


##  MAIN ENTRY POINT
def main(args=None):
    logging.basicConfig(
        level=logging.DEBUG if __debug__ else logging.INFO,
        stream=sys.stdout,
        format=LOG_FORMAT,
    )
    log.debug('Running %s on %s', sys.version, sys.platform)

    args = sys.argv[1:] if args is None else args
    token = args[0] if args else DISCORD_TOKEN
    dc_bot.run(token)


if __name__ == '__main__':
    sys.exit(main())
