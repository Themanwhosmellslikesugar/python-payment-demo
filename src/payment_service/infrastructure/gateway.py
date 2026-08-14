"""Эмуляция внешнего платёжного шлюза."""

import asyncio
import random

_SUCCESS_RATE = 0.9
_MIN_DELAY = 2.0
_MAX_DELAY = 5.0


async def emulate_processing() -> bool:
    """Эмулировать обработку платежа: 2-5 секунд, 90% успех."""
    await asyncio.sleep(random.uniform(_MIN_DELAY, _MAX_DELAY))  # noqa: S311
    return random.random() < _SUCCESS_RATE  # noqa: S311
