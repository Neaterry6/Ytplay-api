
from flask import Flask, jsonify, request
import yt_dlp
import urllib.parse
import requests
import traceback

app = Flask(__name__)

def shorten_url(long_url):
    try:
        response = requests.get(f"https://is.gd/create.php?format=simple&url={long_url}", timeout=2)
        return response.text if response.status_code == 200 else long_url
    except Exception:
        return long_url

def search_and_extract(query, media_type):
    search_opts = {
        'quiet': True,
        'skip_download': True,
        'cookiefile': 'cookies.txt',
        'cachedir': False,
        'default_search': 'ytsearch1',
        'forcejson': True,
        'noplaylist': True,
        'format': (
            'bestaudio[ext=m4a]/bestaudio' if media_type == 'audio'
            else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
        )
    }
    with yt_dlp.YoutubeDL(search_opts) as ydl:
        result = ydl.extract_info(query, download=False)
        if 'entries' in result and result['entries']:
            return result['entries'][0]
        return result

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

    try:
        info = search_and_extract(decoded_query, media_type)
        if not info or not info.get("url"):
            raise Exception("No video found or YouTube blocked access")

        short_url = shorten_url(info.get("url"))
        publish_date = info.get("upload_date")
        if publish_date:
            publish_date = f"{publish_date[:4]}-{publish_date[4:6]}-{publish_date[6:]}"
        video_id = info.get("id")
        embed_url = f"https://www.youtube.com/embed/{video_id}" if video_id else None

        return jsonify({
            "title": info.get("title"),
            "download_url": short_url if media_type == "audio" else None,
            "video_url": embed_url,
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "publish_date": publish_date,
            "description": info.get("description"),
            "format": "mp3" if media_type == "audio" else "mp4",
            "quality": info.get("format"),
            "type": media_type,
            "creator": "Broken Vzn"
        })

    except Exception as e:
        print("YT-DLP ERROR:", traceback.format_exc())
        return jsonify({
            "title": decoded_query,
            "download_url": None,
            "video_url": None,
            "thumbnail": None,
            "duration": None,
            "publish_date": None,
            "description": None,
            "format": "mp3" if media_type == "audio" else "mp4",
            "quality": None,
            "type": media_type,
            "creator": "Broken Vzn",
            "error": str(e)
        }), 500