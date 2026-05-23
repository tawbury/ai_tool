from __future__ import annotations

VALIDATORS_BY_KIND = {
    "activation": ["activation"],
    "agent": ["agent"],
    "skill": ["skill"],
    "sync-manifest": ["sync-manifest"],
    "workflow": ["workflow"],
    "validator-index": ["references"],
    "repository": ["activation", "agent", "skill", "workflow", "references"],
}
