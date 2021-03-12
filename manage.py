from alembic import command
from alembic.config import Config
from alembic.util import CommandError
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from dotenv import load_dotenv
import importlib
from os import environ
from typing import Optional

# Load from environment file
load_dotenv()


def run(app: str, **_):
    # Load the service module
    module = importlib.import_module(app)

    try:
        # Ensure the runner function exists
        run_fn = getattr(module, "run")
        run_fn()
    except AttributeError:
        print(f"Could not find 'run' function in '{app}'")


def migrations(action: str, database: str, revision: Optional[str], **_):
    if database == "":
        print("A database must be specified")
        return

    cfg = Config("./alembic.ini")
    cfg.attributes["sqlalchemy.url"] = database

    try:
        if action == "run":
            command.upgrade(cfg, "head" if revision is None else revision)
        elif action == "reset":
            command.downgrade(cfg, "base" if revision is None else revision)
        elif action == "status":
            command.current(cfg)
    except CommandError as e:
        print(f"Failed to run command: {e}")


# Instantiate the argument parser
parser = ArgumentParser(
    description="WaffleBot management commands",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
subparsers = parser.add_subparsers(
    dest="subcommand", help="Subcommands:", required=True
)
runner = subparsers.add_parser("run", help="Run one of the sections")
runner.add_argument(
    "app",
    metavar="APP",
    choices=["api", "bot", "frontend"],
    help="Run the frontend, api, or Discord bot",
)
migrator = subparsers.add_parser("migrations", help="Interact with migrations")
migrator.add_argument(
    "action",
    metavar="ACTION",
    choices=["run", "reset", "status"],
    help="Run, reset, or get the current status of the migrations",
)
migrator.add_argument(
    "-d",
    "--database",
    type=str,
    action="store",
    default=environ.get("DATABASE_URL", ""),
    help="The database to connect to",
)
migrator.add_argument(
    "-r",
    "--revision",
    type=str,
    action="store",
    default=None,
    help="The revision to run or reset to",
)

# Parse the arguments
args = parser.parse_args()
args_dict = vars(args)

# Run the subcommand
{"run": run, "migrations": migrations}[args.subcommand](**args_dict)
