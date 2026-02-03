from argparse import Namespace
from pathlib import Path

from suss.commands.index import index as index_cmd
from suss.handlers.repo import SussContext
from suss.misc import exit_codes


def test_index_command_returns_ok(tmp_path: Path) -> None:
    context = SussContext(tmp_path)
    args = Namespace(repo=None, context=context)
    code, msg = index_cmd(args)
    assert code == exit_codes.UserStatus.OK
