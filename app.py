import json
import os
import subprocess
import time
from datetime import datetime
import streamlit as st

st.set_page_config(
    page_title="24/7 Direct Upload Streamer", page_icon="🎥", layout="centered"
)

INFO_FILE = "stream_info.json"
VIDEO_FILE = "temp_video.mp4"
LIVE_SNAP_FILE = "live_snapshot.jpg"


def is_ffmpeg_running():
  """Check if ffmpeg process is running in system."""
  try:
    output = subprocess.check_output(["pgrep", "-f", "ffmpeg"]).decode().strip()
    return bool(output)
  except Exception:
    return False


def stop_all_ffmpeg():
  """Kill all running ffmpeg processes and remove temp files."""
  try:
    subprocess.run(["pkill", "-9", "-f", "ffmpeg"])
    for f in [VIDEO_FILE, INFO_FILE, LIVE_SNAP_FILE]:
      if os.path.exists(f):
        os.remove(f)
    return True
  except Exception:
    return False


def get_video_duration(file_path):
  """Get video duration in seconds using ffprobe."""
  try:
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        file_path,
    ]
    duration = float(subprocess.check_output(cmd).decode().strip())
    return duration
  except Exception:
    return 0.0


def capture_live_snapshot(current_pos):
  """Capture current live frame using ffprobe/ffmpeg position."""
  try:
    cmd = f'ffmpeg -ss {current_pos} -i "{VIDEO_FILE}" -vframes 1 -q:v 2 "{LIVE_SNAP_FILE}" -y'
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return True
  except Exception:
    return False


def save_stream_info(filename, rtmp_url, duration):
  """Save metadata about current playing stream."""
  data = {
      "filename": filename,
      "rtmp_url": rtmp_url,
      "start_epoch": time.time(),
      "start_time_str": datetime.now().strftime("%I:%M %p (%d-%b-%Y)"),
      "duration": duration,
  }
  with open(INFO_FILE, "w") as f:
    json.dump(data, f)


def load_stream_info():
  """Load metadata with auto-fallback recovery."""
  if os.path.exists(INFO_FILE):
    try:
      with open(INFO_FILE, "r") as f:
        return json.load(f)
    except Exception:
      pass

  if os.path.exists(VIDEO_FILE):
    duration = get_video_duration(VIDEO_FILE)
    start_epoch = os.path.getmtime(VIDEO_FILE)
    return {
        "filename": "Uploaded_Video.mp4",
        "rtmp_url": "rtmp://a.rtmp.youtube.com/live2",
        "start_epoch": start_epoch,
        "start_time_str": datetime.fromtimestamp(start_epoch).strftime(
            "%I:%M %p (%d-%b-%Y)"
        ),
        "duration": duration,
    }
  return None


def format_seconds(seconds):
  """Format seconds into HH:MM:SS format."""
  m, s = divmod(int(seconds), 60)
  h, m = divmod(m, 60)
  if h > 0:
    return f"{h}h {m:02d}m {s:02d}s"
  return f"{m:02d}m {s:02d}s"


st.title("🎥 24/7 Live Streamer (Direct Upload)")
st.write("Apni video direct computer se upload karein aur Live Stream chalayein!")

# File Upload Option
uploaded_file = st.file_uploader(
    "Apni Video File Select Karein (.mp4, .mkv)", type=["mp4", "mkv", "mov"]
)

rtmp_url = st.text_input(
    "Stream URL (Server URL)",
    value="rtmp://a.rtmp.youtube.com/live2",
    placeholder="rtmp://a.rtmp.youtube.com/live2",
)

stream_key = st.text_input(
    "Stream Key",
    type="password",
    placeholder="xxxx-xxxx-xxxx-xxxx-xxxx",
)

col1, col2 = st.columns(2)

with col1:
  if st.button("Start Streaming 🚀", type="primary"):
    if not uploaded_file or not stream_key or not rtmp_url:
      st.error("Tamam fields fill karna aur Video upload karna zaroori hai!")
    else:
      stop_all_ffmpeg()

      base_url = rtmp_url.strip().rstrip("/")
      clean_key = stream_key.strip()
      full_stream_url = f"{base_url}/{clean_key}"

      with open(VIDEO_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())

      duration = get_video_duration(VIDEO_FILE)
      save_stream_info(uploaded_file.name, base_url, duration)

      cmd = f'ffmpeg -re -
