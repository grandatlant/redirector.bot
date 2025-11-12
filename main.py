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

from __future__ import annotations

import os
import sys
import logging
import asyncio

from typing import (
    Optional,
    Union,
    List,
)

import telegram
import discord
from discord.ext.commands import Bot as DiscordBot
from dotenv import load_dotenv

load_dotenv()

LOG_LEVEL: Union[str, int] = os.getenv('LOG_LEVEL') or (
    logging.DEBUG if __debug__ else logging.INFO
)
LOG_FORMAT: str = (
    os.getenv('LOG_FORMAT') or '%(levelname)s:%(name)s:%(message)s'
)

log: logging.Logger = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

DISCORD_TOKEN: str = os.getenv('DISCORD_TOKEN') or 'No-Token'
DISCORD_COMMAND_PREFIX: str = os.getenv('DISCORD_COMMAND_PREFIX') or '!'
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

TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN') or 'No-Token'
TELEGRAM_CHAT_ID: int = int(os.getenv('TELEGRAM_CHAT_ID') or 0)

intents: discord.Intents = discord.Intents.default()
intents.message_content = True
dc_bot: DiscordBot = DiscordBot(
    command_prefix=DISCORD_COMMAND_PREFIX,
    intents=intents,
)


async def transfer_message(message: str) -> None:
    log.debug('%s.transfer_message(%r) call.', __name__, message)
    async with telegram.Bot(token=TELEGRAM_TOKEN) as tg_bot:
        await tg_bot.send_message(TELEGRAM_CHAT_ID, message)


@dc_bot.event
async def on_ready() -> None:
    # log.debug('dc_bot.on_ready() call.')
    log.info('Logged in as %s.', dc_bot.user)


@dc_bot.event
async def on_message(message: discord.Message) -> None:
    log.debug('dc_bot.on_message(%r) call.', message)
    if message.author == dc_bot.user or message.guild is None:
        # Ignore made by bot and private messages
        return

    tasks: List[asyncio.Future] = [
        asyncio.create_task(dc_bot.process_commands(message))
    ]

    if message.channel.id in DISCORD_CHANNEL_IDS:
        author_ok: bool = not DISCORD_ALLOWED_AUTHOR_IDS or (
            message.author.id in DISCORD_ALLOWED_AUTHOR_IDS
        )
        mention_ok: bool = not DISCORD_ALLOWED_MENTION_IDS or any(
            user.id in DISCORD_ALLOWED_MENTION_IDS for user in message.mentions
        )

        if author_ok and mention_ok:
            # Form and transfer message in new async task
            guild: str = message.guild.name
            channel: str = getattr(message.channel, 'name', 'Unknown channel')

            author: str = message.author.display_name
            content: str = message.clean_content

            text: str = f'{guild}.{channel}: {author}: {content}'

            log.info('--> Text for transfer: %r.', text)

            tasks.append(asyncio.create_task(transfer_message(text)))

    await asyncio.gather(*tasks)


##  MAIN ENTRY POINT
def main(args: Optional[List[str]] = None) -> None:
    logging.basicConfig(
        level=LOG_LEVEL,
        stream=sys.stdout,
        format=LOG_FORMAT,
    )
    log.debug('Running %s on %s', sys.version, sys.platform)

    if args is None:
        args = sys.argv[1:]
    token: str = args[0] if args else DISCORD_TOKEN
    dc_bot.run(token)


if __name__ == '__main__':
    sys.exit(main())
