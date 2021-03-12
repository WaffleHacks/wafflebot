import sqlalchemy

# Enable auto-generation of migrations
metadata = sqlalchemy.MetaData()

# Users table
users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("email", sqlalchemy.String(256), nullable=False),
    sqlalchemy.Column("username", sqlalchemy.String(37), nullable=False),
    sqlalchemy.Column("avatar", sqlalchemy.Text, nullable=False),
    sqlalchemy.Column("has_panel", sqlalchemy.Boolean, default=False, nullable=False),
)

# Categories table
categories = sqlalchemy.Table(
    "categories",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("name", sqlalchemy.String(64), nullable=False),
)

# Tickets table
tickets = sqlalchemy.Table(
    "tickets",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column(
        "category_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("categories.id"),
        nullable=False,
    ),
    sqlalchemy.Column(
        "creator_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("users.id"),
        nullable=False,
    ),
    sqlalchemy.Column("is_open", sqlalchemy.Boolean, default=True, nullable=False),
    sqlalchemy.Column("reason", sqlalchemy.String(256), nullable=True),
)

# Messages table
messages = sqlalchemy.Table(
    "messages",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column(
        "ticket_id",
        sqlalchemy.Integer,
        sqlalchemy.ForeignKey("tickets.id"),
        nullable=False,
    ),
    sqlalchemy.Column("sender_id", sqlalchemy.ForeignKey("users.id"), nullable=False),
    sqlalchemy.Column("is_reaction", sqlalchemy.Boolean, nullable=False),
    sqlalchemy.Column("content", sqlalchemy.Text, nullable=False),
)
