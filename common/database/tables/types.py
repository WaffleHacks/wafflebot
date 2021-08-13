from datetime import datetime, timezone
import sqlalchemy
from sqlalchemy.types import TypeDecorator


# From https://mike.depalatis.net/blog/sqlalchemy-timestamps.html
class TimeStamp(TypeDecorator):
    impl = sqlalchemy.DateTime
    cache_ok = True
    LOCAL_TIMEZONE = datetime.now().astimezone().tzinfo

    def process_bind_param(self, value: datetime, dialect):
        if value.tzinfo is None:
            value = value.astimezone(self.LOCAL_TIMEZONE)

        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)
