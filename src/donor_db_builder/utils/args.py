from __future__ import annotations

from argparse import ArgumentParser, Namespace
from typing import Literal, TypeAlias

from donor_db_builder import __application_title__, __application_binary__, __version__


def get_args() -> Namespace:
    """Parse and return the command line arguments.

    Returns:
            The result of parsing the arguments.
    """

    # Create the parser object.
    parser = ArgumentParser(
        prog=__application_binary__,
        description=f"{__application_title__} -- Donor DB Builder.",
        epilog=f"v{__version__}",
    )

    # Add --version
    parser.add_argument(
        "-v",
        "--version",
        help="Show version information.",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "-d",
        "--data-dir",
        help="Data Directory. Defaults to ~/.raising",
    )

    parser.add_argument(
        "-s",
        "--starting-tab",
        help="Starting tab. Defaults to local",
        # choices=[s.lower() for s in valid_tabs],
    )

    parser.add_argument("-t", "--theme-name", help="Theme name. Defaults to par")
    parser.add_argument(
        "-m",
        "--theme-mode",
        help="Dark / Light mode. Defaults to dark",
        choices=["dark", "light"],
    )

    parser.add_argument(
        "--no-save",
        help="Prevent saving settings for this session",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "--no-chat-save",
        help="Prevent saving chats for this session",
        default=False,
        action="store_true",
    )

    # Finally, parse the command line.
    return parser.parse_args()
