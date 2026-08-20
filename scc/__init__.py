#!/usr/bin/env python3
"""
SC-Controller compatibility/bootstrap helpers.
"""

# Legacy SC-Controller modules are being migrated incrementally from Python 2.
# Keep these names available while preserving the original runtime semantics.
import builtins
import inspect

if not hasattr(builtins, "xrange"):
    builtins.xrange = range
if not hasattr(builtins, "unicode"):
    builtins.unicode = str
if not hasattr(builtins, "file"):
    builtins.file = open

if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec
