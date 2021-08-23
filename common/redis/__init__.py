from typing import Optional

from .kv import KV, Key


NOT_CONNECTED_ERROR = RuntimeError(
    "connect() must be called before interacting with Redis"
)


class Redis(object):
    def __init__(self, redis_url: str):
        self.__url = redis_url
        self.__kv: Optional[KV] = None

    async def connect(self):
        """
        Connect the underlying services
        """
        self.__kv = await KV.connect(self.__url)

    async def disconnect(self):
        """
        Disconnect from the underlying services
        """
        await self.__kv.disconnect()

    @property
    def kv(self) -> KV:
        if self.__kv is None:
            raise NOT_CONNECTED_ERROR
        return self.__kv
