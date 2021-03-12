import databases

from common import SETTINGS

db = databases.Database(SETTINGS.database_url)
