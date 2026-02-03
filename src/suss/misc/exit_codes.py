from enum import IntEnum

class ReadStatus(IntEnum):
    OK = 0
    EMPTY_INPUT = 1
    MISSING_DATA = 2
    INVALID_ID = 3
    INVALID_TAG = 4
    INVALID_GROUP = 5
    INVALID_SEARCH = 6
    INVALID_INPUT = 7
    LEGACY_UNSUPPORTED = 98
    UNEXPECTED = 99

class ParseStatus(IntEnum):
    OK = 0
    TEST_CREATION_FAILED = 1
    UNEXPECTED = 99

class WriteStatus(IntEnum):
    OK = 0
    PATH_INVALID = 1
    WRITE_OPERATION_FAILED = 2
    ALREADY_EXISTS = 3
    UNEXPECTED = 99

class RepoStatus(IntEnum):
    OK = 0
    ALREADY_EXISTS = 1
    UNEXPECTED = 99

class IndexStatus(IntEnum):
    OK = 0
    DUPLICATE_FOUND = 1
    MISSING_INDEX = 2
    LOAD_FAILED = 3
    UNEXPECTED = 99

class ListStatus(IntEnum):
    OK = 0
    NO_MATCH = 1
    UNEXPECTED = 99

class UserStatus(IntEnum):
    OK = 0
    USER_INTERRUPTED = 98
    UNEXPECTED = 99
