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

def extract_audio_info(video_url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'cookiefile': 'cookies.txt',
        'forcejson': True,
        'noplaylist': True,
        'format': 'bestaudio[ext=m4a]/bestaudio'
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

    # Hardcoded top video URLs for known queries
    fallback_map = {
        "holiday by rema": "https://www.youtube.com/watch?v=LboPHhUyIbo",
        "juice wrld burn": "https://www.youtube.com/watch?v=HA1srD2DwaI"
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
            "error": "No known video URL for this query"
        }), 404

    try:
        if media_type == "audio":
            info = extract_audio_info(video_url)
            short_url = shorten_url(info.get("url"))
            publish_date = info.get("upload_date")
            if publish_date:
                publish_date = f"{publish_date[:4]}-{publish_date[4:6]}-{publish_date[6:]}"
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
                "format": "mp3",
                "quality": info.get("format"),
                "type": "audio",
                "creator": "Broken Vzn"
            })
        else:
            # Video mode returns embed link + metadata only
            video_id = video_url.split("v=")[-1]
            embed_url = f"https://www.youtube.com/embed/{video_id}"
            return jsonify({
                "title": decoded_query.title(),
                "download_url": None,
                "video_url": embed_url,
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
                "duration": None,
                "channel_name": None,
                "publish_date": None,
                "views": None,
                "likes": None,
                "description": None,
                "format": "mp4",
                "quality": "YouTube Embed",
                "type": "video",
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