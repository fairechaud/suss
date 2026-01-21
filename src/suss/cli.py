import argparse
import sys

from suss.misc import exit_codes
from suss.commands import init as init_cmd
from suss.commands import index as index_cmd
from suss.commands import testcase as tc_cmd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="suss", description="SUSS - test case cataloguing CLI")
    sub = parser.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init", help="Initialise a new SUSS repo")
    p_init.set_defaults(func=init_cmd.init)

    p_index = sub.add_parser("index", help="Rebuild the derived index")
    p_index.set_defaults(func=index_cmd.index)

    p_tc = sub.add_parser("tc", aliases=["test", "testcase"], help="Testcase operations")
    tc_sub = p_tc.add_subparsers(dest="tc_cmd")

    p_tc_create = tc_sub.add_parser("create", aliases=["new"], help="Create testcase(s)")
    p_tc_create.add_argument("input", nargs="?", default=None, help="Omit for editor, '-' for stdin")
    p_tc_create.add_argument("-g", "--group", default=None, help="Group/folder (e.g. PDM_270)")
    p_tc_create.set_defaults(func=tc_cmd.create)

    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        # interactive menu later
        print("Welcome to SUSS")
        return exit_codes.EXIT_OK

    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return exit_codes.EXIT_USER_ERROR

    try:
        return int(args.func(args))
    except KeyboardInterrupt:
        return exit_codes.EXIT_INTERRUPTED


if __name__ == "__main__":
    raise SystemExit(main())
