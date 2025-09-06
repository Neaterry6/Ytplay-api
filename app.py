from flask import Flask, jsonify, request
import yt_dlp
import urllib.parse
import requests
from functools import lru_cache

app = Flask(__name__)

# 🔗 Shorten long download URLs using TinyURL
def shorten_url(long_url):
    try:
        response = requests.get(f"https://tinyurl.com/api-create.php?url={long_url}")
        return response.text if response.status_code == 200 else long_url
    except Exception:
        return long_url

# ⚡ Cache results to avoid repeated YouTube hits
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
        'format': (
            'bestaudio[ext=m4a]/bestaudio' if media_type == 'audio'
            else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
        )
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(query, download=False)
        if 'entries' in result and result['entries']:
            return result['entries'][0]
        return None

# 🏠 Root route for uptime bots
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Broken Vzn's YouTube API",
        "endpoints": ["/play/<query>?format=audio|video"],
        "creator": "Broken Vzn"
    })

# 🎧 /play endpoint for audio or video search
@app.route('/play/<path:query>')
def play(query):
    media_type = request.args.get('format', 'video').lower()
    decoded_query = urllib.parse.unquote(query)

    try:
        info = fetch_video_info(decoded_query, media_type)
        if not info or not info.get("url"):
            return jsonify({
                "title": decoded_query,
                "download_url": None,
                "short_url": None,
                "format": "mp3" if media_type == "audio" else "mp4",
                "quality": None,
                "type": media_type,
                "creator": "Broken Vzn",
                "error": "No video found"
            }), 404

        short_url = shorten_url(info.get("url"))

        return jsonify({
            "title": info.get("title"),
            "download_url": info.get("url"),
            "short_url": short_url,
            "format": "mp3" if media_type == "audio" else "mp4",
            "quality": info.get("format"),
            "type": media_type,
            "creator": "Broken Vzn"
        })

    except yt_dlp.utils.DownloadError as e:
        if "429" in str(e):
            return jsonify({
                "title": decoded_query,
                "download_url": None,
                "short_url": None,
                "format": "mp3" if media_type == "audio" else "mp4",
                "quality": None,
                "type": media_type,
                "creator": "Broken Vzn",
                "error": "YouTube is rate-limiting this server. Try again later."
            }), 429
        else:
            return jsonify({
                "title": decoded_query,
                "download_url": None,
                "short_url": None,
                "format": "mp3" if media_type == "audio" else "mp4",
                "quality": None,
                "type": media_type,
                "creator": "Broken Vzn",
                "error": str(e)
            }), 500

if __name__ == '__main__':
    app.run(port=5000)