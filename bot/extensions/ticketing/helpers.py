from discord import utils, CategoryChannel, Member
from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select
from typing import List, Optional

from common.database import get_db, Setting, SettingsKey, User


async def create_user_if_not_exists(member: Member) -> User:
    """
    Add the user to the database if they don't exist
    :param member: the member
    :return:
    """
    async with get_db() as db:
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
    async with get_db() as db:
        statement = select(Setting.value).where(
            Setting.key == SettingsKey.TicketCategory
        )
        result = await db.execute(statement)
    category_id = int(result.scalars().first())

    # Get the channel category
    return utils.get(categories, id=category_id)


async def get_ticket_roles() -> List[Setting]:
    """
    Get a list of the roles that can view a ticket
    """
    async with get_db() as db:
        statement = select(Setting).where(
            Setting.key.in_([SettingsKey.PanelAccessRole, SettingsKey.MentionRole])
        )
        result = await db.execute(statement)
        return result.scalars().all()
