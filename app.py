import json
import os
import subprocess
import time
from datetime import datetime
import streamlit as st
import streamlit.components.v1 as components

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
    for f in [VIDEO_FILE, INFO_FILE]:
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


def extract_youtube_embed(url):
  """Extract YouTube video ID or stream embed link."""
  if not url:
    return None
  url = url.strip()
  if "v=" in url:
    video_id = url.split("v=")[1].split("&")[0]
    return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1"
  elif "youtu.be/" in url:
    video_id = url.split("youtu.be/")[1].split("?")[0]
    return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1"
  elif "live/" in url:
    video_id = url.split("live/")[1].split("?")[0]
    return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1"
  return None


def save_stream_info(filename, rtmp_url, yt_link, duration):
  """Save metadata about current playing stream."""
  data = {
      "filename": filename,
      "rtmp_url": rtmp_url,
      "yt_link": yt_link,
      "start_epoch": time.time(),
      "start_time_str": datetime.now().strftime("%I:%M %p (%d-%b-%Y)"),
      "duration": duration,
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
      pass
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

# Inputs
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

yt_live_link = st.text_input(
    "YouTube Live Video Link (Live Stream Player Ke Liye - Optional)",
    placeholder="https://www.youtube.com/watch?v=abcdef12345",
    help="Apni live stream ka public link yahan dalein taakay app par real-time live player chal sake.",
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
      save_stream_info(
          uploaded_file.name, base_url, yt_live_link.strip(), duration
      )

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

# --- REAL-TIME LIVE PLAYER DASHBOARD ---
st.divider()

if is_ffmpeg_running():
  st.success("🟢 Live Status: Stream Active Hai!")

  info = load_stream_info()

  st.subheader("🔴 Real-Time Live Broadcast Feed")

  yt_link = info.get("yt_link", "") if info else ""
  embed_url = extract_youtube_embed(yt_link)

  if embed_url:
    # YouTube Real-time Live Player Embed
    components.iframe(embed_url, height=400, scrolling=False)
  else:
    st.info(
        "💡 Tip: Agli baar 'YouTube Live Video Link' box mein apna live link"
        " dalein, yahan live YouTube player auto-play hoga!"
    )
    if os.path.exists(VIDEO_FILE):
      st.video(VIDEO_FILE)

  if info:
    start_epoch = info.get("start_epoch", time.time())
    duration = info.get("duration", 0.0)
    elapsed_total = time.time() - start_epoch

    if duration > 0:
      loop_count = int(elapsed_total // duration) + 1
      current_loop_pos = elapsed_total % duration
      progress_ratio = min(1.0, max(0.0, current_loop_pos / duration))

      m1, m2, m3 = st.columns(3)
      m1.metric("🔁 Repeat Count", f"{loop_count} baar")
      m2.metric(
          "⏱ Video Position",
          f"{format_seconds(current_loop_pos)} / {format_seconds(duration)}",
      )
      m3.metric("⏳ Total Stream Time", format_seconds(elapsed_total))

      st.write(f"**Current Video Progress:** {int(progress_ratio * 100)}%")
      st.progress(progress_ratio)

    st.markdown(f"**📄 File Name:** `{info.get('filename', 'N/A')}`")
    st.markdown(f"**⏰ Start Time:** `{info.get('start_time_str', 'N/A')}`")

    if st.button("🔄 Dashboard Refresh Karein"):
      st.rerun()
else:
  st.info("⚪ Live Status: Filhal koi stream active nahi hai.")
