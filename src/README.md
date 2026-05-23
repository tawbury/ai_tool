# Source Directory

This directory contains the AIOS Python runtime implementation.

## Structure

| Path | Purpose |
|---|---|
| `aios/` | Runtime package for `python -m aios`. |
| `aios/semantic_loader/` | Semantic context extraction and budget-aware loading. |
| `aios/validate/` | Validation target discovery and validators. |

## Boundary

The current runtime is read-only. It supports inspect, inventory, validate, activation checks, context loading, and opt-in command result envelope v2 output.
