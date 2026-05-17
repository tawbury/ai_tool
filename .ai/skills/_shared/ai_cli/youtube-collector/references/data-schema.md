# YouTube Collector Data Schema

## Configuration File Structure

### User API Key

The API key is stored outside the codebase for security.

Paths:

- macOS/Linux: `~/.config/youtube-collector/config.yaml`
- Windows: `%APPDATA%\youtube-collector\config.yaml`

```yaml
api_key: "YOUR_YOUTUBE_DATA_API_KEY"
```

Configuration command:

```bash
python scripts/setup_api_key.py
```

### Project Data Directory

```text
.reference/
  youtube-config.yaml
  channels.yaml
  contents/
    {channel_handle}/
      {video_id}.yaml
```

## `youtube-config.yaml`

```yaml
default_language: "ko"
max_results: 10
```

Fields:

- `default_language`: Preferred transcript language. Default: `ko`.
- `max_results`: Maximum number of videos collected per channel. Default: `10`.

## `channels.yaml`

```yaml
channels:
  - id: "UCxxxxxxxxxxxxxxxxxxxxxx"
    handle: "@channelname"
    name: "Channel display name"
    added_at: "2025-12-13"
```

Fields:

- `id`: YouTube channel ID.
- `handle`: Channel handle.
- `name`: Human-readable channel name.
- `added_at`: Registration date.

## `contents/{channel_handle}/{video_id}.yaml`

```yaml
video_id: "abc123xyz"
title: "Video title"
published_at: "2025-12-10T10:00:00Z"
url: "https://youtube.com/watch?v=abc123xyz"
thumbnail: "https://i.ytimg.com/vi/abc123xyz/maxresdefault.jpg"
description: |
  Full video description text.
duration: "PT10M30S"
collected_at: "2025-12-13T15:00:00Z"
transcript:
  available: true
  language: "ko"
  text: |
    Full transcript text.
summary:
  source: "transcript"
  content: |
    ## Introduction
    - Topic and context.

    ## Body
    - Key details.
    - Methods, examples, or arguments.

    ## Conclusion
    - Main takeaway.
    - Implications or next steps.
```

## Without Transcript

```yaml
transcript:
  available: false
  language: null
  text: null
summary:
  source: "description"
  content: |
    Description-based summary content.
```

## Duplicate Prevention

- File names use `{video_id}.yaml`.
- The collector checks whether that file already exists before writing.
- Existing video IDs are skipped unless overwrite behavior is explicitly requested.
