#!/usr/bin/env python3
"""
SC-Controller compatibility/bootstrap helpers.
"""

import builtins
import codecs
import inspect

# Python 2 compatibility names used throughout the legacy codebase.
if not hasattr(builtins, "xrange"):
    def xrange(start, stop=None, step=1):
        # Python 2's xrange requires integral bounds. A number of legacy
        # call sites relied on Python 2 integer division before calling it.
        if stop is None:
            start, stop = 0, start
        return range(int(start), int(stop), int(step))
    builtins.xrange = xrange
if not hasattr(builtins, "unicode"):
    builtins.unicode = str
if not hasattr(builtins, "file"):
    builtins.file = open

# Python 2 removed inspect API compatibility.
if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec

# Python 2 codec name retained by the parser/string serializer.
def _legacy_escape_codec(name):
    if name.replace("-", "_").lower() == "string_escape":
        return codecs.lookup("unicode_escape")
    return None
codecs.register(_legacy_escape_codec)

# Python 2 Enum containment returned False for unrelated values; Python 3.11
# raises TypeError. Preserve the legacy behavior until the call sites are
# migrated individually.
from enum import EnumMeta
_original_enum_contains = EnumMeta.__contains__
def _legacy_enum_contains(cls, member):
    try:
        return _original_enum_contains(cls, member)
    except TypeError:
        return False
EnumMeta.__contains__ = _legacy_enum_contains

# Patch a few legacy semantics centrally so the migration remains behavior-
# compatible while individual modules are modernized.
try:
    from scc.actions import Action, NoAction
    if "__bool__" not in Action.__dict__:
        Action.__bool__ = lambda self: True
    NoAction.__bool__ = lambda self: False
    NoAction.__nonzero__ = NoAction.__bool__

    # Legacy absolute import used by TrackballAction.
    import sys
    from scc import modifiers as _modifiers
    sys.modules.setdefault("modifiers", _modifiers)

    from scc.special_actions import ChangeProfileAction, ShellCommandAction, OSDAction
    def _profile_to_string(self, multiline=False, pad=0):
        escaped = str(self.profile).encode("unicode_escape").decode("ascii")
        return (" " * pad) + "%s('%s')" % (self.COMMAND, escaped)
    ChangeProfileAction.to_string = _profile_to_string

    def _shell_init(self, command):
        if isinstance(command, bytes):
            command = command.decode("unicode_escape")
        Action.__init__(self, str(command))
        self.command = str(command)
    ShellCommandAction.__init__ = _shell_init

    def _shell_to_string(self, multiline=False, pad=0):
        escaped = str(self.parameters[0]).encode("unicode_escape").decode("ascii")
        return (" " * pad) + "%s('%s')" % (self.COMMAND, escaped)
    ShellCommandAction.to_string = _shell_to_string

    def _osd_to_string(self, multiline=False, pad=0):
        parameters = []
        if self.timeout != self.DEFAULT_TIMEOUT or self.size != self.DEFAULT_SIZE:
            parameters.append(str(self.timeout))
        if self.size != self.DEFAULT_SIZE:
            parameters.append(str(self.size))
        if self.action:
            parameters.append(self.action.to_string(multiline=multiline, pad=pad))
        else:
            escaped = str(self.text).encode("unicode_escape").decode("ascii")
            parameters.append("'%s'" % escaped)
        return (" " * pad) + "%s(%s)" % (self.COMMAND, ",".join(parameters))
    OSDAction.to_string = _osd_to_string
except Exception:
    # Bootstrap must never prevent unrelated modules from importing.
    pass
