from flask import Flask, jsonify, request
import yt_dlp
import os

app = Flask(__name__)

# 🔧 Generate a short download URL (placeholder logic)
def shorten_download_url(video_id):
    # Replace with your own redirector or dynamic logic if needed
    return "https://amy46.oceansaver.in/pacific/?0geBw0SIRLAo7JGf6FIGBH8"

# 🔍 Search YouTube and extract metadata using yt_dlp
def get_video_data(query):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'default_search': 'ytsearch1',
        'forcejson': True,
        'format': 'best[ext=mp4]/best',
        'cookiefile': 'cookies.txt'  # Optional but recommended
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            video = info['entries'][0] if 'entries' in info else info

            video_id = video.get("id")
            duration_sec = video.get("duration", 0)
            duration = f"{duration_sec // 60}:{duration_sec % 60:02}"
            views = video.get("view_count", 0)
            published = video.get("upload_date", "")
            published_fmt = f"{published[:4]}-{published[4:6]}-{published[6:]}" if len(published) == 8 else "Unknown"

            return {
                "title": video.get("title"),
                "video_id": video_id,
                "duration": duration,
                "views": views,
                "published": published_fmt
            }
    except Exception as e:
        print(f"[yt_dlp error] {e}")
        return None

# 🎬 /video?query=... — full video metadata
@app.route('/video')
def video():
    query = request.args.get('query')
    if not query:
        return jsonify({
            "creator": "broken Vzn",
            "status": False,
            "error": "Missing query parameter"
        }), 400

    video_data = get_video_data(query)
    if not video_data:
        return jsonify({
            "creator": "broken Vzn",
            "status": False,
            "error": "Video not found"
        }), 404

    video_url = f"https://youtube.com/watch?v={video_data['video_id']}"
    thumbnail = f"https://i.ytimg.com/vi/{video_data['video_id']}/hq720.jpg"
    short_download_url = shorten_download_url(video_data["video_id"])

    return jsonify({
        "creator": "broken Vzn",
        "status": True,
        "result": {
            "title": video_data["title"],
            "video_url": video_url,
            "thumbnail": thumbnail,
            "duration": video_data["duration"],
            "views": video_data["views"],
            "published": "6 years ago",  # You can replace with video_data["published"] if you want exact date
            "download_url": short_download_url
        }
    })

# 🏠 Root route
@app.route('/')
def home():
    return jsonify({
        "message": "Broken Vzn YouTube Metadata API is running",
        "routes": ["/video?query=..."],
        "creator": "broken Vzn"
    })

# 🚀 Render-compatible port binding
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)