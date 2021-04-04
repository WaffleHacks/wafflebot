import asyncio
import signal
import sys

from common import CONFIG, SETTINGS
from . import logger
from .bot import bot


# From https://github.com/Rapptz/discord.py/blob/master/discord/client.py#L59-L86
def cancel_tasks(loop: asyncio.AbstractEventLoop):
    # Get all the tasks
    try:
        task_retriever = asyncio.Task.all_tasks
    except AttributeError:
        task_retriever = asyncio.all_tasks
    tasks = {t for t in task_retriever(loop=loop) if not t.done()}

    if not tasks:
        return

    # Cancel the tasks
    for task in tasks:
        task.cancel()

    # Wait until tasks are completed
    loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

    # Ensure all tasks canceled gracefully
    for task in tasks:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "Unhandled exception during shutdown",
                    "exception": task.exception(),
                    "task": task,
                }
            )


# Equivalent to https://github.com/Rapptz/discord.py/blob/master/discord/client.py#L665-L723
def start_bot(loop: asyncio.AbstractEventLoop):
    """
    Run the bot
    This is almost identical to the Discord.py implementation of Bot.run
    except that it does not close the event loop
    """

    async def runner():
        try:
            # Run the bot
            await bot.start(SETTINGS.discord_token)
        finally:
            # Close the bot if not already done
            if not bot.is_closed():
                await bot.close()

    def stop_loop_on_completion(_):
        loop.stop()

    # Register signal handlers
    try:
        loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
        loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
    except NotImplementedError:
        pass

    # Start the bot
    future = asyncio.ensure_future(runner(), loop=loop)
    future.add_done_callback(stop_loop_on_completion)

    # Run until complete
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.get().info("Received signal to terminate bot")
    finally:
        future.remove_done_callback(stop_loop_on_completion)
        logger.get().info("Cleaning up tasks")
        cancel_tasks(loop)

    if not future.cancelled():
        try:
            return future.result()
        except KeyboardInterrupt:
            return None


def main():
    """
    The entrypoint for the bot
    """
    loop = asyncio.get_event_loop()
    logger.get().info("starting bot")

    # Connect to Redis
    loop.run_until_complete(CONFIG.connect())
    logger.get().info("connected to redis")

    # Run the bot
    start_bot(loop)

    logger.get().info("bot exited gracefully. good bye!")

    # Disconnect from Redis
    loop.run_until_complete(CONFIG.disconnect())
    logger.get().info("disconnected from redis")

    # Shutdown the event loop and cleanup tasks
    # From https://github.com/Rapptz/discord.py/blob/master/discord/client.py#L88-L95
    try:
        # Cancel the remaining tasks
        cancel_tasks(loop)

        # Stop async generators
        if sys.version_info >= (3, 6):
            loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        loop.close()


if __name__ == "__main__":
    main()
