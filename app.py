from flask import Flask, jsonify, request
import yt_dlp
import urllib.parse
import requests
from functools import lru_cache

app = Flask(__name__)

def shorten_url(long_url):
    try:
        response = requests.get(f"https://is.gd/create.php?format=simple&url={long_url}", timeout=2)
        return response.text if response.status_code == 200 else long_url
    except Exception:
        return long_url

@lru_cache(maxsize=100)
def fetch_video_info(query, media_type):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'cookiefile': 'cookies.txt',
        'default_search': 'ytsearch1',
        'forcejson': True,
        'noplaylist': True,
        'force_ipv4': True,
        'socket_timeout': 5,
        'format': (
            'bestaudio[ext=m4a]/bestaudio' if media_type == 'audio'
            else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
        )
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(query, download=False)
            if 'entries' in result and result['entries']:
                return result['entries'][0]
            return None
        except Exception:
            return None

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Broken Vzn's YouTube API",
        "usage": "/play/<query>?format=audio|video",
        "creator": "Broken Vzn"
    })

@app.route('/play/<path:query>')
def play(query):
    media_type = request.args.get('format', 'video').lower()
    decoded_query = urllib.parse.unquote(query)

    info = fetch_video_info(decoded_query, media_type)

    # Fallback to direct YouTube URL if search fails
    if not info or not info.get("url"):
        fallback_url = "https://www.youtube.com/watch?v=HA1srD2DwaI"  # Juice WRLD – Burn
        try:
            with yt_dlp.YoutubeDL({
                'quiet': True,
                'skip_download': True,
                'forcejson': True,
                'noplaylist': True,
                'format': (
                    'bestaudio[ext=m4a]/bestaudio' if media_type == 'audio'
                    else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
                )
            }) as ydl:
                info = ydl.extract_info(fallback_url, download=False)
        except Exception:
            info = None

    if not info or not info.get("url"):
        return jsonify({
            "title": decoded_query,
            "download_url": None,
            "video_url": None,
            "thumbnail": None,
            "duration": None,
            "channel_name": None,
            "publish_date": None,
            "views": None,
            "likes": None,
            "description": None,
            "format": "mp3" if media_type == "audio" else "mp4",
            "quality": None,
            "type": media_type,
            "creator": "Broken Vzn",
            "error": "No video found"
        }), 404

    short_url = shorten_url(info.get("url"))
    video_url = f"https://www.youtube.com/watch?v={info.get('id')}" if info.get("id") else None
    channel_name = info.get("channel") or info.get("channel_id") or None
    publish_date = info.get("upload_date")
    if publish_date:
        publish_date = f"{publish_date[:4]}-{publish_date[4:6]}-{publish_date[6:]}"  # Format YYYY-MM-DD

    return jsonify({
        "title": info.get("title"),
        "download_url": short_url,
        "video_url": video_url,
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "channel_name": channel_name,
        "publish_date": publish_date,
        "views": info.get("view_count"),
        "likes": info.get("like_count"),
        "description": info.get("description"),
        "format": "mp3" if media_type == "audio" else "mp4",
        "quality": info.get("format"),
        "type": media_type,
        "creator": "Broken Vzn"
    })

if __name__ == '__main__':
    app.run(port=5000, threaded=True)