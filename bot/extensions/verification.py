from aiohttp import ClientSession
from discord import Member, Object, utils
from discord.ext import tasks
from discord.ext.commands import Bot, Cog, Context, command
from typing import List, Optional

from common import CONFIG, SETTINGS, ConfigKey
from .. import embeds
from ..logger import get as get_logger
from ..permissions import has_role

DESCRIPTION = (
    "Only allow participants registered in Hackathon Manager to view the full server"
)


class Verification(Cog):
    def __init__(self, bot: Bot):
        self.logger = get_logger("extensions.verification")
        self.bot = bot

        # Setup the HTTP session
        self.__session = ClientSession()
        self.__token: Optional[str] = None

        # Start the token refresher and manually call it once
        self.renew_token.start()

        self.logger.info("loaded verification commands")

    def cog_unload(self):
        # Close the session
        self.bot.loop.create_task(self.__shutdown_session())

        # Stop the refresher
        self.renew_token.stop()

        self.logger.info("unloaded verification commands")

    async def __shutdown_session(self):
        await self.__session.close()

    @tasks.loop(hours=1)
    async def renew_token(self):
        """
        Refresh the authentication token every hour
        """
        response = await self.__session.post(
            f"{SETTINGS.bot.hm_url}/oauth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": SETTINGS.bot.hm_client_id,
                "client_secret": SETTINGS.bot.hm_client_secret,
                "scope": "discord",
            },
        )

        if response.status != 200:
            self.logger.error(
                f"failed to renew token: ({response.status}) {await response.text()}"
            )
            self.__token = None
            return

        content = await response.json()
        self.__token = content.get("access_token")
        self.logger.debug("successfully renewed authentication token")

    async def list_usernames(self) -> List[str]:
        """
        Get a list of all the known usernames
        """
        if self.__token is None:
            await self.renew_token()

        response = await self.__session.get(
            f"{SETTINGS.bot.hm_url}/bot/discord.json",
            headers={"Authorization": f"Bearer {self.__token}"},
        )
        response.raise_for_status()

        return await response.json()

    async def username_exists(self, username: str) -> bool:
        """
        Check if a username is registered
        :param username: the full username to check
        """
        if self.__token is None:
            await self.renew_token()

        response = await self.__session.get(
            f"{SETTINGS.bot.hm_url}/bot/discord.json",
            params={"username": username},
            headers={"Authorization": f"Bearer {self.__token}"},
        )
        if response.status not in [204, 404]:
            response.raise_for_status()

        return response.status == 204

    @Cog.listener()
    async def on_member_join(self, member: Member):
        """
        Check if the user is already registered and admit them
        :param member: the member to check
        """
        role = Object(await CONFIG.registered_role())

        # Add the role to the user
        username = f"{member.name}#{member.discriminator}"
        if await self.username_exists(username):
            await member.add_roles(role)

    @command(name="re-verify")
    @has_role(ConfigKey.PanelAccessRole)
    async def re_verify(self, ctx: Context):
        """
        Re-verify every member currently in the server
        :param ctx: the command context
        """
        # Get the roles to ignore and the role to add/remove
        ignored = set(
            await CONFIG.get_multiple(
                ConfigKey.PanelAccessRole, ConfigKey.ManagementRole
            )
        )
        verified = Object(await CONFIG.registered_role())

        # Get all the known usernames
        usernames = await self.list_usernames()

        for user in ctx.guild.members:
            # Skip any bots
            if user.bot:
                continue

            # Ignore anyone with privileged roles
            roles = set(map(lambda r: r.id, user.roles))
            if len(roles & ignored) != 0:
                continue

            # Determine whether to add or remove the role
            if f"{user.name}#{user.discriminator}" in usernames:
                await user.add_roles(verified)
            else:
                await user.remove_roles(verified)


def setup(bot: Bot):
    """
    Register the cog
    :param bot: the underlying bot
    """
    bot.add_cog(Verification(bot))


def teardown(bot: Bot):
    """
    Unregister the cog
    :param bot: the underlying bot
    """
    bot.remove_cog("Verification")
