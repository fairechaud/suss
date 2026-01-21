from dataclasses import dataclass, field
from enum import IntEnum

class SaveCode(IntEnum):
    SAVE_SUCCESS = 0
    SAVE_FAILURE = 1
    SAVE_ERROR_DUPLICATE_ID = 2
    SAVE_ERROR_INVALID_FORMAT = 3

@dataclass 
class SaveResult:
    code: SaveCode
