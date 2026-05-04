# Oh My OpenCode

Minimal shell plugin for OpenCode.

## Features
- Adds `oc`, `oco`, and `opencode` helper aliases.
- Provides shell completion loading if available.
- Adds a small prompt helper for project-local OpenCode commands.

## Install
```bash
git clone <repo-url> ~/.oh-my-opencode
source ~/.oh-my-opencode/install.sh
```

Or source the main entry directly:
```bash
source ~/.oh-my-opencode/oh-my-opencode.sh
```

## Configuration
- `OPENCODE_BIN`: override the OpenCode binary path.
- `OPENCODE_PROJECT_DIR`: default project directory used by helpers.
