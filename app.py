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

stream_key_input = st.text_input(
    "YouTube Stream Key (Ya poora RTMP URL + Key)",
    type="password",
    placeholder="huvh-c00p-90v2-c5wp-cqz2 ya rtmp://...",
)

if "process" not in st.session_state:
  st.session_state.process = None

col1, col2 = st.columns(2)

with col1:
  if st.button("Start Streaming 🚀", type="primary"):
    if not uploaded_file or not stream_key_input:
      st.error("Pehle Video Upload karein aur Stream Key daalein!")
    else:
      # Stream Key Auto Formatting (Agar rtmp na ho to auto add kar do)
      clean_key = stream_key_input.strip()
      if not clean_key.startswith("rtmp"):
        full_stream_url = f"rtmp://a.rtmp.youtube.com/live2/{clean_key}"
      else:
        full_stream_url = clean_key

      # Video file save in server
      video_path = "temp_video.mp4"
      with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

      # Stop active process
      if st.session_state.process:
        st.session_state.process.kill()

      # FFmpeg command to stream live on YouTube
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
