import subprocess
import streamlit as st

st.set_page_config(page_title="24/7 Live Streamer", page_icon="🎥")
st.title("🎥 24/7 Live Stream Manager")

video_url = st.text_input(
    "Video Direct MP4 Link",
    placeholder="https://example.com/video.mp4",
)
stream_key = st.text_input(
    "YouTube/FB Stream Key (RTMP URL + Key)",
    type="password",
    placeholder="rtmp://a.rtmp.youtube.com/live2/xxxx-xxxx-xxxx-xxxx",
)

if "process" not in st.session_state:
  st.session_state.process = None

col1, col2 = st.columns(2)

with col1:
  if st.button("Start Streaming 🚀", type="primary"):
    if not video_url or not stream_key:
      st.error("Dono fields fill karna zaroori hain!")
    else:
      if st.session_state.process:
        st.session_state.process.kill()

      # User-Agent add kiya hai taakay 403 Forbidden error na aaye
      ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
      cmd = f'ffmpeg -user_agent "{ua}" -re -stream_loop -1 -i "{video_url}" -c:v libx264 -preset ultrafast -b:v 2500k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 -f flv "{stream_key}"'

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
