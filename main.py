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



##  MAIN ASYNC ENTRY POINT
async def amain(args=None):
    log.debug('amain args = %s', args)
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
