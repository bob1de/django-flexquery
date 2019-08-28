"""
Reusable QuerySet filtering logic for Django.
"""

try:
    from .flexquery import *
    from .q import *
except ImportError:  # pragma: no cover
    # Django is missing, just provide version
    __all__ = []
else:
    __all__ = ["FlexQuery", "Manager", "Q", "QuerySet"]


__version__ = "4.1.0"
