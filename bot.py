r"""Redirector.Bot control module.

Contains single Discord Bot instance with necessary interface methods and data.
"""

from __future__ import annotations

import os
import logging
import asyncio
import collections

from typing import (
    Any,
    TypeVar,
    Callable,
    Iterable,
    Coroutine,
)

import discord
from discord.ext.commands import Bot as DiscordBot
from dotenv import load_dotenv

load_dotenv()

log: logging.Logger = logging.getLogger(__name__)
log.setLevel(os.getenv('LOG_LEVEL') or logging.WARNING)

T = TypeVar('T')
Coro = Coroutine[Any, Any, T]
CoroT = TypeVar('CoroT', bound=Callable[..., Coro[Any]])
ReceiverT = TypeVar('ReceiverT', bound=Callable[[str], Any])

DISCORD_CHANNEL_IDS: list[int] = [
    int(i.strip())
    for i in (os.getenv('DISCORD_CHANNEL_IDS') or '').split(',')
    if i.strip()
]

# Additional filters. Disabled if empty
DISCORD_ALLOWED_AUTHOR_IDS: list[int] = [
    int(i.strip())
    for i in (os.getenv('DISCORD_ALLOWED_AUTHOR_IDS') or '').split(',')
    if i.strip()
]
DISCORD_ALLOWED_MENTION_IDS: list[int] = [
    int(i.strip())
    for i in (os.getenv('DISCORD_ALLOWED_MENTION_IDS') or '').split(',')
    if i.strip()
]


# Global instance setup


class Bot(DiscordBot):
    pass


defaults: dict[str, Any] = {
    'command_prefix': os.getenv('DISCORD_COMMAND_PREFIX') or '!',
    'intents': (
        discord.Intents(int(os.getenv('DISCORD_INTENTS') or '0', base=0))
        or discord.Intents.default()
    ),
}
defaults['intents'].message_content = True


instance: Bot | None = Bot(**defaults)


# Bot events stored here to apply in recreate() call.
events: list[CoroT] = []


def event(coro: CoroT) -> CoroT:
    """Decorator for registering new bot event handler coroutine."""
    events.append(coro)
    if instance is not None:
        # register it for instance
        return instance.event(coro)
    return coro


def register_events(
    extend_events: Iterable[CoroT] | None = None,
) -> list[CoroT]:
    """Register global events, extended with extend_register if not None.

    Return value: all events list.
    """
    events.extend(extend_events or [])
    for event in events:
        instance.event(event)
    return events


# Bot message receivers stored here to iterate in transfer_message() call.
receivers: list[ReceiverT] = []


def receiver(func: ReceiverT) -> ReceiverT:
    """Decorator for registering new text message receiver callable."""
    receivers.append(func)
    return func


def add_receivers(
    extend_receivers: Iterable[ReceiverT] | None = None,
) -> list[ReceiverT]:
    """Add more text message receivers for bot.

    Return value: all receivers list.
    """
    receivers.extend(extend_receivers or [])
    return receivers


@event
async def on_ready() -> None:
    log.debug('instance.on_ready() call.')
    log.info('Logged in as %s.', instance.user)


@event
async def on_message(message: discord.Message) -> None:
    log.debug('instance.on_message(%r) call.', message)
    if message.author == instance.user or message.guild is None:
        # Ignore made by bot and private messages
        return

    async with asyncio.TaskGroup() as tasks:
        tasks.create_task(instance.process_commands(message))

        if should_transfer_message(message):
            # Form and transfer message in new async task
            text = get_message_text(message)
            log.info('--> Transfering message: %r. <--', text)
            tasks.create_task(transfer_text_message(text))
        else:
            log.debug(
                '--> Message ignored: %r. <--',
                get_message_text(message),
            )


def should_transfer_message(message: discord.Message) -> bool:
    if message.channel.id in DISCORD_CHANNEL_IDS:
        author_ok: bool = not DISCORD_ALLOWED_AUTHOR_IDS or (
            message.author.id in DISCORD_ALLOWED_AUTHOR_IDS
        )
        mention_ok: bool = not DISCORD_ALLOWED_MENTION_IDS or any(
            user.id in DISCORD_ALLOWED_MENTION_IDS for user in message.mentions
        )
        if author_ok or mention_ok:
            return True
    return False


def get_message_text(message: discord.Message) -> str:
    guild: str = message.guild.name
    channel: str = getattr(message.channel, 'name', 'Unknown channel')

    author: str = message.author.display_name
    content: str = message.clean_content

    return f'{guild}.{channel}: {author}: {content}'


async def transfer_text_message(text: str) -> None:
    async with asyncio.TaskGroup() as tasks:
        for receiver in receivers:
            if asyncio.iscoroutinefunction(receiver):
                tasks.create_task(receiver(text))
            else:
                tasks.create_task(asyncio.to_thread(receiver, text))


# Redirect unknown requests to instance object.
def __getattr__(name, *args, **kwargs):
    return getattr(instance, name, *args, **kwargs)


def recreate(*args, **kwargs) -> Bot:
    """Recreate bot instance.

    Return value: Bot instance itself.
    """
    global instance
    log.debug(
        '%s.recreate(*%r, **%r) call with last instance value %r.',
        __name__,
        args,
        kwargs,
        instance,
    )

    instance = Bot(*args, **collections.ChainMap(kwargs, defaults))
    register_events()

    log.debug('New instance recreated: %r.', instance)
    return instance


def main(*args, **kwargs) -> None:
    log.debug('%s.main(*%r, **%r) call.', __name__, args, kwargs)
    instance.run(
        token=os.getenv('DISCORD_TOKEN') or 'DISCORD_TOKEN',
        *args,
        **kwargs,
    )


if instance is None:
    # Init with default values before possible use.
    recreate()


if __name__ == '__main__':
    main()
