from flask import Flask, jsonify, request
import yt_dlp
import urllib.parse
import requests
import traceback
from bs4 import BeautifulSoup

app = Flask(__name__)

GENIUS_ACCESS_TOKEN = "2yHuhzVQAmuuHKKcJekeM3wXiBLQzt8GDqWVodgzq7slXnwZSZqLqXnhwVcjIwn9"

fallback_map = {
    "holiday by rema": "https://www.youtube.com/watch?v=LboPHhUyIbo",
    "juice wrld burn": "https://www.youtube.com/watch?v=HA1srD2DwaI"
}

def shorten_url(long_url):
    try:
        response = requests.get(f"https://is.gd/create.php?format=simple&url={long_url}", timeout=2)
        return response.text if response.status_code == 200 else long_url
    except Exception:
        return long_url

def search_and_extract(query, media_type):
    ydl_opts = {
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
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(query, download=False)
        if 'entries' in result and result['entries']:
            return result['entries'][0]
        return result

def get_genius_lyrics(query):
    try:
        search_url = f"https://api.genius.com/search?q={urllib.parse.quote(query)}"
        headers = {"Authorization": f"Bearer {GENIUS_ACCESS_TOKEN}"}
        response = requests.get(search_url, headers=headers, timeout=5).json()

        hits = response.get("response", {}).get("hits", [])
        if not hits:
            return None

        song_path = hits[0]["result"]["path"]
        lyrics_url = f"https://genius.com{song_path}"
        page = requests.get(lyrics_url, timeout=5)
        soup = BeautifulSoup(page.text, "html.parser")

        containers = soup.find_all("div", class_="Lyrics__Container")
        if not containers:
            return None

        lyrics = "\n".join([c.get_text(separator="\n").strip() for c in containers])
        return lyrics
    except Exception:
        return None

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to Broken Vzn's Media API",
        "usage": {
            "/play/<query>?format=audio|video": "Stream audio or video",
            "/lyrics/<query>": "Get lyrics from Genius"
        },
        "creator": "Broken Vzn"
    })

@app.route('/play/<path:query>')
def play(query):
    media_type = request.args.get('format', 'video').lower()
    decoded_query = urllib.parse.unquote(query).lower()

    try:
        video_url = fallback_map.get(decoded_query)
        info = search_and_extract(video_url if video_url else decoded_query, media_type)
        if not info or not info.get("url"):
            raise Exception("No video found or YouTube blocked access")

        short_url = shorten_url(info.get("url"))
        video_id = info.get("id")
        thumbnail = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg" if video_id else None
        publish_date = info.get("upload_date")
        if publish_date:
            publish_date = f"{publish_date[:4]}-{publish_date[4:6]}-{publish_date[6:]}"
        
        if media_type == "audio":
            return jsonify({
                "title": info.get("title"),
                "download_url": short_url,
                "video_url": info.get("webpage_url"),
                "thumbnail": thumbnail,
                "duration": info.get("duration"),
                "publish_date": publish_date,
                "description": info.get("description"),
                "format": "mp3",
                "quality": info.get("format"),
                "type": "audio",
                "creator": "Broken Vzn"
            })
        else:
            return jsonify({
                "title": info.get("title"),
                "download_url": short_url,
                "thumbnail": thumbnail,
                "format": "mp4",
                "quality": info.get("format"),
                "type": "video",
                "creator": "Broken Vzn"
            })

    except Exception as e:
        print("YT-DLP ERROR:", traceback.format_exc())
        return jsonify({
            "title": decoded_query.title(),
            "download_url": None,
            "thumbnail": None,
            "format": "mp3" if media_type == "audio" else "mp4",
            "quality": None,
            "type": media_type,
            "creator": "Broken Vzn",
            "error": str(e)
        }), 500

@app.route('/lyrics/<path:query>')
def lyrics(query):
    decoded_query = urllib.parse.unquote(query)
    lyrics = get_genius_lyrics(decoded_query)
    if lyrics:
        return jsonify({
            "title": decoded_query.title(),
            "lyrics": lyrics,
            "source": "Genius",
            "creator": "Broken Vzn"
        })
    else:
        return jsonify({
            "title": decoded_query.title(),
            "lyrics": None,
            "error": "Lyrics not found",
            "creator": "Broken Vzn"
        }), 404