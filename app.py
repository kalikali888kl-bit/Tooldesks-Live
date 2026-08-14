import json
import os
import subprocess
from datetime import datetime
import streamlit as st

st.set_page_config(
    page_title="24/7 Direct Upload Streamer", page_icon="🎥", layout="centered"
)

INFO_FILE = "stream_info.json"
VIDEO_FILE = "temp_video.mp4"


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
    if os.path.exists(VIDEO_FILE):
      os.remove(VIDEO_FILE)
    if os.path.exists(INFO_FILE):
      os.remove(INFO_FILE)
    return True
  except Exception:
    return False


def save_stream_info(filename, rtmp_url):
  """Save metadata about current playing stream."""
  data = {
      "filename": filename,
      "rtmp_url": rtmp_url,
      "start_time": datetime.now().strftime("%I:%M %p (%d-%b-%Y)"),
  }
  with open(INFO_FILE, "w") as f:
    json.dump(data, f)


def load_stream_info():
  """Load metadata of current active stream."""
  if os.path.exists(INFO_FILE):
    try:
      with open(INFO_FILE, "r") as f:
        return json.load(f)
    except Exception:
      return None
  return None


st.title("🎥 24/7 Live Streamer (Direct Upload)")
st.write("Apni video direct computer se upload karein aur Live Stream chalayein!")

# File Upload Option
uploaded_file = st.file_uploader(
    "Apni Video File Select Karein (.mp4, .mkv)", type=["mp4", "mkv", "mov"]
)

# Alag Alag Inputs: Server URL aur Stream Key
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
      # Stop existing stream
      stop_all_ffmpeg()

      base_url = rtmp_url.strip().rstrip("/")
      clean_key = stream_key.strip()
      full_stream_url = f"{base_url}/{clean_key}"

      # Save video file
      with open(VIDEO_FILE, "wb") as f:
        f.write(uploaded_file.getbuffer())

      # Save metadata info
      save_stream_info(uploaded_file.name, base_url)

      # Continuous Loop FFmpeg Command
      cmd = f'ffmpeg -re -stream_loop -1 -i "{VIDEO_FILE}" -c:v libx264 -preset ultrafast -b:v 2500k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 -f flv "{full_stream_url}"'

      subprocess.Popen(cmd, shell=True)
      st.success("🚀 Stream YouTube par bhej di gayi hai!")
      st.rerun()

with col2:
  if st.button("Stop Streaming 🛑"):
    if is_ffmpeg_running():
      stop_all_ffmpeg()
      st.warning("🛑 Live Stream mukammal roki gayi hai.")
      st.rerun()
    else:
      st.info("Koi active stream nahi chal rahi.")

# --- ACTIVE STREAM MONITORING DASHBOARD ---
st.divider()

if is_ffmpeg_running():
  st.success("🟢 Live Status: Stream Active Hai!")

  info = load_stream_info()

  st.subheader("📺 Abhi Live Loop Par Yeh Video Chal Rahi Hai:")
  col_preview, col_details = st.columns([1, 1])

  with col_preview:
    if os.path.exists(VIDEO_FILE):
      st.video(VIDEO_FILE)

  with col_details:
    if info:
      st.markdown(f"**📄 File Name:** `{info.get('filename', 'N/A')}`")
      st.markdown(f"**⏰ Shuru Hone Ka Waqt:** `{info.get('start_time', 'N/A')}`")
      st.markdown(f"**📡 Target Server:** `{info.get('rtmp_url', 'N/A')}`")
    else:
      st.write("Video Server par active hai.")
else:
  st.info("⚪ Live Status: Filhal koi stream active nahi hai.")
