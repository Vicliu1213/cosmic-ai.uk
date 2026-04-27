# MCP and Agents Registration

This repository registers agent tool access through `platform_toolsets.cli` and `tools.mcp_servers`.

## Registered tools
- `terminal`
- `file`
- `web`
- `browser`
- `memory`
- `todo`
- `skills`
- `session_search`
- `mcp_hermes_webui`

## MCP server
- `hermes_webui` at `http://127.0.0.1:8787/mcp`

## Notes
- Web UI toolsets merge MCP servers automatically when `hermes_cli` is available.
- CLI runtime passes `tools.mcp_servers` into the agent loop.

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
