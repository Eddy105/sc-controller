# Development Guide

SC Controller is a Linux-focused controller mapping project built primarily in Python, with native components and desktop integration around GTK3, udev and Linux input facilities.

## Before changing code

1. Read the relevant documentation in `docs/`.
2. Identify the controller driver, mapping path or GUI component affected by the change.
3. Check whether the behavior is inherited from upstream or specific to this fork.
4. Prefer a focused change over broad unrelated refactoring.

## Local development

Clone the repository and work from a dedicated branch:

```bash
git clone https://github.com/Eddy105/sc-controller.git
cd sc-controller
git switch -c feature/my-change
```

Use a Python 3 environment for development. The exact native dependencies depend on the Linux distribution and the part of the application being exercised.

## Hardware testing

Controller software should be tested with real hardware whenever a change affects input handling.

Record at least:

- controller model
- wired or wireless connection
- Linux distribution and release
- Python version
- GTK/PyGObject version where relevant
- daemon output or traceback
- whether Steam or another input mapper is running

## Areas that deserve extra care

### Drivers

Driver changes can affect device detection, permissions, input events and lifecycle handling. Test both connect and disconnect paths.

### Mapping

Mapping changes should be tested with buttons, axes, pads and any affected modifiers or mode shifts. Check that existing profiles continue to load.

### uinput / virtual devices

Changes involving `/dev/uinput` or virtual controller output require Linux-level testing. A working GUI does not necessarily mean virtual output is working.

### GUI and OSD

GTK and OSD changes should be checked on a normal desktop session and with the daemon running independently where possible.

## Documentation changes

When behavior changes, update the relevant documentation in the same change. Do not document an intended future feature as if it were already implemented.

## Pull requests

A useful pull request should explain:

- what changed
- why it changed
- how it was tested
- what hardware/platform was used
- any known limitations

Keep commits and pull requests focused so that regressions can be isolated easily.
