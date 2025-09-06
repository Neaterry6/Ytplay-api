from flask import Flask, jsonify, request
import yt_dlp
import urllib.parse

app = Flask(__name__)

@app.route('/play/<path:query>')
def play(query):
    media_type = request.args.get('format', 'video').lower()
    decoded_query = urllib.parse.unquote(query)

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'cookiefile': 'cookies.txt',
        'default_search': 'ytsearch1',
        'forcejson': True,
        'format': 'bestaudio' if media_type == 'audio' else 'best'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_result = ydl.extract_info(decoded_query, download=False)

            # ytsearch returns a playlist, so we grab the first video
            if 'entries' in search_result and search_result['entries']:
                info = search_result['entries'][0]
            else:
                return jsonify({
                    "title": decoded_query,
                    "download_url": None,
                    "format": "mp3" if media_type == "audio" else "mp4",
                    "quality": None,
                    "type": media_type,
                    "creator": "Broken Vzn",
                    "error": "No video found for query"
                }), 404

            return jsonify({
                "title": info.get("title"),
                "download_url": info.get("url"),
                "format": "mp3" if media_type == "audio" else "mp4",
                "quality": info.get("format"),
                "type": media_type,
                "creator": "Broken Vzn"
            })

    except Exception as e:
        return jsonify({
            "title": decoded_query,
            "download_url": None,
            "format": "mp3" if media_type == "audio" else "mp4",
            "quality": None,
            "type": media_type,
            "creator": "Broken Vzn",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(port=5000)