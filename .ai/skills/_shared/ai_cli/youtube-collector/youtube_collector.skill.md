---
name: youtube-collector
description: Register YouTube channels, collect video metadata and transcripts, and prepare YAML data for summary generation. Use when the user asks to manage YouTube channel collection, fetch recent videos, fetch transcripts, or summarize collected YouTube content.
---

# YouTube Collector

Collect YouTube channel content and prepare transcript or description based summary data.

## Requirements

Install Python dependencies before running collection scripts:

```bash
pip install google-api-python-client youtube-transcript-api pyyaml
```

Configure the YouTube Data API key:

```bash
python scripts/setup_api_key.py
```

## Scripts

| Script | Purpose |
|---|---|
| `scripts/setup_api_key.py` | Store or show the YouTube API key configuration. |
| `scripts/register_channel.py` | Register a channel by handle, URL, or channel ID. |
| `scripts/collect_videos.py` | Fetch videos, metadata, transcripts, and write YAML content files. |
| `scripts/fetch_videos.py` | Fetch video metadata from the YouTube API. |
| `scripts/fetch_transcript.py` | Fetch transcripts when available. |

## Workflow

1. Register a channel into a chosen output directory.
2. Collect recent videos for a specific channel or all registered channels.
3. Review generated YAML files.
4. Add or generate summaries using transcript text when available.
5. Fall back to description-based summaries when transcripts are unavailable.

## Example Commands

Register a channel:

```bash
python scripts/register_channel.py --channel-handle @channelname --output-dir .reference/
```

Collect videos:

```bash
python scripts/collect_videos.py --channel-handle @channelname --output-dir .reference/ --max-results 10
```

Collect all registered channels:

```bash
python scripts/collect_videos.py --all --output-dir .reference/
```

## Data Schema

Read `references/data-schema.md` when validating or editing generated YAML files.

## Safety

- Do not commit API keys or credential files.
- Store API keys in user configuration, not repository files.
- Respect YouTube API quotas and report quota failures clearly.
