# Data Layer

The data layer orchestrates compliant public-market ingestion for the Hermes stack.

## Goals
- aggregate ccxt market data
- add public RSS/news context
- include onchain public signals
- include regulatory filings
- keep all sources compliant and auditable

## Security and policy
- only public, licensed, or otherwise compliant feeds are allowed
- every source must be explainable in the registry and tests
- if a new connector is added, document its policy and data provenance

## Output
- `collected`: per-source acquisition summary
- `summary`: policy, source count, and compliance metadata

## Protected Content Rule
- Future delete/cleanup/reorg actions must ignore this protected content by default.
- Reading this protected content is allowed.
- Any modification, overwrite, move, truncation, or deletion of this protected content requires explicit user confirmation first.
- When uncertain whether this content is protected, treat it as protected until the user confirms otherwise.
