import sys
from argparse import ArgumentParser
from dataclasses import dataclass

from plowman.__version__ import __version__

sys.tracebacklimit = 0


@dataclass(frozen=True, slots=True)
class CLIArgs:
    verbosity: int


def parse_args() -> CLIArgs:
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

    args = parser.parse_args()
    if args.verbosity > 0:
        sys.tracebacklimit = 1000

    return CLIArgs(verbosity=args.verbosity)
