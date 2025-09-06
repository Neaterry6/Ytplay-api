## 📘 `README.md`

```markdown
# 🎧 YouTube Downloader API

Minimal Flask API to search YouTube and return direct download URLs for audio or video using `yt-dlp`.

## 🔊 /play

**POST** `/play`

**Body:**
```json
{ "query": "baby girl by joeboy" }
```

**Response:**
```json
{
  "title": "...",
  "download_url": "...",
  "format": "mp3",
  "quality": "bestaudio",
  "type": "audio",
  "creator": "Broken Vzn"
}
```

## 🎥 /video

**POST** `/video`

**Body:**
```json
{ "query": "baby girl by joeboy" }
```

**Response:**
```json
{
  "title": "...",
  "download_url": "...",
  "format": "mp4",
  "quality": "best",
  "type": "video",
  "creator": "Broken Vzn"
}
```

## 🛠 Setup

```bash
pip install -r requirements.txt
python app.py
```
