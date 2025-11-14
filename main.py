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

import telegram
from dotenv import load_dotenv

import bot

load_dotenv()


LOG_LEVEL: str | int = os.getenv('LOG_LEVEL') or (
    logging.DEBUG if __debug__ else logging.INFO
)
LOG_FORMAT: str = (
    os.getenv('LOG_FORMAT') or '%(levelname)s:%(name)s:%(message)s'
)
log: logging.Logger = logging.getLogger(__name__)
log.setLevel(LOG_LEVEL)

DISCORD_TOKEN: str = os.getenv('DISCORD_TOKEN') or 'No-Token'
TELEGRAM_TOKEN: str = os.getenv('TELEGRAM_TOKEN') or 'No-Token'
TELEGRAM_CHAT_ID: int = int(os.getenv('TELEGRAM_CHAT_ID') or 0)


@bot.receiver
async def telegram_send(message: str) -> None:
    log.debug('%s.telegram_send(%r) call.', __name__, message)
    async with telegram.Bot(token=TELEGRAM_TOKEN) as tg_bot:
        await tg_bot.send_message(TELEGRAM_CHAT_ID, message)


##  MAIN ENTRY POINT
def main(args: list[str] | None = None) -> None:
    logging.basicConfig(
        level=LOG_LEVEL,
        stream=sys.stdout,
        format=LOG_FORMAT,
    )
    log.debug('Running %s on %s', sys.version, sys.platform)

    if args is None:
        args = sys.argv[1:]
    token: str = args[0] if args else DISCORD_TOKEN
    bot.run(token)


if __name__ == '__main__':
    sys.exit(main())
