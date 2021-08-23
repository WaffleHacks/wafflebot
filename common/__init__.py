from .redis import Redis, Key
from .settings import load_settings

# Settings vs Config
# - Settings is loaded on startup from the environment variables
# - Config is retrieved at runtime from Redis
#   (this data was previously stored in PostgreSQL in the settings table)
#
# Config should be used for data that can change during runtime and needs
# to be accessed frequently.

SETTINGS = load_settings()
REDIS = Redis(SETTINGS.redis_url)
