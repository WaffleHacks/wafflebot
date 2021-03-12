import databases
from dotenv import load_dotenv
from os import environ

# TODO: pull database URL from settings module
load_dotenv()

db = databases.Database(environ.get("DATABASE_URL", ""))
