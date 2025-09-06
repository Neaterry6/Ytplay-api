from flask import Flask, jsonify, request
import yt_dlp
import urllib.parse
import requests

app = Flask(__name__)

def shorten_url(long_url):
    try:
        response = requests.get(f"https://is.gd/create.php?format=simple&url={long_url}", timeout=2)
        return response.text if response.status_code == 200 else long_url
    except Exception:
        return long_url

def extract_info(video_url, media_type):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'noplaylist': True,
        'format': (
            'bestaudio[ext=m4a]/bestaudio' if media_type == 'audio'
            else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]'
        )
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(video_url, download=False)

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

    # Step 1: Search YouTube manually (you can automate this with YouTube Data API or scraping)
    fallback_map = {
        "juice wrld burn": "https://www.youtube.com/watch?v=HA1srD2DwaI",
        "holiday by rema": "https://www.youtube.com/watch?v=LboPHhUyIbo"
    }

    video_url = fallback_map.get(decoded_query.lower())
    if not video_url:
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
            "error": "No fallback video URL found for this query"
        }), 404

    try:
        info = extract_info(video_url, media_type)
    except Exception as e:
        return jsonify({
            "title": decoded_query,
            "download_url": None,
            "video_url": video_url,
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
            "error": str(e)
        }), 500

    short_url = shorten_url(info.get("url"))
    publish_date = info.get("upload_date")
    if publish_date:
        publish_date = f"{publish_date[:4]}-{publish_date[4:6]}-{publish_date[6:]}"  # Format YYYY-MM-DD

    return jsonify({
        "title": info.get("title"),
        "download_url": short_url,
        "video_url": video_url,
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "channel_name": info.get("channel"),
        "publish_date": publish_date,
        "views": info.get("view_count"),
        "likes": info.get("like_count"),
        "description": info.get("description"),
        "format": "mp3" if media_type == "audio" else "mp4",
        "quality": info.get("format"),
        "type": media_type,
        "creator": "Broken Vzn"
    })