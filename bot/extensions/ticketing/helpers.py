from discord import utils, CategoryChannel, Member
from sqlalchemy.exc import IntegrityError
from typing import List, Optional

from common import CONFIG, ConfigKey
from common.database import db_context, User


async def create_user_if_not_exists(member: Member) -> User:
    """
    Add the user to the database if they don't exist
    :param member: the member
    :return:
    """
    async with db_context() as db:
        # Construct the user
        user = User(
            id=member.id,
            username=f"{member.name}#{member.discriminator}",
            avatar=str(member.avatar_url),
            # TODO: determine if they have panel access
            has_panel=True,
        )
        db.add(user)

        # Save the user, ignoring any users that already exist
        try:
            await db.commit()
        except IntegrityError:
            pass

        return user


async def get_channel_category(
    categories: List[CategoryChannel],
) -> Optional[CategoryChannel]:
    """
    Get the channel category for the guild
    :param categories: all the channel categories
    """
    # Get the channel category id
    category_id = await CONFIG.ticket_category()

    # Get the channel category
    return utils.get(categories, id=category_id)


async def get_ticket_roles() -> List[int]:
    """
    Get a list of the roles that can view a ticket
    """
    return await CONFIG.get_multiple(ConfigKey.MentionRoles, ConfigKey.PanelAccessRole)
