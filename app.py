from flask import Flask, request, jsonify
import yt_dlp
import os

app = Flask(__name__)

# Shared yt-dlp options with cookie support
def get_ydl_opts(format_type):
    return {
        'quiet': True,
        'default_search': 'ytsearch1',
        'format': format_type,
        'skip_download': True,
        'cookiefile': 'cookies.txt'
    }

@app.route('/play')
def play():
    query = request.args.get('query')
    if not query:
        return jsonify({'status': False, 'error': 'Missing query'}), 400

    opts = get_ydl_opts('best')
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
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

@app.route('/play/audio')
def play_audio():
    query = request.args.get('query')
    if not query:
        return jsonify({'status': False, 'error': 'Missing query'}), 400

    opts = get_ydl_opts('bestaudio[ext=m4a]/bestaudio/best')
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            video = info['entries'][0] if 'entries' in info else info

            return jsonify({
                'status': True,
                'title': video.get('title'),
                'duration': video.get('duration_string') or str(video.get('duration')),
                'thumbnail': video.get('thumbnail') or f"https://i.ytimg.com/vi/{video.get('id')}/hqdefault.jpg",
                'download_url': video.get('url'),
                'creator': 'broken Vzn'
            })
    except Exception as e:
        return jsonify({'status': False, 'error': str(e)}), 500

@app.route('/play/video')
def play_video():
    query = request.args.get('query')
    if not query:
        return jsonify({'status': False, 'error': 'Missing query'}), 400

    opts = get_ydl_opts('best[ext=mp4]/best')
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            video = info['entries'][0] if 'entries' in info else info

            return jsonify({
                'status': True,
                'title': video.get('title'),
                'duration': video.get('duration_string') or str(video.get('duration')),
                'thumbnail': video.get('thumbnail') or f"https://i.ytimg.com/vi/{video.get('id')}/hqdefault.jpg",
                'download_url': video.get('url'),
                'creator': 'broken Vzn'
            })
    except Exception as e:
        return jsonify({'status': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print("Using cookies from:", os.path.abspath("cookies.txt"))
    app.run(host="0.0.0.0", port=port)