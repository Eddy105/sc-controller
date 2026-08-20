# Troubleshooting

Use this guide to narrow down controller and daemon problems before opening an issue.

## 1. Confirm that Linux sees the controller

Check the kernel/device view first. For USB devices, inspect recent kernel messages after connecting the controller. For Bluetooth devices, confirm that the device is paired and connected.

Useful commands include:

```bash
lsusb
```

and:

```bash
journalctl -k --since "5 minutes ago"
```

The exact commands and output depend on the controller and connection method.

## 2. Check udev permissions

SC Controller may require udev rules to access controller devices without running the entire application as root.

If the controller is detected by the operating system but not by SC Controller, verify that the relevant rules are installed and that the device permissions have been reloaded.

Avoid solving permission problems by running the GUI permanently as root.

## 3. Check `/dev/uinput`

Virtual controller and input emulation paths can depend on Linux uinput support.

Check whether the device exists:

```bash
ls -l /dev/uinput
```

If it does not exist, inspect whether the kernel module and distribution configuration provide uinput.

## 4. Check the daemon

Run the daemon separately when diagnosing controller detection:

```bash
scc-daemon
```

Capture warnings, errors and tracebacks. A daemon log is usually more useful than a GUI-only symptom report.

## 5. Check for competing input software

Steam Input, another controller mapper or an existing SC Controller process can change device ownership or event routing.

For a clean test, close competing controller-mapping software and verify that only the intended SC Controller daemon is handling the device.

## 6. Check the profile

If the controller is detected but buttons or axes behave incorrectly:

- verify that the expected profile is selected
- test with a minimal/default profile
- check whether the problem is limited to one action or mode shift
- confirm that the affected controller is the one being configured

## 7. Report reproducible information

When opening an issue, include:

- controller model
- connection type
- Linux distribution and version
- Python version
- installation method
- whether Steam is running
- daemon output
- relevant `journalctl` output
- the profile or mapping involved, if applicable

Do not include private paths, tokens or unrelated personal information.
