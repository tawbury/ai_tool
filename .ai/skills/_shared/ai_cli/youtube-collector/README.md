# YouTube Collector Skill

Register YouTube channels, collect recent video metadata and transcripts, and prepare summary-ready YAML files.

## Main Features

- **Channel registration**: Register and manage YouTube channels.
- **Content collection**: Collect recent video metadata from registered channels.
- **Transcript collection**: Fetch transcripts when available.
- **Summary preparation**: Store transcript or description data for AI-generated summaries.
- **Duplicate prevention**: Skip already collected videos by video ID.

## Initial Setup

### 1. Install Dependencies

```bash
pip install google-api-python-client youtube-transcript-api pyyaml
```

### 2. Configure API Key

```bash
python scripts/setup_api_key.py
```

## Example Prompts

### Register Channels

```text
Register YouTube channel @channelname.
```

```text
Register this YouTube channel: https://youtube.com/@examplechannel
```

```text
Register these channels:
- @channel1
- @channel2
- @channel3
```

### Collect Content

```text
Collect new videos from registered YouTube channels.
```

```text
Collect the latest 5 videos from YouTube channel @channelname.
```

```text
Check all registered channels for new content and collect it.
```

### Inspect Collected Data

```text
Show collected YouTube content.
```

```text
Show videos collected from @channelname.
```

```text
Show summaries for recently collected videos.
```

### Manage Channels

```text
Show registered YouTube channels.
```

```text
Remove @channelname from registered channels.
```

### Manage API Key

```text
Check YouTube API key configuration.
```

```text
Set a new YouTube API key.
```

## Data Locations

| Data | Path |
|---|---|
| API key | `~/.config/youtube-collector/config.yaml` |
| Project config | `.reference/youtube-config.yaml` |
| Registered channels | `.reference/channels.yaml` |
| Collected content | `.reference/contents/{channel}/` |

## Scripts

| Script | Purpose |
|---|---|
| `setup_api_key.py` | Configure the API key. |
| `fetch_videos.py` | Fetch a channel video list. |
| `fetch_transcript.py` | Fetch video transcripts. |
| `register_channel.py` | Register a YouTube channel. |
| `collect_videos.py` | Collect video metadata and transcripts into YAML files. |
