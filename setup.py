#!/usr/bin/env python3
"""Build and install SC Controller."""

from glob import glob
from setuptools import Extension, setup


DAEMON_VERSION = "0.4.8"

data_files = [
    ("share/scc/glade", glob("glade/*.glade")),
    ("share/scc/glade/ae", glob("glade/ae/*.glade")),
    ("share/scc/images", glob("images/*.svg")),
    ("share/scc/images", glob("images/*.json")),
    ("share/scc/images/button-images", glob("images/button-images/*.svg")),
    ("share/scc/images/button-images", glob("images/button-images/*.json")),
    ("share/scc/images/controller-icons", glob("images/controller-icons/*.svg")),
    ("share/scc/images/controller-images", glob("images/controller-images/*.svg")),
    ("share/icons/hicolor/24x24/status", glob("images/24x24/status/*.png")),
    ("share/icons/hicolor/256x256/status", glob("images/256x256/status/*.png")),
    ("share/scc/default_profiles", glob("default_profiles/*.sccprofile")),
    ("share/scc/default_profiles", glob("default_profiles/.*.sccprofile")),
    ("share/scc/default_menus", glob("default_menus/*.menu")),
    ("share/scc/default_menus", glob("default_menus/.*.menu")),
    ("share/scc/osd-styles", glob("osd-styles/*.json")),
    ("share/scc/osd-styles", glob("osd-styles/*.css")),
    ("share/scc/", ["gamecontrollerdb.txt"]),
    ("share/pixmaps", ["images/sc-controller.svg"]),
    ("share/mime/packages", ["scc-mime-types.xml"]),
    ("share/applications", ["scripts/sc-controller.desktop"]),
    ("lib/udev/rules.d", glob("scripts/*.rules")),
]

data_files += [
    (
        "share/scc/images/menu-icons/" + path.split("/")[-1],
        [path + "/LICENCES"] + glob(path + "/*.png"),
    )
    for path in glob("images/menu-icons/*")
]

packages = [
    "scc",
    "scc.drivers",
    "scc.lib",
    "scc.x11",
    "scc.osd",
    "scc.foreign",
    "scc.gui",
    "scc.gui.ae",
    "scc.gui.importexport",
    "scc.gui.creg",
]

extensions = [
    Extension("libuinput", sources=["scc/uinput.c"]),
    Extension(
        "libcemuhook",
        define_macros=[("PYTHON", 1)],
        sources=["scc/cemuhook_server.c"],
        libraries=["z"],
    ),
    Extension("libhiddrv", sources=["scc/drivers/hiddrv.c"]),
    Extension("libsc_by_bt", sources=["scc/drivers/sc_by_bt.c"]),
    Extension("libremotepad", sources=["scc/drivers/remotepad_controller.c"]),
]

setup(
    name="sccontroller",
    version=DAEMON_VERSION,
    description="Standalone controller mapping tool for Linux",
    author="SC Controller contributors",
    packages=packages,
    data_files=data_files,
    scripts=[
        "scripts/scc-daemon",
        "scripts/sc-controller",
        "scripts/scc",
        "scripts/scc-osd-dialog",
        "scripts/scc-osd-keyboard",
        "scripts/scc-osd-launcher",
        "scripts/scc-osd-menu",
        "scripts/scc-osd-message",
        "scripts/scc-osd-radial-menu",
        "scripts/scc-osd-show-bindings",
    ],
    license="GPL-2.0-only",
    platforms=["Linux"],
    python_requires=">=3.9",
    ext_modules=extensions,
)
