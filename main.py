#!/usr/bin/env -S python3 -O
# -*- coding = utf-8 -*-
"""bridgebot main script.
"""

import sys
import asyncio

import logging
logging.basicConfig(
    level = logging.DEBUG if __debug__ else logging.INFO,
    stream = sys.stdout,
    style = '{',
    format = '{levelname}:{name}:{message}',
)
log = logging.getLogger(__name__)

# pip install discord.py python-telegram-bot
from discord.ext import commands
from telegram import Bot as TgBot

# Налаштування
DISCORD_TOKEN = 'your_discord_token'
DISCORD_CHANNEL_IDS = [1234567890, 2345678901]  # id каналів для відстеження
TELEGRAM_TOKEN = 'your_telegram_token'
TELEGRAM_CHAT_ID = 123456789  # id чату/каналу куди надсилати

# Telegram бот (простий інтерфейс)
tg_bot = TgBot(token=TELEGRAM_TOKEN)

# Discord бот
intents = commands.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged as {bot.user}')


@bot.event
async def on_message(message):
    # Ігноруємо приватні повідомлення та свої власні
    if message.author == bot.user or message.guild is None:
        return

    if message.channel.id in DISCORD_CHANNEL_IDS:
        # Фільтрація за згадуваннями
        mention_ok = any(user.id in ALLOWED_MENTION_IDS for user in message.mentions)
        # Фільтрація за авторами
        author_ok = message.author.id in ALLOWED_AUTHOR_IDS

        if mention_ok or author_ok:
            text = f'**{message.author.display_name}**: {message.content}'
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, tg_bot.send_message, TELEGRAM_CHAT_ID, text)

    await bot.process_commands(message)


##  MAIN ASYNC ENTRY POINT
async def amain(args=None):
    log.debug('amain args = %s', args)
    bot.run(DISCORD_TOKEN)
    pass


##  MAIN ENTRY POINT
def main(args=None):
    log.debug('main args = %s', args)
    try:
        asyncio.run(amain(args))
    except Exception as ex:
        log.fatal('Unhandled exception "%s" during asyncio.run execution.', ex)
        return ex
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
