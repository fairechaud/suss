from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass 
class TestCase:
    key: Optional[str]
    id: Optional[str]
    title: str
    tags: List[str] = field(default_factory=list)
    group: Optional[str] = None
    body: str = ""
    metadata: Dict[str,str] = field(default_factory=dict)
    source: Optional[str] = None
    author: Optional[str] = "linkecu"
