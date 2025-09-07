from flask import Flask, jsonify, request
import yt_dlp
import urllib.parse
import requests

app = Flask(__name__)

# 🔗 Safe URL shortener (skip YouTube/Google to avoid block)
def safe_shorten_url(long_url):
    if any(domain in long_url for domain in ["youtube.com", "youtu.be", "google.com"]):
        return long_url
    try:
        response = requests.get(f"https://tinyurl.com/api-create.php?url={long_url}", timeout=2)
        return response.text if response.status_code == 200 else long_url
    except Exception:
        return long_url

# 🔍 Search YouTube and return top video URL
def search_youtube(query):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'default_search': 'ytsearch',
        'forcejson': True,
        'noplaylist': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(query, download=False)
            if 'entries' in result and result['entries']:
                return result['entries'][0].get('webpage_url')
        except Exception:
            return None

# 🎯 Extract media info from YouTube URL
def fetch_media_info(video_url, media_type):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'forcejson': True,
        'noplaylist': True,
        'format': (
            'bestaudio/best' if media_type == 'audio'
            else 'bestvideo+bestaudio/best'
        )
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            return ydl.extract_info(video_url, download=False)
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

    # 🔍 Search YouTube for the query
    video_url = search_youtube(decoded_query)
    if not video_url:
        return jsonify({
            "title": decoded_query,
            "real_download_url": None,
            "tinyurl_download_url": None,
            "video_url": None,
            "thumbnail": None,
            "duration": None,
            "format": "mp3" if media_type == "audio" else "mp4",
            "quality": None,
            "type": media_type,
            "creator": "Broken Vzn",
            "error": "No video found"
        }), 404

    # 🎯 Fetch media info
    info = fetch_media_info(video_url, media_type)
    if not info or not info.get("url"):
        return jsonify({
            "title": decoded_query,
            "real_download_url": None,
            "tinyurl_download_url": None,
            "video_url": video_url,
            "thumbnail": None,
            "duration": None,
            "format": "mp3" if media_type == "audio" else "mp4",
            "quality": None,
            "type": media_type,
            "creator": "Broken Vzn",
            "error": "Download link not found"
        }), 404

    real_download_url = info.get("url")
    tinyurl_download_url = safe_shorten_url(real_download_url)

    return jsonify({
        "title": info.get("title"),
        "real_download_url": real_download_url,
        "tinyurl_download_url": tinyurl_download_url,
        "video_url": video_url,
        "thumbnail": info.get("thumbnail"),
        "duration": info.get("duration"),
        "format": "mp3" if media_type == "audio" else "mp4",
        "quality": info.get("format"),
        "type": media_type,
        "creator": "Broken Vzn"
    })

if __name__ == '__main__':
    app.run(port=5000, threaded=True)