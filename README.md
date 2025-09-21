# SC-Controller (Python 3 Fork)

This is a maintained fork of [kozec/sc-controller](https://github.com/kozec/sc-controller).

### Changes
- Ported to **Python 3**
- Tested on **Ubuntu 24.04**
- Various bugfixes and improvements
- just dont wanted to throw away the steam controller


### Installation (Ubuntu/Debian)
```bash
git clone https://github.com/Eddy105/sc-controller.git
cd sc-controller
./configure
make
sudo make install
```
### Quick Start
After installation, you can launch SC-Controller with:
```bash
sc-controller
```

- A tray icon should appear, allowing you to configure and manage your Steam Controller or other supported devices.
- If you want to run it in daemon mode (without the UI), use:
```bash
scc-daemon
```
- Configuration files are usually stored in ~/.config/scc/.

