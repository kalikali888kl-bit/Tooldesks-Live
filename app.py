import os
import signal
import subprocess
import streamlit as st

st.set_page_config(
    page_title="24/7 Direct Upload Streamer", page_icon="🎥", layout="centered"
)

st.title("🎥 24/7 Live Streamer (Direct Upload)")
st.write("Apni video direct computer se upload karein aur Live Stream chalayein!")


def is_ffmpeg_running():
  """Check if ffmpeg process is running in system."""
  try:
    output = subprocess.check_output(["pgrep", "-f", "ffmpeg"]).decode().strip()
    return bool(output)
  except Exception:
    return False


def stop_all_ffmpeg():
  """Kill all running ffmpeg processes."""
  try:
    subprocess.run(["pkill", "-9", "-f", "ffmpeg"])
    if os.path.exists("temp_video.mp4"):
      os.remove("temp_video.mp4")
    return True
  except Exception:
    return False


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
      # Purani koi bhi stream chal rahi ho to kill kar do
      stop_all_ffmpeg()

      # URL aur Key combine karna
      base_url = rtmp_url.strip().rstrip("/")
      clean_key = stream_key.strip()
      full_stream_url = f"{base_url}/{clean_key}"

      # Video file save in server
      video_path = "temp_video.mp4"
      with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

      # Continuous Loop FFmpeg Command
      cmd = f'ffmpeg -re -stream_loop -1 -i "{video_path}" -c:v libx264 -preset ultrafast -b:v 2500k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 -f flv "{full_stream_url}"'

      subprocess.Popen(cmd, shell=True)
      st.success("🚀 Stream YouTube par bhej di gayi hai!")

with col2:
  if st.button("Stop Streaming 🛑"):
    if is_ffmpeg_running():
      stop_all_ffmpeg()
      st.warning("🛑 Live Stream mukammal roki gayi hai.")
    else:
      st.info("Koi active stream nahi chal rahi.")

# Current Status Indicator
st.divider()
if is_ffmpeg_running():
  st.success("🟢 Live Status: Stream Server Par Active Chal Rahi Hai")
else:
  st.secondary if hasattr(st, "secondary") else st.info(
      "⚪ Live Status: Koi Stream Active Nahi Hai"
  )
