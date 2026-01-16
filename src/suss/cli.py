import argparse
import sys


EXIT_OK = 0
EXIT_USER_ERROR = 1
EXIT_REPO_ERROR = 2
EXIT_INTERRUPTED = 130

def common_args() -> list[argparse.ArgumentParser]:
    return []

def menu_options() -> None:
    print("Welcome to SUSS")
    print("1) list tests")
    print("2) Search")
    print("3) Create tests")
    print("4) Manage test suites")

def launch_from_args(args: argparse.Namespace) -> int:
    if args.cmd == "init":
        print("suss init: TODO create suss.yaml, directory skeleton")
        return EXIT_OK

    if args.cmd == "index":
        print("suss init: TODO scan specs/testcases, parse front matter, write .suss/index.json")
        return EXIT_OK
    
    if args.cmd == "tc" or args.cmd == "test" or args.cmd == "testcase":
        print("suss tc: Subcommands are create with optional file path or read/update/delete with options are ID, and list with option tags (category, label, etc))")

    if args.cmd == "search":
        print("suss search: Advanced grep search for testcases, option is a specific string")

    if args.cmd == "suite":
        print("suss suite: Subcommands are add with option IDs, and export")

    return EXIT_USER_ERROR

def parse_args():
    common = common_args()
    parser = argparse.ArgumentParser(
        prog="suss",
        description="SUSS - catalog and search test cases specs and patterns",
        parents=common
    )

    sub = parser.add_subparsers(dest="cmd", required=False)

    # init
    init_cmd = sub.add_parser("init", 
                              help="Initialise a new SUSS repository in the current directory",
                              parents=common
                              )
    # index
    index_cmd = sub.add_parser("index",
                               help="Rebuild the derived index",
                               parents=common
                               )
    tc_cmd = sub.add_parser("tc", 
                            aliases=["test", "testcase"],
                            help="Rebuild the derived index",
                            parents=common
                            )
    return parser

def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if not argv:
        menu_options()
        return EXIT_OK

    parser = parse_args()
    try:
        args = parser.parse_args(argv)
        if args.cmd is None:
            parser.print_help()
            return EXIT_USER_ERROR
        return launch_from_args(args)
    except KeyboardInterrupt:
        print("User stopped execution")
        return EXIT_INTERRUPTED
    except Exception as e:
        print(f"Something went wrong : {e}")
        return EXIT_USER_ERROR

if __name__ == "__main__":
    raise SystemExit(main())
