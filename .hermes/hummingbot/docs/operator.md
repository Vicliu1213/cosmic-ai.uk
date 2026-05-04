# Operator Notes

## Safe start
1. Install Hummingbot source into `vendor/hummingbot`.
2. Configure paper trading.
3. Validate connectors and balances.
4. Run a dry-run session.
5. Promote only after checklist approval.

## Hermes boundary
- Hermes decides intent and risk.
- Hummingbot executes exchange-facing workflows.
- Memory and verification stay in Hermes.
