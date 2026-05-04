# Gateway map

Current gateway-related paths kept in place:

- `vendor/hermes-webui/` — WebUI + gateway session sync reference
- `vendor/hermes-webui/api/gateway_watcher.py` — gateway session watcher
- `vendor/hermes-webui/tests/test_gateway_sync.py` — gateway sync verification
- `vendor/github-inspect/MarketBot/marketbot/cli/gateway_runtime.py` — gateway runtime reference
- `vendor/github-inspect/MarketBot/tests/test_cli_gateway_runtime.py` — runtime tests
- `hermes/dashboard/pages/trading_orchestrator.html` — dashboard surface mentioning gateway flow
- `tests/test_trading_orchestrator_layout.py` — local check asserting gateway visibility

This file was added during repo cleanup so gateway references are easier to locate without moving vendor sources.
