from plowman.commands.sow import SowCommand
from plowman.lib.cli import parse_args


def main() -> None:
    args = parse_args()
    match args.subcommand:
        case "sow":
            SowCommand(verbosity=args.verbosity, dry_run=args.dry_run).run()
