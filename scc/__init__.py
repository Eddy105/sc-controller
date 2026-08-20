#!/usr/bin/env python3
"""
SC-Controller compatibility/bootstrap helpers.
"""

import builtins
import codecs
import inspect

if not hasattr(builtins, "xrange"):
    def xrange(start, stop=None, step=1):
        if stop is None:
            start, stop = 0, start
        return range(int(start), int(stop), int(step))
    builtins.xrange = xrange
if not hasattr(builtins, "unicode"):
    builtins.unicode = str
if not hasattr(builtins, "file"):
    builtins.file = open

if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec

def _legacy_escape_codec(name):
    if name.replace("-", "_").lower() == "string_escape":
        return codecs.lookup("unicode_escape")
    return None
codecs.register(_legacy_escape_codec)

from enum import EnumMeta
_original_enum_contains = EnumMeta.__contains__
def _legacy_enum_contains(cls, member):
    try:
        return _original_enum_contains(cls, member)
    except TypeError:
        return False
EnumMeta.__contains__ = _legacy_enum_contains

try:
    from scc.actions import Action, NoAction
    from scc.constants import PARSER_CONSTANTS
    from scc.tools import nameof

    if "__bool__" not in Action.__dict__:
        Action.__bool__ = lambda self: True
    NoAction.__bool__ = lambda self: False
    NoAction.__nonzero__ = NoAction.__bool__

    @staticmethod
    def _encode_parameter(parameter):
        if parameter in PARSER_CONSTANTS:
            return parameter
        if isinstance(parameter, str):
            return repr(parameter)
        return nameof(parameter)
    Action._encode_parameter = _encode_parameter

    import sys
    from scc import modifiers as _modifiers
    sys.modules.setdefault("modifiers", _modifiers)

    from scc.special_actions import ChangeProfileAction, ShellCommandAction, OSDAction, DialogAction

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

    def _dialog_to_string(self, multiline=False, pad=0):
        rv = "%s%s(" % (" " * pad, self.COMMAND)
        if self.confirm_with != self.DEFAULT_POSITION:
            pass
        if self.confirm_with != "DEFAULT":
            rv += "%s, " % nameof(self.confirm_with)
            if self.cancel_with != "DEFAULT":
                rv += "%s, " % nameof(self.cancel_with)
        rv += "%r, " % self.text
        for option in self.options:
            rv += "%s, " % option.to_string(False)
        rv = rv.strip(" ,") + ")"
        return rv
    # Keep the original dialog defaults semantics while removing Python 2 bytes.
    def _dialog_to_string_safe(self, multiline=False, pad=0):
        rv = "%s%s(" % (" " * pad, self.COMMAND)
        from scc.constants import DEFAULT
        if self.confirm_with != DEFAULT:
            rv += "%s, " % nameof(self.confirm_with)
            if self.cancel_with != DEFAULT:
                rv += "%s, " % nameof(self.cancel_with)
        rv += "%r" % self.text
        if self.options:
            rv += ", " + ", ".join(option.to_string(False) for option in self.options)
        return rv + ")"
    DialogAction.to_string = _dialog_to_string_safe
except Exception:
    pass
