import argparse
import sys

from suss.misc.exit_codes import UserStatus, ReadStatus
from suss.handlers.repo import get_repo_context
from suss.commands import ls as list_cmd
from suss.commands import init as init_cmd
from suss.commands import index as index_cmd
from suss.commands import testcase as tc_cmd

from linktoolsapi.logger import LinkLogger, LinkLoggerConfiguration, DEBUG

_log = LinkLogger(__name__)

def global_args():
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument(
        "-l", "--logs",
        action="store_true",
        default=False,
        help="Enable logs to stdout"
    )
    p.add_argument("-r", "--repo", default=None, help="Override repo root (e.g. C:\\sandbox\\)")
    return p


def build_parser() -> argparse.ArgumentParser:
    globals = global_args()
    parser = argparse.ArgumentParser(prog="suss", 
                                     description="SUSS - test case cataloguing CLI",
                                     parents=[globals]
                                     )
    sub = parser.add_subparsers(dest="cmd")

    p_init = sub.add_parser("init", help="Initialise a new SUSS repo")
    p_init.set_defaults(func=init_cmd.init)

    p_index = sub.add_parser("index", help="Rebuild the derived index")
    p_index.set_defaults(func=index_cmd.index)

    p_list = sub.add_parser("list", aliases=["ls"], help="List specific testcases based on criteria.")
    p_list.add_argument("-g", "--group", default=None, help="CSV groups to match lazily e.g. -g PDM_270, PDM_271 matches PDM_270 OR PDM_271 testcases.")
    p_list.add_argument("-i","--id", default=None, help="CSV IDs to match lazily e.g. -i aaa111, bbb222 matches aaa111 OR bbb222 testcases.")
    p_list.add_argument("-t", "--tags", default=None, help="CSV tags to match, can be modified to lazy/greedy match through --tag-mode.")
    p_list.add_argument("--tag-mode", choices=["any", "all"], default="any", help="Tag match mode (any|all). Default is any for a lazy search.")
    p_list.add_argument("-s","--search", default=None, help="Search for matching substrings in testcase body (e.g. firmware update).")
    p_list.add_argument("--search-mode", choices=["any", "all"], default="any", help="Substring search mode (any|all). Default is any for a lazy search.")
    p_list.add_argument("-m","--query-mode", choices=["any", "all"], default="any", help="Defines the match mode across criteria (any|all). Default is any for matching group OR id OR tags OR search, all matches group AND id AND tags AND search.")
    p_list.add_argument("--stdout", choices=["quiet","short", "verbose", "json"], default="quiet", help="Display mode for list results (quiet|short|verbose|json). Default is quiet for no stdout.")
    p_list.add_argument("--limit", type=int, default=5, help="Customise size of head (prints [LIMIT] top results). Default is 5")
    p_list.set_defaults(func=list_cmd.ls)

    p_tc = sub.add_parser("tc", aliases=["test", "testcase"], help="Testcase operations")
    tc_sub = p_tc.add_subparsers(dest="tc_cmd")

    p_tc_create = tc_sub.add_parser("create", aliases=["new"], help="Create testcase(s)")
    p_tc_create.add_argument("input", nargs="?", default=None, help="Omit for editor, '-' for stdin, filepath for appending")
    p_tc_create.add_argument("-g", "--group", default=None, help="Group/folder (e.g. PDM_270)")
    p_tc_create.set_defaults(func=tc_cmd.create)

    return parser

def log_setup(to_console: bool):
    LOG_CONFIG = LinkLoggerConfiguration()
    LOG_CONFIG.set_global_log_level(DEBUG)
    if to_console:
        LOG_CONFIG.enable_console_handler()

def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        # interactive menu later
        _log.info("Welcome to SUSS")
        return UserStatus.OK

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.cmd != "init":
        context = get_repo_context(args)
        setattr(args, "context", context)

    log_setup(to_console=args.logs)

    if not hasattr(args, "func"):
        parser.print_help()
        return UserStatus.UNEXPECTED

    try:
        result = args.func(args)
        if isinstance(result, tuple):
            code, msg = result
            if msg:
                print(f"[{code.name}] {msg}")
            return int(code)
        return int(result)
    except KeyboardInterrupt:
        return UserStatus.USER_INTERRUPTED


if __name__ == "__main__":
    raise SystemExit(main())
