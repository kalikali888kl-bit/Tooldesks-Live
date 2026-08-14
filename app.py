import os
import subprocess
import streamlit as st

st.set_page_config(
    page_title="24/7 Direct Upload Streamer", page_icon="🎥", layout="centered"
)

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

if "process" not in st.session_state:
  st.session_state.process = None

col1, col2 = st.columns(2)

with col1:
  if st.button("Start Streaming 🚀", type="primary"):
    if not uploaded_file or not stream_key or not rtmp_url:
      st.error("Tamam fields fill karna aur Video upload karna zaroori hai!")
    else:
      # URL aur Key ko safai se combine karna
      base_url = rtmp_url.strip().rstrip("/")
      clean_key = stream_key.strip()
      full_stream_url = f"{base_url}/{clean_key}"

      # Video file save in server
      video_path = "temp_video.mp4"
      with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

      # Purani stream roknay ke liye
      if st.session_state.process:
        st.session_state.process.kill()

      # FFmpeg command
      cmd = f'ffmpeg -re -stream_loop -1 -i "{video_path}" -c:v libx264 -preset ultrafast -b:v 2500k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 -f flv "{full_stream_url}"'

      st.session_state.process = subprocess.Popen(cmd, shell=True)
      st.success("🚀 Stream YouTube par bhej di gayi hai!")

with col2:
  if st.button("Stop Streaming 🛑"):
    if st.session_state.process:
      st.session_state.process.kill()
      st.session_state.process = None
      if os.path.exists("temp_video.mp4"):
        os.remove("temp_video.mp4")
      st.warning("🛑 Stream rok di gayi hai.")
    else:
      st.info("Koi active stream nahi chal rahi.")
