import os
import subprocess
from flask import Flask, render_template_string, request

app = Flask(__name__)
stream_process = None

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Live Stream Server</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 40px auto; padding: 20px; background: #0f172a; color: white; }
        input, button { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: none; box-sizing: border-box; }
        button { background: #0d9488; color: white; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <h2>24/7 Live Stream Manager</h2>
    <form action="/start" method="POST">
        <label>Video Direct URL (.mp4):</label>
        <input type="text" name="video_url" placeholder="https://example.com/video.mp4" required>
        <label>YouTube/FB Stream Key:</label>
        <input type="password" name="stream_key" placeholder="rtmp://a.rtmp.youtube.com/live2/xxxx" required>
        <button type="submit">Start Streaming 🚀</button>
    </form>
</body>
</html>
"""


@app.route("/")
def home():
  return render_template_string(HTML)


@app.route("/start", methods=["POST"])
def start_stream():
  global stream_process
  video_url = request.form.get("video_url")
  stream_key = request.form.get("stream_key")

  cmd = f'ffmpeg -re -stream_loop -1 -i "{video_url}" -c:v libx264 -preset ultrafast -b:v 2500k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 -f flv "{stream_key}"'

  if stream_process:
    stream_process.kill()

  stream_process = subprocess.Popen(cmd, shell=True)
  return "Stream Started Successfully! You can close this browser."


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
