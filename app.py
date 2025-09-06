from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)

# 🔊 /play: Search YouTube for audio
@app.route('/play', methods=['POST'])
def play_audio():
    query = request.json.get('query')
    if not query:
        return jsonify({"error": "Missing query"}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'cookiefile': 'cookies.txt',
        'default_search': 'ytsearch1',
        'format': 'bestaudio',
        'forcejson': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            return jsonify({
                "title": info.get("title"),
                "download_url": info.get("url"),
                "format": "mp3",
                "quality": "bestaudio",
                "type": "audio",
                "creator": "Broken Vzn"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🎥 /video: Search YouTube for video
@app.route('/video', methods=['POST'])
def play_video():
    query = request.json.get('query')
    if not query:
        return jsonify({"error": "Missing query"}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'cookiefile': 'cookies.txt',
        'default_search': 'ytsearch1',
        'format': 'best',
        'forcejson': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            return jsonify({
                "title": info.get("title"),
                "download_url": info.get("url"),
                "format": "mp4",
                "quality": "best",
                "type": "video",
                "creator": "Broken Vzn"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 🚀 Run the app
if __name__ == '__main__':
    app.run(port=5000)
