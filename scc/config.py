#!/usr/bin/env python3
"""SC-Controller configuration handling."""
from __future__ import unicode_literals

from scc.paths import get_config_path
from scc.profile import Encoder
from scc.special_actions import ChangeProfileAction

import os, json, logging
log = logging.getLogger("Config")


class Config(object):
    DEFAULTS = {
        "autoswitch_osd": True,
        "autoswitch": [],
        "recent_max": 10,
        "recent_profiles": ["Desktop", "XBox Controller with High Precision Camera", "XBox Controller"],
        "drivers": {
            "sc_dongle": True, "sc_by_cable": True, "sc_by_bt": True,
            "steamdeck": True, "fake": False, "hiddrv": True,
            "evdevdrv": True, "ds4drv": True,
        },
        "fix_xinput": True,
        "gui": {
            "enable_status_icon": False, "minimize_to_status_icon": True,
            "minimize_on_start": False, "autokill_daemon": False,
            "news": {"enabled": True, "last_version": "0.3.12"},
        },
        "controllers": {},
        "output": {
            "vendor": "0x045e", "product": "0x028e", "version": "0x110",
            "name": "Microsoft X-Box 360 pad", "buttons": 11, "rumble": True,
            "axes": [(-32768, 32767), (-32768, 32767), (-32768, 32767),
                     (-32768, 32767), (0, 255), (0, 255), (-1, 1), (-1, 1)],
        },
        "enable_sniffing": False,
        "osd_style": "Classic.gtkstyle.css",
        "osd_colors": {"background": "101010", "border": "101010", "text": "16BF24",
                        "menuitem_border": "101010", "menuitem_hilight": "202020",
                        "menuitem_hilight_text": "16FF26", "menuitem_hilight_border": "16FF26",
                        "menuseparator": "2e3436"},
        "osk_colors": {"hilight": "7A7A7A", "pressed": "B0B0B0", "button1": "101010",
                        "button1_border": "101010", "button2": "2e3436", "button2_border": "2e3436",
                        "text": "16BF24"},
        "gesture_colors": {"background": "160c00ff", "grid": "004000ff", "line": "ffffff1a"},
        "windows_opacity": 0.95,
        "ignore_serials": True,
    }

    CONTROLLER_DEFAULTS = {
        "name": None, "icon": None, "led_level": 80, "idle_timeout": 600,
        "osd_alignment": 0, "input_rotation_l": 20, "input_rotation_r": -20,
        "menu_control": "STICK", "menu_confirm": "A", "menu_cancel": "B",
    }

    def __init__(self):
        self.filename = os.path.join(get_config_path(), "config.json")
        self.reload()

    def reload(self):
        try:
            self.load()
        except Exception as e:
            log.warning("Failed to load configuration; Creating new one.")
            log.warning("Reason: %s", (e,))
            self.create()
        if self.check_values():
            self.save()

    def _check_dict(self, values, defaults):
        rv = False
        for d in defaults:
            if d not in values:
                values[d] = defaults[d]
                rv = True
            if type(values[d]) == dict:
                rv = self._check_dict(values[d], defaults[d]) or rv
        return rv

    def check_values(self):
        rv = self._check_dict(self.values, self.DEFAULTS)
        if "autoswitch" in self.values:
            for a in self.values["autoswitch"]:
                if "profile" in a:
                    a["action"] = ChangeProfileAction(str(a["profile"])).to_string()
                    del a["profile"]
                    rv = True
        return rv

    def get_controller_config(self, controller_id):
        if controller_id in self.values['controllers']:
            rv = self.values['controllers'][controller_id]
            for key in self.CONTROLLER_DEFAULTS:
                if key not in rv:
                    rv[key] = 0 if key in ("input_rotation_l", "input_rotation_r") else self.CONTROLLER_DEFAULTS[key]
            return rv
        rv = self.values['controllers'][controller_id] = {key: self.CONTROLLER_DEFAULTS[key] for key in self.CONTROLLER_DEFAULTS}
        rv["name"] = controller_id
        return rv

    def load(self):
        with open(self.filename, "r") as fileobj:
            self.values = json.load(fileobj)

    def create(self):
        self.values = {}
        self.check_values()
        self.save()

    def save(self):
        if not os.path.exists(get_config_path()):
            os.makedirs(get_config_path())
        data = {k: self.values[k] for k in self.values}
        jstr = Encoder(sort_keys=True, indent=4).encode(data)
        with open(self.filename, "w") as fileobj:
            fileobj.write(jstr)
        log.debug("Configuration saved")

    def __iter__(self):
        yield from self.values

    def get(self, key, default=None):
        return self.values.get(key, default)

    def set(self, key, value):
        self.values[key] = value

    __getitem__ = get
    __setitem__ = set

    def __contains__(self, key):
        return key in self.values
