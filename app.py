import os
from flask import Flask, render_template_string, request, send_file
import yt_dlp

app = Flask(__name__)

# Простой HTML интерфейс с рабочей логикой скачивания через наш сервер
HTML_PAGE = """
<!DOCTYPE html>
<html lang="ru" class="h-full">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TubeGrabber</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-slate-950 text-slate-100 min-h-full flex flex-col justify-between font-['Inter']">
    <header class="border-b border-slate-800 p-4 text-center">
        <h1 class="text-2xl font-bold text-red-500">TubeGrabber <span class="text-xs bg-red-500/20 px-2 py-0.5 rounded text-red-400">Server Edition</span></h1>
    </header>
    <main class="flex-grow flex items-center justify-center p-4">
        <div class="max-w-md w-full bg-slate-900 border border-slate-800 p-6 rounded-2xl shadow-xl space-y-4">
            <form action="/download" method="POST" class="space-y-4">
              <div>
                <label class="block text-sm text-slate-400 mb-1">Ссылка на YouTube видео</label>
                <input type="text" name="url" required placeholder="https://youtu.be/..." class="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-red-500">
              </div>
              <div>
                <label class="block text-sm text-slate-400 mb-1">Формат</label>
                <select name="format" class="w-full p-3 bg-slate-950 border border-slate-800 rounded-xl text-white focus:outline-none focus:border-red-500">
                  <option value="mp4">Видео (MP4)</option>
                  <option value="mp3">Аудио (MP3)</option>
                </select>
              </div>
              <button type="submit" class="w-full bg-red-600 hover:bg-red-500 text-white font-medium p-3 rounded-xl transition shadow-lg shadow-red-600/30">
                <i class="fa-solid fa-download mr-2"></i> Скачать файл
              </button>
            </form>
        </div>
    </main>
    <footer class="border-t border-slate-800 p-4 text-center text-xs text-slate-500">
        © 2026 TubeGrabber by vizquacker
    </footer>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    fmt = request.form.get('format')

    output_dir = '/tmp'
    if fmt == 'mp3':
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        }
    else:
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if fmt == 'mp3':
                filename = os.path.splitext(filename)[0] + '.mp3'
            return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"Ошибка при скачивании: {str(e)}", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
