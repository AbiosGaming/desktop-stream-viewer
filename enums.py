from enum import Enum


class AddStreamError(Enum):
    """Errors that can occur while adding a stream"""
    URL_NOT_SUPPORTED = 1
    DEFAULT_QUALITY_MISSING = 2
    OTHER = 3
