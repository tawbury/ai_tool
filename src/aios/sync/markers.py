from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


MARKER_VERSION = "0"
STYLE_MARKDOWN = "markdown-html-comment"
STYLE_HASH = "hash-line-comment"
STYLE_YAML = "yaml-line-comment"
SUPPORTED_STYLES = {STYLE_MARKDOWN, STYLE_HASH, STYLE_YAML}

KIND_BEGIN = "begin"
KIND_END = "end"
KIND_ANCHOR = "anchor"

INTEGRITY_VALID = "valid"
INTEGRITY_BEGIN_MISSING = "begin-missing"
INTEGRITY_END_MISSING = "end-missing"
INTEGRITY_BEGIN_DUPLICATED = "begin-duplicated"
INTEGRITY_END_DUPLICATED = "end-duplicated"
INTEGRITY_MALFORMED = "marker-malformed"
INTEGRITY_NESTED = "marker-nested"
INTEGRITY_ENTRY_ID_MISMATCH = "entry-id-mismatch"
INTEGRITY_VERSION_UNSUPPORTED = "marker-version-unsupported"
INTEGRITY_NOT_EXPECTED = "not-expected"
INTEGRITY_ANCHOR_MISSING = "anchor-missing"
INTEGRITY_ANCHOR_DUPLICATED = "anchor-duplicated"
INTEGRITY_ANCHOR_IN_CODE_FENCE = "anchor-in-code-fence"
INTEGRITY_CODE_FENCE_AMBIGUOUS = "code-fence-ambiguous"

_MARKDOWN_RE = re.compile(r"^<!--\s*AIOS:(BEGIN|END|ANCHOR)\s+managed-block\s+(.+?)\s*-->$")
_HASH_RE = re.compile(r"^#\s*AIOS:(BEGIN|END|ANCHOR)\s+managed-block\s+(.+?)\s*$")
_ATTR_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)=([^\s>]+)")


@dataclass(frozen=True)
class MarkerEvent:
    kind: Literal["begin", "end", "anchor"]
    line: int
    raw: str
    style: str
    entry_id: str | None
    marker_version: str | None
    malformed: bool = False
    in_code_fence: bool = False


@dataclass(frozen=True)
class MarkerBlock:
    entry_id: str | None
    marker_version: str | None
    marker_style: str | None
    integrity: str
    begin_line: int | None = None
    end_line: int | None = None
    content_line_start: int | None = None
    content_line_end: int | None = None
    problems: list[str] = field(default_factory=list)
    orphan: bool = False
    nested: bool = False
    duplicate: bool = False

    @property
    def valid(self) -> bool:
        return self.integrity == INTEGRITY_VALID


@dataclass(frozen=True)
class AnchorRecord:
    entry_id: str | None
    marker_version: str | None
    marker_style: str | None
    integrity: str
    line: int | None = None
    problems: list[str] = field(default_factory=list)
    in_code_fence: bool = False
    duplicate: bool = False

    @property
    def valid(self) -> bool:
        return self.integrity == INTEGRITY_VALID


@dataclass(frozen=True)
class MarkerParseResult:
    blocks: list[MarkerBlock]
    anchors: list[AnchorRecord]
    problems: list[str] = field(default_factory=list)
    ignored_code_fence_markers: int = 0

    @property
    def valid_blocks(self) -> list[MarkerBlock]:
        return [block for block in self.blocks if block.valid]


def parse_marker_file(
    path: Path,
    expected_entry_ids: set[str] | None = None,
    expected_anchor_entry_ids: set[str] | None = None,
) -> MarkerParseResult:
    style_hint = STYLE_YAML if path.suffix.lower() in {".yaml", ".yml"} else None
    return parse_marker_text(
        path.read_text(encoding="utf-8"),
        expected_entry_ids=expected_entry_ids,
        expected_anchor_entry_ids=expected_anchor_entry_ids,
        marker_style_hint=style_hint,
    )


def parse_marker_text(
    text: str,
    expected_entry_ids: set[str] | None = None,
    expected_anchor_entry_ids: set[str] | None = None,
    marker_style_hint: str | None = None,
) -> MarkerParseResult:
    expected = expected_entry_ids or set()
    expected_anchors = expected_anchor_entry_ids or set()
    events, ignored, fence_ambiguous = _scan_events(text, marker_style_hint=marker_style_hint)
    blocks = _pair_marker_events([event for event in events if event.kind != KIND_ANCHOR], expected)
    anchors = _classify_anchors([event for event in events if event.kind == KIND_ANCHOR], expected_anchors)
    problems: list[str] = []
    if fence_ambiguous:
        problems.append(INTEGRITY_CODE_FENCE_AMBIGUOUS)
    return MarkerParseResult(
        blocks=blocks,
        anchors=anchors,
        problems=problems,
        ignored_code_fence_markers=ignored,
    )


def _scan_events(text: str, marker_style_hint: str | None = None) -> tuple[list[MarkerEvent], int, bool]:
    events: list[MarkerEvent] = []
    ignored = 0
    in_fence = False
    fence_ambiguous = False
    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        event = _parse_marker_line(stripped, line_no, in_code_fence=in_fence, marker_style_hint=marker_style_hint)
        if event is None:
            continue
        if in_fence and event.kind != KIND_ANCHOR:
            ignored += 1
            continue
        events.append(event)
    if in_fence:
        fence_ambiguous = True
    return events, ignored, fence_ambiguous


def _parse_marker_line(
    line: str,
    line_no: int,
    in_code_fence: bool,
    marker_style_hint: str | None = None,
) -> MarkerEvent | None:
    if "AIOS:" not in line:
        return None
    style = _detect_style(line, marker_style_hint=marker_style_hint)
    if style is None:
        return MarkerEvent(
            kind=KIND_BEGIN,
            line=line_no,
            raw=line,
            style="unknown",
            entry_id=None,
            marker_version=None,
            malformed=True,
            in_code_fence=in_code_fence,
        )
    pattern = _MARKDOWN_RE if style == STYLE_MARKDOWN else _HASH_RE
    match = pattern.match(line)
    if not match:
        return MarkerEvent(
            kind=KIND_BEGIN,
            line=line_no,
            raw=line,
            style=style,
            entry_id=None,
            marker_version=None,
            malformed=True,
            in_code_fence=in_code_fence,
        )
    kind = match.group(1).lower()
    attrs = dict(_ATTR_RE.findall(match.group(2)))
    return MarkerEvent(
        kind=kind,  # type: ignore[arg-type]
        line=line_no,
        raw=line,
        style=style,
        entry_id=attrs.get("entry_id"),
        marker_version=attrs.get("marker_version"),
        malformed="entry_id" not in attrs or "marker_version" not in attrs,
        in_code_fence=in_code_fence,
    )


def _detect_style(line: str, marker_style_hint: str | None = None) -> str | None:
    if line.startswith("<!--"):
        return STYLE_MARKDOWN
    if line.startswith("#"):
        # YAML and hash-line comments have the same text syntax. The parser can
        # classify exact intent later from manifest metadata; source text alone
        # is safely represented as hash-line-comment.
        if marker_style_hint in {STYLE_HASH, STYLE_YAML}:
            return marker_style_hint
        return STYLE_HASH
    return None


def _pair_marker_events(events: list[MarkerEvent], expected_entry_ids: set[str]) -> list[MarkerBlock]:
    blocks: list[MarkerBlock] = []
    open_event: MarkerEvent | None = None
    begin_counts: dict[str, int] = {}
    end_counts: dict[str, int] = {}
    for event in events:
        if event.malformed:
            blocks.append(_problem_block(event, INTEGRITY_MALFORMED, [INTEGRITY_MALFORMED]))
            continue
        if event.marker_version != MARKER_VERSION:
            blocks.append(_problem_block(event, INTEGRITY_VERSION_UNSUPPORTED, [INTEGRITY_VERSION_UNSUPPORTED]))
            continue
        entry_id = event.entry_id or ""
        if event.kind == KIND_BEGIN:
            begin_counts[entry_id] = begin_counts.get(entry_id, 0) + 1
            if open_event is not None:
                blocks.append(
                    MarkerBlock(
                        entry_id=open_event.entry_id,
                        marker_version=open_event.marker_version,
                        marker_style=open_event.style,
                        integrity=INTEGRITY_NESTED,
                        begin_line=open_event.line,
                        end_line=event.line,
                        problems=[INTEGRITY_NESTED],
                        orphan=_is_orphan(open_event.entry_id, expected_entry_ids),
                        nested=True,
                    )
                )
            open_event = event
            continue
        end_counts[entry_id] = end_counts.get(entry_id, 0) + 1
        if open_event is None:
            blocks.append(_problem_block(event, INTEGRITY_BEGIN_MISSING, [INTEGRITY_BEGIN_MISSING]))
            continue
        if open_event.entry_id != event.entry_id:
            blocks.append(
                MarkerBlock(
                    entry_id=open_event.entry_id,
                    marker_version=open_event.marker_version,
                    marker_style=open_event.style,
                    integrity=INTEGRITY_ENTRY_ID_MISMATCH,
                    begin_line=open_event.line,
                    end_line=event.line,
                    problems=[INTEGRITY_ENTRY_ID_MISMATCH],
                    orphan=_is_orphan(open_event.entry_id, expected_entry_ids),
                )
            )
            open_event = None
            continue
        blocks.append(
            MarkerBlock(
                entry_id=open_event.entry_id,
                marker_version=open_event.marker_version,
                marker_style=open_event.style,
                integrity=INTEGRITY_VALID,
                begin_line=open_event.line,
                end_line=event.line,
                content_line_start=open_event.line + 1,
                content_line_end=max(open_event.line + 1, event.line - 1),
                orphan=_is_orphan(open_event.entry_id, expected_entry_ids),
            )
        )
        open_event = None
    if open_event is not None:
        blocks.append(_problem_block(open_event, INTEGRITY_END_MISSING, [INTEGRITY_END_MISSING]))

    duplicate_entries = {
        entry_id
        for entry_id in set(begin_counts) | set(end_counts)
        if begin_counts.get(entry_id, 0) > 1 or end_counts.get(entry_id, 0) > 1
    }
    if duplicate_entries:
        blocks = [_mark_duplicate(block, begin_counts, end_counts) for block in blocks]
    return sorted(blocks, key=lambda block: (block.begin_line or block.end_line or 0, block.entry_id or ""))


def _classify_anchors(events: list[MarkerEvent], expected_anchor_entry_ids: set[str]) -> list[AnchorRecord]:
    anchors: list[AnchorRecord] = []
    counts: dict[str, int] = {}
    for event in events:
        entry_id = event.entry_id or ""
        counts[entry_id] = counts.get(entry_id, 0) + 1
        if event.in_code_fence:
            anchors.append(
                AnchorRecord(
                    entry_id=event.entry_id,
                    marker_version=event.marker_version,
                    marker_style=event.style,
                    integrity=INTEGRITY_ANCHOR_IN_CODE_FENCE,
                    line=event.line,
                    problems=[INTEGRITY_ANCHOR_IN_CODE_FENCE],
                    in_code_fence=True,
                )
            )
            continue
        if event.malformed:
            anchors.append(
                AnchorRecord(
                    entry_id=event.entry_id,
                    marker_version=event.marker_version,
                    marker_style=event.style,
                    integrity=INTEGRITY_MALFORMED,
                    line=event.line,
                    problems=[INTEGRITY_MALFORMED],
                )
            )
            continue
        if event.marker_version != MARKER_VERSION:
            anchors.append(
                AnchorRecord(
                    entry_id=event.entry_id,
                    marker_version=event.marker_version,
                    marker_style=event.style,
                    integrity=INTEGRITY_VERSION_UNSUPPORTED,
                    line=event.line,
                    problems=[INTEGRITY_VERSION_UNSUPPORTED],
                )
            )
            continue
        anchors.append(
            AnchorRecord(
                entry_id=event.entry_id,
                marker_version=event.marker_version,
                marker_style=event.style,
                integrity=INTEGRITY_VALID,
                line=event.line,
            )
        )
    anchors = [_mark_duplicate_anchor(anchor, counts) for anchor in anchors]
    for entry_id in sorted(expected_anchor_entry_ids):
        if counts.get(entry_id, 0) == 0:
            anchors.append(
                AnchorRecord(
                    entry_id=entry_id,
                    marker_version=None,
                    marker_style=None,
                    integrity=INTEGRITY_ANCHOR_MISSING,
                    problems=[INTEGRITY_ANCHOR_MISSING],
                )
            )
    return sorted(anchors, key=lambda anchor: (anchor.line or 10**9, anchor.entry_id or ""))


def _problem_block(event: MarkerEvent, integrity: str, problems: list[str]) -> MarkerBlock:
    return MarkerBlock(
        entry_id=event.entry_id,
        marker_version=event.marker_version,
        marker_style=event.style,
        integrity=integrity,
        begin_line=event.line if event.kind == KIND_BEGIN else None,
        end_line=event.line if event.kind == KIND_END else None,
        problems=problems,
    )


def _mark_duplicate(block: MarkerBlock, begin_counts: dict[str, int], end_counts: dict[str, int]) -> MarkerBlock:
    entry_id = block.entry_id or ""
    problems = list(block.problems)
    integrity = block.integrity
    duplicate = False
    if begin_counts.get(entry_id, 0) > 1:
        duplicate = True
        if INTEGRITY_BEGIN_DUPLICATED not in problems:
            problems.append(INTEGRITY_BEGIN_DUPLICATED)
        if block.valid:
            integrity = INTEGRITY_BEGIN_DUPLICATED
    if end_counts.get(entry_id, 0) > 1:
        duplicate = True
        if INTEGRITY_END_DUPLICATED not in problems:
            problems.append(INTEGRITY_END_DUPLICATED)
        if block.valid:
            integrity = INTEGRITY_END_DUPLICATED
    return MarkerBlock(
        entry_id=block.entry_id,
        marker_version=block.marker_version,
        marker_style=block.marker_style,
        integrity=integrity,
        begin_line=block.begin_line,
        end_line=block.end_line,
        content_line_start=block.content_line_start,
        content_line_end=block.content_line_end,
        problems=problems,
        orphan=block.orphan,
        nested=block.nested,
        duplicate=duplicate,
    )


def _mark_duplicate_anchor(anchor: AnchorRecord, counts: dict[str, int]) -> AnchorRecord:
    entry_id = anchor.entry_id or ""
    if counts.get(entry_id, 0) <= 1:
        return anchor
    problems = list(anchor.problems)
    if INTEGRITY_ANCHOR_DUPLICATED not in problems:
        problems.append(INTEGRITY_ANCHOR_DUPLICATED)
    return AnchorRecord(
        entry_id=anchor.entry_id,
        marker_version=anchor.marker_version,
        marker_style=anchor.marker_style,
        integrity=INTEGRITY_ANCHOR_DUPLICATED,
        line=anchor.line,
        problems=problems,
        in_code_fence=anchor.in_code_fence,
        duplicate=True,
    )


def _is_orphan(entry_id: str | None, expected_entry_ids: set[str]) -> bool:
    return bool(expected_entry_ids and entry_id and entry_id not in expected_entry_ids)
