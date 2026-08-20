# SC Controller — Python 3 Fork

[![License: GPL-2.0](https://img.shields.io/badge/license-GPL--2.0-blue.svg)](LICENSE)
[![Platform: Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://github.com/Eddy105/sc-controller)
[![Python: 3](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)

A maintained **Python 3 fork of [kozec/sc-controller](https://github.com/kozec/sc-controller)** — a Linux user-mode controller driver, input mapper and GTK3-based configuration interface for the Steam Controller and related devices.

This fork exists to keep the Python implementation usable on modern Linux systems and to provide a clean foundation for continued maintenance and modernization.

> **Project status:** Active modernization / maintenance fork. Compatibility claims are intentionally limited to platforms and configurations that have been tested.

## Why this fork?

The original SC Controller project is a substantial and capable Linux controller-mapping application, but its Python implementation was built around an older Python stack. This fork focuses on bringing that codebase forward without throwing away the mature mapping, profile and controller-handling functionality that already exists.

Current work includes:

- Python 3 port and compatibility work
- Modern Linux compatibility, including Ubuntu 24.04 testing
- Bug fixes and maintenance
- Documentation and developer experience improvements
- A foundation for future packaging, CI and release automation

## Features

SC Controller provides a graphical and daemon-based environment for configuring controller input. Depending on the connected device and current implementation support, the project includes functionality inherited from the upstream codebase such as:

- Controller profiles and profile switching
- Stick, pad and gyroscope input mapping
- Haptic feedback and rumble handling
- On-screen display and on-screen keyboard components
- Menus and configurable actions
- Macros, mode shifts and other advanced mappings
- Keyboard and mouse emulation
- Virtual controller output through Linux input facilities
- A background daemon for controller handling

See the existing technical documentation in [`docs/`](docs/) for the profile, action, menu and protocol formats.

## Installation

### Ubuntu / Debian

The repository currently contains the historical build/install workflow as well as the Python 3 fork changes. **Do not assume that every upstream build instruction applies unchanged to this fork.** The build system is being modernized as part of the project roadmap.

Clone the repository:

```bash
git clone https://github.com/Eddy105/sc-controller.git
cd sc-controller
```

Before installing system-wide, review the platform-specific dependencies and the current state of the build configuration for your distribution.

### Running the application

When the installation provides the project scripts, the main GUI entry point is:

```bash
sc-controller
```

The background daemon can be started with:

```bash
scc-daemon
```

Configuration is normally stored below:

```text
~/.config/scc/
```

## Architecture at a glance

SC Controller is split into several logical areas:

```text
Controller hardware
       │
       ▼
  Device drivers
       │
       ▼
 Input / action layer
       │
       ├──────────────► Profile & configuration data
       │
       ▼
   Output mapping
       │
       ├── keyboard / mouse
       ├── virtual game controller
       └── OSD / menus
       │
       ▼
     GUI / daemon
```

The repository contains driver code, mapping logic, GUI components, OSD functionality, profiles, menus, native Linux integration and packaging/build assets.

## Documentation

The project has more documentation than the original README exposed. Start here:

- [Documentation overview](docs/README.md)
- [Actions](docs/actions.md)
- [Profile file format](docs/profile-file.md)
- [Menu file format](docs/menu-file.md)
- [Protocol](docs/protocol.md)
- [Development and contribution guide](docs/development.md)
- [Troubleshooting](docs/troubleshooting.md)

## Development

The project is primarily Python with native Linux components. Some functionality relies on system integration such as udev and `/dev/uinput`, while the graphical interface is based on GTK3.

For development work:

1. Clone the repository.
2. Create an isolated Python environment where appropriate.
3. Install the dependencies required by your Linux distribution.
4. Run the application from the checkout while developing.
5. Test controller detection, profile loading and the affected mapping path before submitting changes.

See [`docs/development.md`](docs/development.md) for the development workflow and project conventions.

## Compatibility

The primary target is **Linux**.

The fork has specifically been tested on **Ubuntu 24.04**. Other distributions may work, but support should be considered dependent on the available GTK, Python, input and udev stack.

Controller support is device- and driver-dependent. If a controller is not explicitly documented as tested in this fork, treat support as experimental and report the device model, connection method and relevant logs when opening an issue.

## Troubleshooting

If the application starts but a controller is not usable, check these areas first:

- Is the controller visible to Linux?
- Are the required udev permissions installed?
- Can the user access the required input device interfaces?
- Is `/dev/uinput` available?
- Does the daemon detect the controller?
- Is an old SC Controller / Steam Input process competing for the device?
- Does the selected profile match the detected controller?

See [`docs/troubleshooting.md`](docs/troubleshooting.md) for a structured diagnostic checklist.

## Roadmap

The modernization roadmap is intentionally incremental:

- [ ] Complete Python 3 compatibility audit
- [ ] Modernize packaging and installation
- [ ] Add reliable automated tests for core mapping logic
- [ ] Add GitHub Actions CI
- [ ] Establish reproducible Linux builds
- [ ] Improve controller detection diagnostics
- [ ] Improve release/version management
- [ ] Expand distribution/package documentation
- [ ] Continue cleaning up legacy build and compatibility code

The roadmap may change as real hardware testing identifies higher-priority work.

## Relationship to upstream

This repository is a fork of [kozec/sc-controller](https://github.com/kozec/sc-controller).

The goal is not to obscure the project's history. Upstream authors, contributors and third-party licenses remain important to the project. See [`LICENSE`](LICENSE) and [`ADDITIONAL-LICENSES`](ADDITIONAL-LICENSES).

## Contributing

Contributions are welcome, especially when they include:

- a clear description of the problem
- reproducible steps
- controller model and connection method
- Linux distribution and version
- Python / GTK versions where relevant
- logs or tracebacks when available
- a focused change rather than unrelated cleanup

Please read [`docs/development.md`](docs/development.md) before submitting larger changes.

## License

SC Controller is distributed under the **GNU General Public License v2.0**. See [`LICENSE`](LICENSE) for the full license text and [`ADDITIONAL-LICENSES`](ADDITIONAL-LICENSES) for additional licensing information.

## Credits

This fork builds on the work of the original SC Controller project and its contributors. See the upstream repository for the project's broader history and contributor base:

https://github.com/kozec/sc-controller
