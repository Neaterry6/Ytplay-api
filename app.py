from flask import Flask, jsonify
import urllib.parse
import os

app = Flask(__name__)

# 🔍 Simulated YouTube search result for "baby girl by joeboy"
def get_video_data(query):
    if query.lower().strip() == "baby girl by joeboy":
        return {
            "title": "Joeboy - Baby Girl (Official Audio)",
            "video_id": "wlOUX5IWT4Y",
            "duration": "2:38",
            "views": 46000,
            "published": "5 years ago",
            "download_url": "https://amy46.oceansaver.in/pacific/?0geBw0SIRLAo7JGf6FIGBH8"
        }
    return None

# 🎧 /play route — simplified audio metadata
@app.route('/play/<path:query>')
def play(query):
    decoded_query = urllib.parse.unquote(query)
    video_data = get_video_data(decoded_query)

    if not video_data:
        return jsonify({
            "creator": "Broken Vzn",
            "status": False,
            "error": "Audio not found"
        }), 404

    return jsonify({
        "creator": "Broken Vzn",
        "status": True,
        "result": {
            "title": video_data["title"],
            "download_url": video_data["download_url"]
        }
    })

# 🎬 /video route — full video metadata
@app.route('/video/<path:query>')
def video(query):
    decoded_query = urllib.parse.unquote(query)
    video_data = get_video_data(decoded_query)

    if not video_data:
        return jsonify({
            "creator": "Broken Vzn",
            "status": False,
            "error": "Video not found"
        }), 404

    video_url = f"https://youtube.com/watch?v={video_data['video_id']}"
    thumbnail = f"https://i.ytimg.com/vi/{video_data['video_id']}/hq720.jpg"

    return jsonify({
        "creator": "Broken Vzn",
        "status": True,
        "result": {
            "title": video_data["title"],
            "video_url": video_url,
            "thumbnail": thumbnail,
            "duration": video_data["duration"],
            "views": video_data["views"],
            "published": video_data["published"],
            "download_url": video_data["download_url"]
        }
    })

# 🏠 Root route
@app.route('/')
def home():
    return jsonify({
        "message": "Broken Vzn's Media API is running",
        "routes": ["/play/<query>", "/video/<query>"],
        "creator": "Broken Vzn"
    })

# 🚀 Render-compatible port binding
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, threaded=True)