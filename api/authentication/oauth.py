from authlib.integrations.starlette_client import OAuth
from starlette.config import Config, environ
from typing import Dict

from common import SETTINGS


async def normalize_userinfo(_client, data: Dict[str, str]) -> Dict[str, str]:
    # Remap the user info
    params = {
        "id": data["id"],
        "username": data["username"] + "#" + data["discriminator"],
    }

    # Make the avatar a full URL if provided
    if "avatar" in data:
        params[
            "picture"
        ] = f"https://cdn.discordapp.com/avatars/{data['id']}/{data['avatar']}.png"

    return params


# And remap the configuration to be compatible with Starlette
environ["DISCORD_CLIENT_ID"] = SETTINGS.api.discord_client_id
environ["DISCORD_CLIENT_SECRET"] = SETTINGS.api.discord_client_secret
config = Config(".env")

# Register the discord auth provider
oauth = OAuth(config)
oauth.register(
    "discord",
    api_base_url="https://discord.com/api/",
    access_token_url="https://discord.com/api/oauth2/token",
    authorize_url="https://discord.com/api/oauth2/authorize",
    userinfo_endpoint="https://discord.com/api/users/%40me",
    userinfo_compliance_fix=normalize_userinfo,
    client_kwargs={
        "token_endpoint_auth_method": "client_secret_post",
        "scope": "identify guilds",
    },
)


def get_discord_client():
    """
    Get a Discord OAuth2 client
    """
    return oauth.create_client("discord")
