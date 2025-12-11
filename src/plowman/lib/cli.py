import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from typing import Literal

from plowman.__version__ import __version__

sys.tracebacklimit = 0


@dataclass(frozen=True, slots=True)
class PlowmanArgs:
    subcommand: Literal["sow"]
    verbosity: int
    dry_run: bool


def parse_args() -> PlowmanArgs:
    parser = ArgumentParser(prog="plowman", description="Dotfile farm manager")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="print the version and exit",
    )

    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        dest="verbosity",
        help="increase the level of verbosity",
    )
    parent_parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="perform a trial run with no changes made",
    )

    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    subparsers.add_parser("sow", parents=[parent_parser])

    args = parser.parse_args()
    if args.verbosity > 0:
        sys.tracebacklimit = 1000

    return PlowmanArgs(
        subcommand=args.subcommand, verbosity=args.verbosity, dry_run=args.dry_run
    )
