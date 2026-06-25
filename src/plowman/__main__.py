from plowman.commands.harvest import HarvestCommand
from plowman.commands.sow import SowCommand
from plowman.lib.cli import parse_args


def main() -> None:
    args = parse_args()
    match args.subcommand:
        case "sow":
            SowCommand(verbosity=args.verbosity, dry_run=args.dry_run).run()
        case "harvest":
            HarvestCommand(
                verbosity=args.verbosity,
                dry_run=args.dry_run,
                add_to_estate=args.add_to_estate,
            ).run()
