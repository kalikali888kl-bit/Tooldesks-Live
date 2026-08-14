import json
import os
import subprocess
import time
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="24/7 Live Streamer Pro", page_icon="🎥", layout="wide"
)

# Folder Paths
UPLOAD_DIR = "uploads"
INFO_FILE = "stream_info.json"
PLAYLIST_FILE = "playlist.txt"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Styling
st.markdown(
    """
    <style>
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.02); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    .time-card {
        background: #111827;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #10b981;
        margin-top: 10px;
        margin-bottom: 15px;
        color: white;
        animation: pulse 3s infinite;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- SYSTEM HELPER FUNCTIONS ---
def is_ffmpeg_running():
  """Check directly via Linux pgrep if FFmpeg is actively streaming."""
  try:
    output = subprocess.check_output(["pgrep", "-f", "ffmpeg"]).decode().strip()
    return bool(output)
  except Exception:
    return False


def get_ffmpeg_state():
  """Check if FFmpeg process is Running, Paused, or Stopped."""
  try:
    pid = subprocess.check_output(["pgrep", "-f", "ffmpeg"]).decode().split()[0]
    with open(f"/proc/{pid}/status", "r") as f:
      for line in f:
        if line.startswith("State:"):
          state = line.split(":")[1].strip().split()[0]
          if state in ["T", "t"]:
            return "Paused ⏸"
          return "Running 🟢"
  except Exception:
    pass
  return "Running 🟢" if is_ffmpeg_running() else "Stopped ⏹"


def stop_all_ffmpeg():
  """Kill all running ffmpeg processes."""
  try:
    subprocess.run(["pkill", "-9", "-f", "ffmpeg"])
    if os.path.exists(INFO_FILE):
      os.remove(INFO_FILE)
    if os.path.exists(PLAYLIST_FILE):
      os.remove(PLAYLIST_FILE)
    return True
  except Exception:
    return False


def pause_ffmpeg():
  try:
    subprocess.run(["pkill", "-STOP", "-f", "ffmpeg"])
    return True
  except Exception:
    return False


def resume_ffmpeg():
  try:
    subprocess.run(["pkill", "-CONT", "-f", "ffmpeg"])
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


def format_seconds(seconds):
  """Format seconds into HH:MM:SS format."""
  m, s = divmod(int(seconds), 60)
  h, m = divmod(m, 60)
  if h > 0:
    return f"{h}h {m:02d}m {s:02d}s"
  return f"{m:02d}m {s:02d}s"


def save_stream_info(data):
  with open(INFO_FILE, "w") as f:
    json.dump(data, f)


def load_stream_info():
  if os.path.exists(INFO_FILE):
    try:
      with open(INFO_FILE, "r") as f:
        return json.load(f)
    except Exception:
      pass
  return None


# --- MAIN HEADER ---
st.title("🎥 24/7 Live Streamer Pro Dashboard")

tabs = st.tabs([
    "🚀 Stream Controls & Setup",
    "📊 Real-Time Live Tracker",
    "📁 Uploaded Videos Library",
])

# ---------------------------------------------------------
# TAB 1: STREAM CONTROLS & SETUP
# ---------------------------------------------------------
with tabs[0]:
  st.subheader("1️⃣ Videos Upload & Multi-Select (Up to 10 Videos)")

  # File Uploader
  new_uploads = st.file_uploader(
      "Nayi Video Files Upload Karein",
      type=["mp4", "mkv", "mov"],
      accept_multiple_files=True,
  )

  if new_uploads:
    for uploaded_file in new_uploads:
      save_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
      if not os.path.exists(save_path):
        with open(save_path, "wb") as f:
          f.write(uploaded_file.getbuffer())
    st.success("Uploaded files library mein save ho gayi hain!")

  existing_files = [
      f for f in os.listdir(UPLOAD_DIR) if f.endswith((".mp4", ".mkv", ".mov"))
  ]

  if not existing_files:
    st.info("Pehle upar se kam az kam 1 video upload karein.")
  else:
    selected_videos = st.multiselect(
        "Library Se Videos Select Karein (Max 10)",
        options=existing_files,
        max_selections=10,
    )

    if selected_videos:
      st.subheader("2️⃣ Videos Loop Configurator")

      total_calculated_seconds = 0
      video_loop_config = []

      cols = st.columns(min(len(selected_videos), 3))

      for idx, vid_name in enumerate(selected_videos):
        vid_path = os.path.join(UPLOAD_DIR, vid_name)
        duration = get_video_duration(vid_path)

        with cols[idx % 3]:
          st.markdown(f"**🎬 Video {idx+1}:** `{vid_name}`")
          st.caption(f"Single Duration: {format_seconds(duration)}")

          loop_count = st.number_input(
              f"Loop Count (Video {idx+1})",
              min_value=1,
              max_value=100,
              value=1,
              key=f"loop_cfg_{idx}",
          )

          vid_total_time = duration * loop_count
          total_calculated_seconds += vid_total_time

          st.write(f"Total Time: **{format_seconds(vid_total_time)}**")
          st.divider()

          video_loop_config.append({
              "name": vid_name,
              "path": vid_path,
              "loops": loop_count,
              "duration": duration,
          })

      # Live Timing Info
      st.subheader("⏱ Timing Calculation")
      now = datetime.now()
      estimated_end = now + timedelta(seconds=total_calculated_seconds)

      st.markdown(
          f"""
        <div class="time-card">
            <h4>⏳ Sequence Total Duration: <b>{format_seconds(total_calculated_seconds)}</b></h4>
            <p style="margin: 3px 0;">🚀 <b>Start Time:</b> {now.strftime('%I:%M:%S %p (%d-%b-%Y)')}</p>
            <p style="margin: 3px 0;">🏁 <b>Calculated End Time:</b> {estimated_end.strftime('%I:%M:%S %p (%d-%b-%Y)')}</p>
        </div>
        """,
          unsafe_allow_html=True,
      )

      # Server Settings
      st.subheader("3️⃣ Target Server Details")
      rtmp_url = st.text_input(
          "Stream URL (Server URL)",
          value="rtmp://a.rtmp.youtube.com/live2",
      )
      stream_key = st.text_input(
          "Stream Key",
          type="password",
          placeholder="xxxx-xxxx-xxxx-xxxx-xxxx",
      )

      # Stream Controls Buttons
      c_start, c_pause, c_resume, c_stop = st.columns(4)

      with c_start:
        if st.button("Start Streaming 🚀", type="primary"):
          if not stream_key or not rtmp_url:
            st.error("Stream Key aur URL fill karna lazmi hai!")
          else:
            stop_all_ffmpeg()

            # Create Playlist Text File
            with open(PLAYLIST_FILE, "w") as f:
              for item in video_loop_config:
                abs_path = os.path.abspath(item["path"])
                for _ in range(item["loops"]):
                  f.write(f"file '{abs_path}'\n")

            base_url = rtmp_url.strip().rstrip("/")
            clean_key = stream_key.strip()
            full_stream_url = f"{base_url}/{clean_key}"

            cmd = f'ffmpeg -re -stream_loop -1 -f concat -safe 0 -i "{PLAYLIST_FILE}" -c:v libx264 -preset ultrafast -b:v 2500k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 -f flv "{full_stream_url}"'

            subprocess.Popen(cmd, shell=True)

            save_stream_info({
                "videos": [v["name"] for v in video_loop_config],
                "main_file": video_loop_config[0]["path"],
                "start_epoch": time.time(),
                "start_time_str": now.strftime("%I:%M %p (%d-%b-%Y)"),
                "end_time_str": estimated_end.strftime("%I:%M %p (%d-%b-%Y)"),
                "total_duration": total_calculated_seconds,
                "rtmp_url": base_url,
            })

            st.success("🚀 Stream YouTube par bhej di gayi hai!")
            st.rerun()

      with c_pause:
        if st.button("Pause Stream ⏸"):
          pause_ffmpeg()
          st.warning("Stream Pause kar di gayi hai.")
          st.rerun()

      with c_resume:
        if st.button("Resume Stream ▶"):
          resume_ffmpeg()
          st.success("Stream Resume ho gayi hai.")
          st.rerun()

      with c_stop:
        if st.button("Stop Stream 🛑"):
          stop_all_ffmpeg()
          st.error("Stream Stop kar di gayi hai.")
          st.rerun()

# ---------------------------------------------------------
# TAB 2: REAL-TIME LIVE TRACKER (RESTORED DASHBOARD)
# ---------------------------------------------------------
with tabs[1]:
  st.subheader("📊 Live Streaming Real-Time Status & Synced Player")

  if is_ffmpeg_running():
    state = get_ffmpeg_state()
    st.success(f"🟢 Live Status: Stream Active Hai! ({state})")

    info = load_stream_info()

    if info:
      start_epoch = info.get("start_epoch", time.time())
      duration = info.get("total_duration", 1.0)
      elapsed_total = time.time() - start_epoch

      loop_count = int(elapsed_total // duration) + 1 if duration > 0 else 1
      current_pos = elapsed_total % duration if duration > 0 else 0
      progress_ratio = (
          min(1.0, max(0.0, current_pos / duration)) if duration > 0 else 0.0
      )

      # 1. Live Synced Video Player
      main_video_file = info.get("main_file", "")
      if main_video_file and os.path.exists(main_video_file):
        st.write(
            f"**📺 Live Synced Player (Position:"
            f" {format_seconds(current_pos)}):**"
        )
        st.video(
            main_video_file,
            start_time=int(current_pos),
            autoplay=True,
            muted=True,
        )

      # 2. Real-Time Metrics
      m1, m2, m3, m4 = st.columns(4)
      m1.metric("🔁 Sequence Loop Count", f"{loop_count} baar")
      m2.metric(
          "⏱ Position / Duration",
          f"{format_seconds(current_pos)} / {format_seconds(duration)}",
      )
      m3.metric("⏳ Total Stream Time", format_seconds(elapsed_total))
      m4.metric("🏁 Target End Time", info.get("end_time_str", "N/A"))

      st.write(f"**Current Sequence Progress:** {int(progress_ratio * 100)}%")
      st.progress(progress_ratio)

      # Details
      st.markdown(
          f"**🎬 Selected Videos:** `{', '.join(info.get('videos', []))}`"
      )
      st.markdown(f"**⏰ Stream Started At:** `{info.get('start_time_str')}`")
      st.markdown(f"**📡 Target Server:** `{info.get('rtmp_url')}`")

      if st.button("🔄 Sync & Refresh Tracker"):
        st.rerun()
  else:
    st.info("⚪ Live Status: Filhal koi stream active nahi hai.")

# ---------------------------------------------------------
# TAB 3: UPLOADED VIDEOS LIBRARY
# ---------------------------------------------------------
with tabs[2]:
  st.subheader("📁 Uploaded Videos History & File Details")

  files = [
      f for f in os.listdir(UPLOAD_DIR) if f.endswith((".mp4", ".mkv", ".mov"))
  ]

  if not files:
    st.info("Koi video file upload nahi hui.")
  else:
    table_data = []
    for file in files:
      file_p = os.path.join(UPLOAD_DIR, file)
      size_mb = os.path.getsize(file_p) / (1024 * 1024)
      mod_time = datetime.fromtimestamp(os.path.getmtime(file_p)).strftime(
          "%I:%M %p (%d-%b-%Y)"
      )
      duration = get_video_duration(file_p)

      table_data.append({
          "File Name": file,
          "Size (MB)": f"{size_mb:.2f} MB",
          "Duration": format_seconds(duration),
          "Upload Date & Time": mod_time,
      })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)
