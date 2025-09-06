from flask import Flask, jsonify, request
import yt_dlp
import urllib.parse
from functools import lru_cache

app = Flask(__name__)

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
                "thumbnail": None,
                "format": "mp3" if media_type == "audio" else "mp4",
                "quality": None,
                "type": media_type,
                "creator": "Broken Vzn",
                "error": "No video found"
            }), 404

        return jsonify({
            "title": info.get("title"),
            "download_url": info.get("url"),
            "thumbnail": info.get("thumbnail"),
            "format": "mp3" if media_type == "audio" else "mp4",
            "quality": info.get("format"),
            "type": media_type,
            "creator": "Broken Vzn"
        })

    except Exception as e:
        return jsonify({
            "title": decoded_query,
            "download_url": None,
            "thumbnail": None,
            "format": "mp3" if media_type == "audio" else "mp4",
            "quality": None,
            "type": media_type,
            "creator": "Broken Vzn",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5000, threaded=True)