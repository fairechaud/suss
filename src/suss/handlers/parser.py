from pathlib import Path
import re
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib

from suss.core.testcase import TestCase

from linktoolsapi.logger import LinkLogger
from suss.handlers.io import read_text
_log = LinkLogger(__name__)

# Error(s)
@dataclass(frozen=True)
class ParsingError:
    message: str = ""
    source: str = ""
    line: int | None = None

    def __str__(self) -> str:
        location = ""
        if self.source:
            location += self.source
        if self.line:
            location += f":{self.line}"
        if location:
            location += f":{self.message}"
            return location
        else:
            return self.message

class ParserException(ValueError):
    pass

# Helpers
def now_iso_utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def generate_id(title: str, body: str) -> str:
    """
    Makes 12-char UUID based on title + body of a testcase
    """
    return make_fingerprint_of_text(
        normalise_for_fingerprint(title)+ "|" + normalise_for_fingerprint(body))[:12]

def _split_front_matter_and_body(markdown: str) -> tuple[str, str]:
    """
    Returns (front_matter_text, body_text).
    If front matter is missing, front_matter_text is "" and body is full markdown
    """
    lines = markdown.splitlines()
    if not lines or lines[0].strip() != "---":
        return "", markdown.lstrip("\n")

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break

    if end is None:
        # malformed front matter treated as no front matter for simplicity
        return "", markdown.lstrip("\n")

    fm = "\n".join(lines[1:end]).strip("\n")
    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    return fm, body

def _parse_tags(tag_field: str) -> str:
    """
    Supports:
        tags: a1, a2, b1, ...
    """
    tag_list = ""
    tags = tag_field.strip()
    if not tags:
        return tag_list
    tag_list = ", ".join(tag.strip() for tag in tags.split(","))
    return tag_list

def _parse_front_matter_key_values(front_matter: str, source: str) -> dict:
    """
    Very small YAML-ish parser:
        key: value
    Ignores blank lines and comment lines starting with '#'
    """
    meta: dict = {}
    if not front_matter.strip():
        return meta

    for idx, raw in enumerate(front_matter.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise ParserException(str(ParsingError("Invalid front matter line (expected <key>: <value>)", source, idx)))

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            raise ParserException(str(ParsingError("Empty key in front matter", source, idx)))

        meta[key] = value

    return meta

def _validate_id(tc_id: str, source: str) -> str:
    """
    Allows <ALPHANUM/UNDERSCORE/DASH> style IDs
    """
    id = tc_id.strip()
    if not id:
        return ""
    if not re.fullmatch(r"[A-Za-z0-9_\-\.]+", id):
        raise ParserException(str(ParsingError(f"Invalid id format: {tc_id!r}", source)))
    return id

def _normalise_title(title: str, source: str) -> str:
    t = (title or "").strip()
    if not t:
        raise ParserException(str(ParsingError("Missing required field: title", source)))
    return t

# Public API
def parse_markdown_draft_to_testcase(markdown: str, source: str = "") -> TestCase:
    """
    Parses a testcase from markdown.

    Requires:
        - Title in front matter

    Populates defaults:
        - id (generated if missing)
        - created 
        - updated 
        - tags (defaults to [])
    """
    if not markdown.strip():
        raise ParserException(str(ParsingError("Empty markdown input", source)))

    front, body = _split_front_matter_and_body(markdown)
    meta = _parse_front_matter_key_values(front, source=source)
    _log.debug(f"front matter was : {meta}")


    title = _normalise_title(str(meta.get("title", "") or ""), source)

    tc_id = _validate_id(str(meta.get("id","") or ""), source)
    if not tc_id:
        tc_id = generate_id(title=title, body=body)
    tags = meta.get("tags", "")
    parsed_tags = _parse_tags(tags)

    created = str(meta.get("created", "") or "").strip() or now_iso_utc()
    updated = str(meta.get("updated", "") or "").strip() or created

    key = derive_testcase_key(title,tc_id)

    return TestCase(
        key=key,
        tc_id=tc_id,
        title=title,
        tags=parsed_tags,
        created=created,
        updated=updated,
        body=body.rstrip() + "\n",
        source=source
    )

def render_testcase_to_text(tc: TestCase,
                            include_id: bool = False,
                            include_tags: bool = False,
                            include_key: bool = False,
                            include_body: bool = True) -> str:
    """
    Renders a testcase object to text format.
    """
    text = tc.get_testcase_as_fields(include_id=include_id,
                                     include_tags=include_tags,
                                     include_key=include_key,
                                     include_body=include_body)
    return text

def render_testcase_as_inline_string(tc: TestCase) -> str:
    """
    Renders a testcase object to inline string format with delimiters for readability.
    """
    fm = tc.get_front_matter_as_strings().strip()
    body = tc.get_body_as_strings().strip()
    parsed_fm = fm.replace("\n"," | ")
    parsed_body = body.replace("\n", " | ")
    return "> " + parsed_fm + " || " + parsed_body

def derive_testcase_key(title: str, tc_id: str):
    keys = [key.strip() for key in title.lower().split("-")]
    hash = tc_id[-6:]
    key_filename = "_".join(keys) + f"_{hash}"
    return key_filename.replace(" ", "_")

def identify_markdown_style(markdown_filepath: Path) -> tuple[TestCase, str]:
    try:
        markdown = read_text(markdown_filepath)
        front, _ = _split_front_matter_and_body(markdown)
    except Exception as e:
        raise IOError(f"path does not point to an .md file : {e}")
    if front == "":
        raise ParserException(
            str(
                ParsingError(
                    "Legacy markdown without front matter is not supported. "
                    "Please add front matter or import manually.",
                    source=str(markdown_filepath),
                )
            )
        )
    return make_testcase_from_markdown_draft(markdown)

def make_testcase_from_markdown_legacy(markdown: str) -> tuple[TestCase, str]:

    _log.debug(markdown)

    raise ParserException("Legacy markdown without front matter is not supported.")

def make_testcase_from_markdown_draft(markdown: str) -> tuple[TestCase, str]:
    tc = parse_markdown_draft_to_testcase(markdown)
    fingerprint = make_fingerprint_of_text(
        normalise_for_fingerprint(tc.title) + "|" + normalise_for_fingerprint(tc.body)
    )
    return tc, fingerprint

def normalise_for_fingerprint(text: str) -> str:
    """
    Formats strings so they can be easily hashed
    """
    return " ".join(text.lower().split())

def make_fingerprint_of_text(data: str) -> str:
    """
    Returns the SHA-1 hash of a given string
    """
    sha1 = hashlib.sha1(data.encode('utf-8'))
    return sha1.hexdigest()

def make_fingerprint_of_file(filepath: Path) -> str:
    """
    Returns the SHA-1 hash of a file's contents
    Reads in chunks to handle large files efficiently
    """
    sha1 = hashlib.sha1()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha1.update(chunk)
    except FileNotFoundError:
        _log.error(f"this file <{filepath}> doesn't exist")
    except PermissionError:
        _log.error(f"permission denied: {filepath}")
    _log.debug(f"the hash of {filepath} is = {sha1.hexdigest()}")
    return sha1.hexdigest()
