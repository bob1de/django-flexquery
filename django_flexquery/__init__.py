"""
Reusable QuerySet filtering logic for Django.
"""

try:
    from .flexquery import Manager, FlexQuery, QuerySet
    from .q import Q
except ImportError:  # pragma: no cover
    # Django is missing, just provide version
    __all__ = []
else:
    __all__ = ["FlexQuery", "Manager", "Q", "QuerySet"]


__version__ = "2.0.0"
