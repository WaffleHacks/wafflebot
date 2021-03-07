from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import importlib


def run(app: str, **_):
    # Load the service module
    module = importlib.import_module(app)

    try:
        # Ensure the runner function exists
        run_fn = getattr(module, "run")
        run_fn()
    except AttributeError:
        print(f"Could not find 'run' function in '{app}'")


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

# Parse the arguments
args = parser.parse_args()
args_dict = vars(args)

# Run the subcommand
{"run": run}[args.subcommand](**args_dict)
