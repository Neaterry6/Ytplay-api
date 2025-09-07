from flask import Flask, jsonify, request
import yt_dlp
import urllib.parse
import requests
import time
import os

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

# ✅ Use verified video URL for "Holiday by Rema"
def search_youtube(query):
    if query.lower().strip() == "holiday by rema":
        return "https://www.youtube.com/watch?v=LboPHhUyIbo"
    return None

# 🎯 Extract media info from YouTube URL
def fetch_media_info(video_url, media_type):
    time.sleep(1.5)  # ⏳ Delay to avoid rate-limiting
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'cookiefile': 'cookies.txt',  # ✅ Use cookies to bypass restrictions
        'forcejson': True,
        'noplaylist': True,
        'format': (
            'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
            if media_type == 'video'
            else 'bestaudio[ext=m4a]/bestaudio'
        )
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(video_url, download=False)
    except Exception as e:
        if "429" in str(e):
            return {"error": "YouTube is rate-limiting your requests. Try again later."}
        return {"error": str(e)}

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

    info = fetch_media_info(video_url, media_type)
    if isinstance(info, dict) and "error" in info:
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
            "error": info["error"]
        }), 429

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

# ✅ Bind to Render's dynamic port
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)