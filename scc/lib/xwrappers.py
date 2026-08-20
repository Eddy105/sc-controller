"""Small ctypes wrapper around the X11 APIs used by SC Controller.

The module is intentionally lazy about loading X11 libraries so importing the
core action model does not fail on headless systems.
"""
from ctypes import CDLL, POINTER, Structure, byref, c_bool, c_char_p, c_int, c_long, c_short, c_ubyte, c_uint, c_ulong, c_ushort, c_void_p, cast


def _load_lib(*names):
    for name in names:
        try:
            return CDLL(name)
        except OSError:
            continue
    return None


libXFixes = _load_lib("libXfixes.so", "libXfixes.so.3")
libX11 = _load_lib("libX11.so", "libX11.so.6")
libXext = _load_lib("libXext.so", "libXext.so.6")

XID = c_ulong
Pixmap = XID
Colormap = XID
Atom = c_ulong
XserverRegion = c_ulong
GC = c_void_p
Display = c_void_p

SHAPE_BOUNDING = 0
SHAPE_CLIP = 1
SHAPE_INPUT = 2
SHAPE_SET = 0
XKBUSECOREKBD = 0x0100
ANYPROPERTYTYPE = 0
SUCCESS = 0
ISVIEWABLE = 2


class XRectangle(Structure):
    _fields_ = [("x", c_short), ("y", c_short), ("width", c_ushort), ("height", c_ushort)]


class XClassHint(Structure):
    _fields_ = [("res_name", c_char_p), ("res_class", c_char_p)]


class XkbStateRec(Structure):
    _fields_ = [
        ("group", c_ubyte), ("locked_group", c_ubyte), ("base_group", c_ushort),
        ("latched_group", c_ushort), ("mods", c_ubyte), ("base_mods", c_ubyte),
        ("latched_mods", c_ubyte), ("locked_mods", c_ubyte), ("compat_state", c_ubyte),
        ("grab_mods", c_ubyte), ("compat_grab_mods", c_ubyte), ("lookup_mods", c_ubyte),
        ("compat_lookup_mods", c_ubyte), ("ptr_buttons", c_ushort),
    ]


class XWindowAttributes(Structure):
    _fields_ = [
        ("x", c_int), ("y", c_int), ("width", c_int), ("height", c_int), ("depth", c_int),
        ("visual", c_void_p), ("root", XID), ("i_class", c_int), ("bit_gravity", c_int),
        ("win_gravity", c_int), ("backing_store", c_int), ("backing_planes", c_ulong),
        ("backing_pixel", c_ulong), ("save_under", c_bool), ("colormap", Colormap),
        ("map_installed", c_bool), ("map_state", c_int), ("all_event_masks", c_long),
        ("your_event_mask", c_long), ("do_not_propagate_mask", c_long), ("screen", c_void_p),
    ]


def _require_x11():
    if libX11 is None:
        raise RuntimeError("X11 libraries are not available")
    return libX11


def open_display(name=None):
    lib = _require_x11()
    fn = lib.XOpenDisplay
    fn.argtypes = [c_char_p]
    fn.restype = c_void_p
    encoded = name.encode("utf-8") if isinstance(name, str) else name
    return fn(encoded)


def free(value):
    if libX11 is not None:
        libX11.XFree(value)


def flush(dpy):
    if libX11 is not None:
        libX11.XFlush(dpy)


def get_default_root_window(dpy):
    fn = _require_x11().XDefaultRootWindow
    fn.argtypes = [c_void_p]
    fn.restype = XID
    return fn(dpy)


def get_window_size(dpy, window):
    attrs = XWindowAttributes()
    fn = _require_x11().XGetWindowAttributes
    fn.argtypes = [c_void_p, XID, POINTER(XWindowAttributes)]
    fn(dpy, window, byref(attrs))
    return attrs.width, attrs.height


def is_window_visible(dpy, window):
    attrs = XWindowAttributes()
    fn = _require_x11().XGetWindowAttributes
    fn.argtypes = [c_void_p, XID, POINTER(XWindowAttributes)]
    fn(dpy, window, byref(attrs))
    return attrs.map_state == ISVIEWABLE


def get_screen_size(dpy):
    return get_window_size(dpy, get_default_root_window(dpy))


def get_mouse_pos(dpy, relative_to=None):
    lib = _require_x11()
    relative_to = get_default_root_window(dpy) if relative_to is None else relative_to
    root_return, child = XID(), XID()
    x, y, child_x, child_y, mask = c_int(), c_int(), c_int(), c_int(), c_uint()
    fn = lib.XQueryPointer
    fn.argtypes = [c_void_p, XID, POINTER(XID), POINTER(XID), POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_int), POINTER(c_uint)]
    fn(dpy, relative_to, byref(root_return), byref(child), byref(x), byref(y), byref(child_x), byref(child_y), byref(mask))
    return x.value, y.value


def set_mouse_pos(dpy, x, y, relative_to=None):
    lib = _require_x11()
    relative_to = get_default_root_window(dpy) if relative_to is None else relative_to
    fn = lib.XWarpPointer
    fn.argtypes = [c_void_p, XID, XID, c_int, c_int, c_uint, c_uint, c_int, c_int]
    fn(dpy, 0, relative_to, 0, 0, 0, 0, x, y)
    flush(dpy)


def get_current_window(dpy):
    lib = _require_x11()
    root = get_default_root_window(dpy)
    atom = lib.XInternAtom(dpy, b"_NET_ACTIVE_WINDOW", False)
    actual_type, actual_format = Atom(), c_int()
    nitems, bytes_after = c_ulong(), c_ulong()
    prop = c_void_p()
    fn = lib.XGetWindowProperty
    fn.argtypes = [c_void_p, XID, Atom, c_long, c_long, c_bool, Atom, POINTER(Atom), POINTER(c_int), POINTER(c_ulong), POINTER(c_ulong), POINTER(c_void_p)]
    status = fn(dpy, root, atom, 0, 1, False, ANYPROPERTYTYPE, byref(actual_type), byref(actual_format), byref(nitems), byref(bytes_after), byref(prop))
    if status == SUCCESS and prop.value:
        window = cast(prop, POINTER(XID)).contents.value
        free(prop)
        return window
    window, revert_to = XID(), c_int()
    focus = lib.XGetInputFocus
    focus.argtypes = [c_void_p, POINTER(XID), POINTER(c_int)]
    focus(dpy, byref(window), byref(revert_to))
    return root if window.value == 0 else window.value


def get_window_title(dpy, window):
    lib = _require_x11()
    atom = lib.XInternAtom(dpy, b"_NET_WM_NAME", False)
    utf8 = lib.XInternAtom(dpy, b"UTF8_STRING", False)
    actual_type, actual_format = Atom(), c_int()
    nitems, bytes_after = c_ulong(), c_ulong()
    prop = c_void_p()
    fn = lib.XGetWindowProperty
    fn.argtypes = [c_void_p, XID, Atom, c_long, c_long, c_bool, Atom, POINTER(Atom), POINTER(c_int), POINTER(c_ulong), POINTER(c_ulong), POINTER(c_void_p)]
    if fn(dpy, window, atom, 0, 2048, False, utf8, byref(actual_type), byref(actual_format), byref(nitems), byref(bytes_after), byref(prop)) == SUCCESS and prop.value:
        try:
            return cast(prop, c_char_p).value.decode("utf-8", errors="replace")
        finally:
            free(prop)
    return None


def get_window_type(dpy, window):
    return None


def get_window_geometry(dpy, window):
    attrs = XWindowAttributes()
    fn = _require_x11().XGetWindowAttributes
    fn.argtypes = [c_void_p, XID, POINTER(XWindowAttributes)]
    fn(dpy, window, byref(attrs))
    return attrs.x, attrs.y, attrs.width, attrs.height


def get_xkb_state(dpy):
    if libX11 is None:
        raise RuntimeError("X11 libraries are not available")
    rec = XkbStateRec()
    fn = libX11.XkbGetState
    fn.argtypes = [c_void_p, c_uint, POINTER(XkbStateRec)]
    fn(dpy, XKBUSECOREKBD, byref(rec))
    return rec
