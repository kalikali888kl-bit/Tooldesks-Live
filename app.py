import subprocess
import streamlit as st

st.set_page_config(page_title="24/7 Live Streamer", page_icon="🎥")
st.title("🎥 24/7 Live Stream Manager")

video_url = st.text_input(
    "Video Direct Link (.mp4)", placeholder="https://example.com/video.mp4"
)
stream_key = st.text_input(
    "YouTube/FB Stream Key",
    type="password",
    placeholder="rtmp://a.rtmp.youtube.com/live2/xxxx",
)

if "process" not in st.session_state:
  st.session_state.process = None

col1, col2 = st.columns(2)

with col1:
  if st.button("Start Streaming 🚀", type="primary"):
    if not video_url or not stream_key:
      st.error("Meharbani karke dono fields fill karein!")
    else:
      cmd = f'ffmpeg -re -stream_loop -1 -i "{video_url}" -c:v libx264 -preset ultrafast -b:v 2500k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 -f flv "{stream_key}"'
      if st.session_state.process:
        st.session_state.process.kill()
      st.session_state.process = subprocess.Popen(cmd, shell=True)
      st.success("🚀 Stream Shuru Ho Chuki Hai!")

with col2:
  if st.button("Stop Streaming 🛑"):
    if st.session_state.process:
      st.session_state.process.kill()
      st.session_state.process = None
      st.warning("🛑 Stream rok di gayi hai.")
    else:
      st.info("Koi active stream nahi chal rahi.")
