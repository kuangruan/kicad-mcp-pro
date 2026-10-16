# Native KiCad Companion

This is the existing KiCad MCP Pro PCM integration, now using KiCad 10's IPC
plugin framework. One package identifier is retained for upgrades:
com.github.oaslananka.kicad-mcp-pro.

The PCM artifact and its SHA256SUMS/evidence are produced by the established
release tool:

    python scripts/build_kicad_pcm.py --output-dir /tmp/kicad-pcm --verify

An installed package contains plugin.json, companion.py, companion_core.py,
context.py, compatibility.json, requirements.txt and icon.png under plugins/.
KiCad provisions kicad-python into the plugin's isolated Python environment.

Click Open MCP Pro Companion in the PCB Editor toolbar. A modeless window
shows read-only board counts and the local backend state. The user can open
the existing dashboard or explicitly publish board context to the existing
MCP backend (using the versioned contract in context.py). No board mutations
or security-gate bypasses occur here.

Requirements: KiCad 10.x, IPC enabled, a graphical Python/Tkinter environment,
and the separately installed/running KiCad MCP Pro backend for dashboard or
context-sync actions. The UI does not silently launch or configure a server.

To install for development, put the package contents directly under a
subdirectory of the KiCad 10 IPC plugins directory, for example
~/.local/share/KiCad/10.0/plugins/kicad-mcp-pro (Linux). Production PCM
publication still requires live Windows/macOS/Linux acceptance; the updated
IPC package version is marked development pending that acceptance.

Reference: https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/
