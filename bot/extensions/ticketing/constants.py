from discord import PermissionOverwrite

TICKET_PERMISSIONS = PermissionOverwrite(
    view_channel=True,
    read_messages=True,
    read_message_history=True,
    send_messages=True,
    add_reactions=True,
)

NO_PERMISSIONS = PermissionOverwrite(view_channel=False)
