from aiohttp import ClientConnectionError, ClientSession
from asyncio import TimeoutError
from discord import Message
from discord.ext.commands import Bot, Cog, command, Context
import json
from typing import Any, Dict, Tuple

from common import SETTINGS
from ..logger import get as get_logger
from ..permissions import has_role, ConfigKey

DESCRIPTION = "Register for WaffleHacks services"


def not_from_bot(message: Message):
    """
    Check that a message is not from the bot
    :param message: the message to check
    """
    return not message.author.bot


class Registration(Cog):
    def __init__(self, bot: Bot):
        self.logger = get_logger("extensions.registration")
        self.bot = bot

        # Load the configuration
        try:
            self.__services = json.load(open(SETTINGS.bot.registration_config, "r"))
            self.__services_list = set(self.__services)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.error(f"failed to load registration configuration: {e}")

            # Disable self on error
            self.bot.remove_cog("Registration")
            return

        # Setup the request session
        self.__session = ClientSession()

        self.logger.info("loaded registration commands")

    async def __shutdown_session(self):
        await self.__session.close()

    def cog_unload(self):
        # Close the session
        self.bot.loop.create_task(self.__shutdown_session())

        self.logger.info("unloaded registration commands")

    async def send_request(self, url, **kwargs) -> Tuple[int, Dict[str, Any]]:
        """
        Send the request to the API
        :param url: the url to send to
        :param kwargs: arguments to be passed to aiohttp
        :return: the response content and status code
        """
        # Attempt to send the request
        try:
            response = await self.__session.post(url, **kwargs)
        except ClientConnectionError as e:
            self.logger.error(f"failed to connect to URL: {e}")
            return 500, {"success": False, "reason": "failed to connect to URL"}

        # Parse the response body
        parsed = await response.json()
        return response.status, parsed

    @command()
    @has_role(ConfigKey.PanelAccessRole)
    async def register(self, ctx: Context, service: str):
        """
        Register the requester with the specified service
        :param ctx: the command context
        :param service: the service's name
        """
        service = service.lower()

        # Ensure service exists
        if service not in self.__services:
            formatted = ", ".join(map(lambda s: "`" + s + "`", self.__services_list))
            await ctx.channel.send(
                f"The service `{service}` does not exist. Possible services are: {formatted}"
            )
            return

        config = self.__services[service]
        await ctx.author.send(
            f"Beginning registration process for `{service}`."
            f" You can cancel the process at any time by typing `cancel`."
        )

        # Prompt the user for each required field
        fields = {}
        for field in config["fields"]:
            await ctx.author.send(
                f"Please send your preferred {field.replace('-', ' ').replace('_', ' ')}:"
            )

            # Wait for the user's response for 5 minutes
            try:
                message = await self.bot.wait_for(
                    "message", check=not_from_bot, timeout=60 * 5
                )
            except TimeoutError:
                await ctx.author.send(
                    "No response in 5 minutes; cancelling registration."
                )
                return

            # Allow cancelling
            if message.content.lower() == "cancel":
                await ctx.author.send(f"Cancelled registration for `{service}`.")
                return

            fields[field] = message.content

        # Send the request
        params = {"params": {"token": config["token"]}, config["format"]: fields}
        status, response = await self.send_request(config["url"], **params)

        # Respond based on the status
        if status == 401:
            await ctx.author.send(
                f"Failed to register for `{service}`, configuration is invalid."
            )
            self.logger.error(f"invalid configuration for service `{service}`")
        elif status != 200:
            await ctx.author.send(
                f"Failed to register for `{service}`, {response['reason']}"
            )
        else:
            extra = (
                ""
                if response.get("url") is None
                else f" Complete your registration: {response['url']}."
            )
            await ctx.author.send(f"Successfully registered for `{service}`.{extra}")


def setup(bot: Bot):
    """
    Register the cog
    :param bot: the underlying bot
    """
    bot.add_cog(Registration(bot))


def teardown(bot: Bot):
    """
    Unregister the cog
    :param bot: the underlying bot
    """
    bot.remove_cog("Registration")
