from dataclasses import dataclass, field
import hashlib
from typing import Dict, Optional


def _normalise_for_fingerprint(text: str) -> str:
    return " ".join(text.lower().split())

@dataclass 
class TestCase:
    tc_id: Optional[str]
    key: Optional[str]
    title: str
    tags: Optional[str]
    group: Optional[str] = None
    created: str = ""
    updated: str = ""
    body: str = ""
    source: Optional[str] = None
    author: Optional[str] = "linkecu"
    metadata: Dict[str,str] = field(default_factory=dict)

    def get_front_matter_as_strings(self) -> str:
        fm = []
        if self.tc_id: 
            fm.append(f"id: {self.tc_id}")
        if self.key:
            fm.append(f"key: {self.key}")
        if self.title:
            fm.append(f"title: {self.title}")
        if self.tags:
            fm.append(f"tags: {self.tags}")
        if self.created:
            fm.append(f"created: {self.created}")
        if self.updated:
            fm.append(f"updated: {self.updated}")
        return "\n".join(fm)

    def get_body_as_strings(self) -> str:
        return self.body

    def get_testcase_as_fields(self,
                               include_id: bool = False,
                               include_tags: bool = False,
                               include_key: bool = False,
                               include_body: bool = True,
                               include_created: bool = False,
                               include_updated: bool = False) -> str:
        """
        Renders front matter fields as needed.
        """
        fm = "---\n"
        body = ""
        if include_id: 
            fm += f"id: {self.tc_id}\n"
        fm += f"title: {self.title}\n"
        if include_tags: 
            fm += f"tags: {self.tags}\n"
        if include_key: 
            fm += f"key: {self.key}\n"
        if include_created:
            fm += f"created: {self.created}\n"
        if include_updated: 
            fm += f"updated: {self.updated}\n"
        fm += "---\n\n"
        if include_body:
            body += self.body
        return fm + body

    def get_key(self) -> str | None:
        if self.key:
            return self.key
        else:
            return None

    def compute_fingerprint(self) -> str:
        data = _normalise_for_fingerprint(self.title) + "|" + _normalise_for_fingerprint(self.body)
        sha1 = hashlib.sha1(data.encode('utf-8'))
        return sha1.hexdigest()

    def ensure_ids(self):
        data = _normalise_for_fingerprint(self.title) + "|" + _normalise_for_fingerprint(self.body)[:12]
        sha1 = hashlib.sha1(data.encode('utf-8'))
        return sha1.hexdigest()

    def compute_key(self):
        if not self.title or not self.tc_id:
            raise ValueError("title and id are required to compute key")
        keys = [key.strip() for key in self.title.lower().split("-")]
        hash = self.tc_id[-6:]
        key_filename = "_".join(keys) + f"_{hash}"
        return key_filename.replace(" ", "_")
