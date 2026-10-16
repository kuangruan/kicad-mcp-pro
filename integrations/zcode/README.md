# ZCode — KiCad MCP Integration

Connect [ZCode](https://zcode.dev) to your local KiCad projects via the `kicad-mcp-pro` MCP server.

## Quick Install

```bash
kicad-mcp-pro setup zcode --write --scope user
```

Or manually:

- **User scope (all workspaces):** `~/.zcode/cli/config.json`
- **Workspace scope (one project):** `<project>/.zcode/config.json`

1. Copy `zcode.config.example.json` into the file for the scope you want.
2. Replace `KICAD_MCP_PROJECT_DIR` with the absolute path to your KiCad project
   (or remove the key and open the project folder as the ZCode workspace instead).
3. Restart the ZCode session so the server connects.

## Verification

```bash
kicad-mcp-pro doctor
```

`agent_config_zcode_user: ok` confirms the config parsed; **Settings → MCP** in ZCode shows
the connected server. For live board interaction also enable **Preferences → Plugins →
"Enable KiCad API"** inside KiCad.

## Notes

- ZCode's config schema is strict — only the canonical fields (`type`, `command`, `args`,
  `env`, `enabled`, `timeoutMs`) are accepted, and `${...}` templates are not expanded in
  configuration files.
- `setup zcode` preserves unrelated keys already present in the config file (hooks,
  plugins, skill overrides).

See `docs/agents/zcode.md` for the full guide.
