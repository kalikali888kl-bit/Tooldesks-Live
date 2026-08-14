import subprocess
import streamlit as st

st.set_page_config(page_title="24/7 Live Streamer", page_icon="🎥")
st.title("🎥 24/7 Live Stream Manager")

video_url = st.text_input(
    "Video URL (YouTube link ya Direct MP4 link)",
    placeholder="https://youtu.be/xxx ya https://site.com/video.mp4",
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

      # Checking if YouTube URL or Direct MP4 URL
      if "youtube.com" in video_url or "youtu.be" in video_url:
        cmd = f'yt-dlp -g -f "best[ext=mp4]/best" "{video_url}" | xargs -I {{}} ffmpeg -re -stream_loop -1 -i "{{}}" -c:v libx264 -preset ultrafast -b:v 2500k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 -f flv "{stream_key}"'
      else:
        cmd = f'ffmpeg -re -stream_loop -1 -i "{video_url}" -c:v libx264 -preset ultrafast -b:v 2500k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 -f flv "{stream_key}"'

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
