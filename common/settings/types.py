from pydantic import AnyUrl, PostgresDsn
from typing import Union


class SqliteDsn(AnyUrl):
    allowed_schemes = {"sqlite", "sqlite3"}


DatabaseUrl = Union[PostgresDsn, SqliteDsn]
