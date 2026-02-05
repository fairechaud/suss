from pathlib import Path
from argparse import Namespace
import json
from suss.commands.ls import ls as list_cmd
from suss.handlers.repo import SussContext
from suss.handlers.indexer import load_index, save_index
from suss.misc import exit_codes

def _populate_index(tmp_path) -> SussContext:
    repo_root = tmp_path
    context = SussContext(repo_root)
    index_path = context.get_index_file()
    index = load_index(index_path)
    index["testcases"].append( 
                              {
                                  "id": "TCID",
                                  "key": "sample_test_TCID",
                                  "title": "sample test",
                                  "tags": "",
                                  "group": "sample group",
                                  "path": "specs\\testcases\\sample group\\sample_test_TCID.md",
                                  "created": "sometime",
                                  "updated": "sometime",
                                  "fingerprint": "ABCDEFG"
                                  })
    index["testcases"].append(
                              {
                                  "id": "999999",
                                  "key": "sample_test_999999",
                                  "title": "sample test",
                                  "tags": "smoke",
                                  "group": "sample group",
                                  "path": "specs\\testcases\\sample group\\sample_test_999999.md",
                                  "created": "sometime",
                                  "updated": "sometime",
                                  "fingerprint": "ABCDEFG"
                                  })
    index["testcases"].append(
                              {
                                  "id": "XXXXXX",
                                  "key": "sample_test_happy_path_XXXXXX",
                                  "title": "sample test - happy path",
                                  "tags": "regression",
                                  "group": "",
                                  "path": "specs\\testcases\\sample_test_happy_path_XXXXXX.md",
                                  "created": "sometime",
                                  "updated": "sometime",
                                  "fingerprint": "ABCDEFG"
                                  })
    index["testcases"].append(
                              {
                                  "id": "ZZZZZZ",
                                  "key": "negative_test_happy_path",
                                  "title": "negative test - happy path",
                                  "tags": "TAG1, TAG2, smoke, regression",
                                  "group": "GROUP1",
                                  "path": "specs\\testcases\\negative_test_happy_path_ZZZZZZ.md",
                                  "created": "sometime",
                                  "updated": "sometime",
                                  "fingerprint": "ABCDEFG"
                                  }
                              )
    index["testcases"].append(
                              {
                                  "id": "000000",
                                  "key": "negative_test_happy_path",
                                  "title": "negative test - happy path",
                                  "tags": "TAG1, TAG2, TAG3",
                                  "group": "GROUP1",
                                  "path": "specs\\testcases\\negative_test_happy_path_000000.md",
                                  "created": "sometime",
                                  "updated": "sometime",
                                  "fingerprint": "ABCDEFG"
                                  }
                              )
    index["testcases"].append(
                              {
                                  "id": "111111",
                                  "key": "negative_test_happy_path",
                                  "title": "negative test - happy path",
                                  "tags": "TAG1, TAG2, TAG4",
                                  "group": "GROUP1",
                                  "path": "specs\\testcases\\negative_test_happy_path_111111.md",
                                  "created": "sometime",
                                  "updated": "sometime",
                                  "fingerprint": "ABCDEFG"
                                  }
                              )
    save_index(index_path, index)
    return context

def test_list_returns_error_when_index_is_empty(tmp_path: Path):
    repo_root = tmp_path
    context = SussContext(repo_root)
    index_path = context.get_index_file()
    index = {
            "meta": {"version": "0.2", "generated_at": "right now"},
            "testcases": []
            }
    save_index(index_path, index)
    args = Namespace(group="some_group", 
                     id="some_ID", 
                     tags="some_tag", 
                     tag_mode="any",
                     search="some_pattern", 
                     search_mode="any",
                     query_mode="any",
                     stdout="quiet",
                     limit=5,
                     context=context)
    code, msg = list_cmd(args)
    assert code == exit_codes.IndexStatus.MISSING_INDEX
    assert "suss tc new" in msg

def test_list_returns_error_when_index_is_missing(tmp_path: Path):
    repo_root = tmp_path
    context = SussContext(repo_root)
    args = Namespace(group="some_group", 
                     id="some_ID", 
                     tags="some_tag", 
                     tag_mode="any",
                     search="some_pattern", 
                     search_mode="any",
                     query_mode="any",
                     stdout="quiet",
                     limit=5,
                     context=context)
    code, msg = list_cmd(args)
    assert code == exit_codes.IndexStatus.MISSING_INDEX
    assert "suss index" in msg

def test_list_returns_invalid_status_on_incorrect_tag_mode(tmp_path: Path):
    context = _populate_index(tmp_path)
    args = Namespace(group="some_group", 
                     id="some_ID", 
                     tags="some_tag", 
                     tag_mode="other",
                     search="some_pattern", 
                     search_mode="any",
                     query_mode="any",
                     stdout="quiet",
                     limit=5,
                     context=context)
    code, _ = list_cmd(args)
    assert code == exit_codes.ReadStatus.INVALID_TAG

def test_list_returns_invalid_status_on_incorrect_search_mode(tmp_path: Path):
    context = _populate_index(tmp_path)
    args = Namespace(group="some_group", 
                     id="some_ID", 
                     tags="some_tag", 
                     tag_mode="any",
                     search="some_pattern", 
                     search_mode="other",
                     query_mode="any",
                     stdout="quiet",
                     limit=5,
                     context=context)
    code, _ = list_cmd(args)
    assert code == exit_codes.ReadStatus.INVALID_SEARCH

def test_list_returns_invalid_status_on_incorrect_stdout_mode(tmp_path: Path):
    context = _populate_index(tmp_path)
    args = Namespace(group="sample group", 
                     id="some_ID", 
                     tags="some_tag", 
                     tag_mode="any",
                     search="some_pattern", 
                     search_mode="any",
                     query_mode="any",
                     limit=5,
                     stdout="other",
                     context=context)
    code, _ = list_cmd(args)
    assert code == exit_codes.ReadStatus.INVALID_OUTPUT

def test_list_shows_no_matches_for_criteria(tmp_path: Path):
    context = _populate_index(tmp_path)
    args = Namespace(group="GROUP_NOT_FOUND",
                     id=None,
                     tags=None,
                     tag_mode=None,
                     search=None,
                     search_mode=None,
                     query_mode="any",
                     stdout="quiet",
                     limit=5,
                     context=context
                     )
    code, _ = list_cmd(args)
    assert code == exit_codes.ListStatus.NO_MATCH

def test_list_returns_match_any_results_group_and_id(tmp_path: Path, capsys):
    context = _populate_index(tmp_path)
    args = Namespace(group="sample group",
                     id="999999",
                     tags=None,
                     tag_mode=None,
                     search=None,
                     search_mode=None,
                     stdout="json",
                     query_mode="any",
                     limit=5,
                     context=context
                     )
    list_cmd(args)
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 2

def test_list_returns_group_and_id_intersection(tmp_path: Path, capsys):
    context = _populate_index(tmp_path)
    args = Namespace(group="sample group",
                     id="TCID",
                     tags=None,
                     tag_mode=None,
                     search=None,
                     search_mode=None,
                     stdout="json",
                     query_mode="all",
                     limit=5,
                     context=context
                     )
    list_cmd(args)
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 1

def test_list_returns_group_and_id_union(tmp_path: Path, capsys):
    context = _populate_index(tmp_path)
    args = Namespace(group="sample group",
                     id="999999",
                     tags=None,
                     tag_mode=None,
                     search=None,
                     search_mode=None,
                     stdout="json",
                     query_mode="any",
                     limit=5,
                     context=context
                     )
    list_cmd(args)
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 2

def test_list_returns_group_intersection_with_tags(tmp_path: Path, capsys):
    context = _populate_index(tmp_path)
    args = Namespace(group="GROUP1",
                     id=None,
                     tags="TAG1, TAG2",
                     tag_mode="all",
                     search=None,
                     search_mode=None,
                     stdout="json",
                     query_mode="any",
                     limit=5,
                     context=context
                     )
    list_cmd(args)
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 3

def test_list_returns_match_any_results_tags(tmp_path: Path, capsys):
    context = _populate_index(tmp_path)
    args = Namespace(group=None,
                     id=None,
                     tags="smoke, regression",
                     tag_mode="any",
                     search=None,
                     search_mode=None,
                     stdout="json",
                     query_mode="any",
                     limit=5,
                     context=context
                     )
    list_cmd(args)
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 3

def test_list_returns_match_any_results_tags_and_group(tmp_path: Path, capsys):
    context = _populate_index(tmp_path)
    args = Namespace(group="sample group",
                     id=None,
                     tags="smoke, regression",
                     tag_mode="any",
                     search=None,
                     search_mode=None,
                     stdout="json",
                     limit=5,
                     query_mode="any",
                     context=context
                     )
    list_cmd(args)
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 4

def test_list_returns_match_all_results_tags(tmp_path: Path, capsys):
    context = _populate_index(tmp_path)
    args = Namespace(group=None,
                     id=None,
                     tags="smoke, regression",
                     tag_mode="all",
                     search=None,
                     search_mode=None,
                     stdout="json",
                     limit=5,
                     query_mode="any",
                     context=context
                     )
    list_cmd(args)
    out = capsys.readouterr().out
    assert len(json.loads(out)) == 1

def test_list_returns_no_match_for_empty_criteria(tmp_path: Path):
    context = _populate_index(tmp_path)
    args = Namespace(group=None,
                     id=None,
                     tags=None,
                     tag_mode=None,
                     search=None,
                     search_mode=None,
                     stdout=None,
                     limit=5,
                     query_mode="any",
                     context=context)
    code, _ = list_cmd(args)
    assert code == exit_codes.ListStatus.NO_MATCH
