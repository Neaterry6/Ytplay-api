from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

@app.route('/play')
def play():
    query = request.args.get('query')
    if not query:
        return jsonify({'status': False, 'error': 'Missing query'}), 400

    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'default_search': 'ytsearch1'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            video = info['entries'][0] if 'entries' in info else info

            return jsonify({
                'status': True,
                'title': video.get('title'),
                'id': video.get('id'),
                'url': f"https://www.youtube.com/watch?v={video.get('id')}",
                'thumbnail': video.get('thumbnail') or f"https://i.ytimg.com/vi/{video.get('id')}/hqdefault.jpg",
                'duration': video.get('duration_string') or str(video.get('duration')),
                'creator': 'broken Vzn',
                'upload_date': video.get('upload_date'),
                'views': video.get('view_count')
            })
    except Exception as e:
        return jsonify({'status': False, 'error': str(e)}), 500

@app.route('/audio')
def audio():
    query = request.args.get('query')
    if not query:
        return jsonify({'status': False, 'error': 'Missing query'}), 400

    ydl_opts = {
        'quiet': True,
        'default_search': 'ytsearch1',
        'format': 'bestaudio[ext=m4a]/bestaudio/best',
        'skip_download': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            return jsonify({
                'status': True,
                'title': info.get('title'),
                'duration': info.get('duration_string') or str(info.get('duration')),
                'thumbnail': info.get('thumbnail') or f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg",
                'download_url': info.get('url'),
                'creator': 'broken Vzn'
            })
    except Exception as e:
        return jsonify({'status': False, 'error': str(e)}), 500

@app.route('/video')
def video():
    query = request.args.get('query')
    if not query:
        return jsonify({'status': False, 'error': 'Missing query'}), 400

    ydl_opts = {
        'quiet': True,
        'default_search': 'ytsearch1',
        'format': 'best[ext=mp4]/best',
        'skip_download': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            return jsonify({
                'status': True,
                'title': info.get('title'),
                'duration': info.get('duration_string') or str(info.get('duration')),
                'thumbnail': info.get('thumbnail') or f"https://i.ytimg.com/vi/{info.get('id')}/hqdefault.jpg",
                'download_url': info.get('url'),
                'creator': 'broken Vzn'
            })
    except Exception as e:
        return jsonify({'status': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)