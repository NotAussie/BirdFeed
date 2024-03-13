import asyncio


def startup():
    def decorator(func):
        async def wrapper(*args, **kwargs):
            await func(*args, **kwargs)

        # Start the task immediately upon decoration
        eventLoop = asyncio.get_event_loop()
        eventLoop.create_task(wrapper())

        return wrapper

    return decorator


def periodic(interval_seconds: float, start_up_wait: float = 0):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            await asyncio.sleep(start_up_wait)

            while True:
                await func(*args, **kwargs)
                await asyncio.sleep(interval_seconds)

        # Start the task immediately upon decoration
        eventLoop = asyncio.get_event_loop()
        eventLoop.create_task(wrapper())

        return wrapper

    return decorator
