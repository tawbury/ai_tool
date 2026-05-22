from __future__ import annotations

VALIDATORS_BY_KIND = {
    "agent": ["agent"],
    "skill": ["skill"],
    "workflow": ["workflow"],
    "validator-index": ["references"],
    "repository": ["agent", "skill", "workflow", "references"],
}
