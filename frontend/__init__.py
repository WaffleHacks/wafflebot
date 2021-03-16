import os
from pathlib import Path
import subprocess


def run():
    """
    Run the frontend development server
    """
    print("Running frontend dev server")

    # Enter the frontend directory
    os.chdir(Path(__file__).parent)

    # Start the development server
    try:
        subprocess.Popen("yarn dev", shell=True).communicate()
    except KeyboardInterrupt:
        pass
