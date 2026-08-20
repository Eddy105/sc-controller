"""Python 3 compatible JSON encoder used by SC-Controller.

The project historically carried a private copy of Python's JSON encoder
only to keep arrays compact.  The standard library already provides that
behavior when ``indent`` is ``None``, so use it directly instead of relying on
removed Python 2 internals.
"""

import json


class JSONEncoder(json.JSONEncoder):
    """Compatibility wrapper around :class:`json.JSONEncoder`.

    ``encoding`` is accepted for compatibility with the old Python 2 API but
    is intentionally ignored on Python 3, where strings are already Unicode.
    """

    def __init__(self, skipkeys=False, ensure_ascii=True,
                 check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, encoding='utf-8', default=None,
                 **kwargs):
        super(JSONEncoder, self).__init__(
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            sort_keys=sort_keys,
            indent=indent,
            separators=separators,
            default=default,
            **kwargs
        )
