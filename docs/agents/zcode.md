# ZCode Integration

[ZCode](https://zcode.dev) connects to MCP servers from its configuration files. Servers
are declared under the nested `mcp.servers` block, per scope:

| Scope | File | Use |
|-------|------|-----|
| User | `~/.zcode/cli/config.json` | Applies to every workspace. |
| Workspace | `<project>/.zcode/config.json` | Applies only to that project; safe to commit for a team. |

Both scopes connect automatically at session start; no manual trust step is required.

## Quick Start

```bash
kicad-mcp-pro setup zcode --write --scope user
```

Or edit the file directly and add:

```json
{
  "mcp": {
    "servers": {
      "kicad": {
        "type": "stdio",
        "command": "uvx",
        "args": ["kicad-mcp-pro"],
        "env": {
          "KICAD_MCP_PROJECT_DIR": "/absolute/path/to/your/kicad-project",
          "KICAD_MCP_PROFILE": "default",
          "KICAD_MCP_OPERATING_MODE": "readonly"
        }
      }
    }
  }
}
```

Ready-to-copy: [`docs/examples/clients/zcode.config.json`](../examples/clients/zcode.config.json).

A remote (HTTP) server uses `url` instead of `command`:

```json
{ "mcp": { "servers": { "kicad": { "type": "http", "url": "http://127.0.0.1:8765/mcp" } } } }
```

## ZCode configuration notes

- The configuration schema is **strict**: an unknown key causes the server entry to be
  dropped. Use the canonical fields (`type`, `command`, `args`, `env`, `enabled`,
  `timeoutMs`).
- `${...}` templates are **not** expanded in configuration files — use absolute paths.
  `setup zcode` writes the resolved absolute path of `uvx` because a GUI-launched session
  may not inherit `~/.local/bin` from your shell PATH.
- Existing keys in `~/.zcode/cli/config.json` (hooks, plugins, skill overrides) are
  preserved; only `mcp.servers.kicad` is added or replaced.

## Project targeting

- With `KICAD_MCP_PROJECT_DIR` set to an absolute path, that directory is the default
  project for every session using this config.
- Without it, the server falls back to its working directory (open the KiCad project
  folder as the ZCode workspace), or call the `kicad_set_project()` tool mid-session.
- For one fixed project, prefer a workspace config at `<project>/.zcode/config.json`
  over pinning the user config.

## Verification

```bash
kicad-mcp-pro doctor
```

`agent_config_zcode_user: ok` confirms the file parsed. In the client, **Settings → MCP**
shows the server as connected, and restarting the ZCode session reloads the tool list.

## KiCad live connection (IPC)

The review and export tools run through `kicad-cli` and work with KiCad closed. Live board
reads/writes (applied edits, board screenshots) also need KiCad's IPC API:

1. In KiCad: **Preferences → Plugins → "Enable KiCad API"** (KiCad 9/10).
2. Keep KiCad running with the board open while using live tools.
3. Non-default sockets or tokens are passed via `KICAD_API_SOCKET` / `KICAD_API_TOKEN`.

## Example Prompt

> Use the kicad MCP server. Inspect this KiCad project, run DRC and ERC, and summarize the
> results. Do not modify any files.
