import json
import os
import signal
import subprocess
import time
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="24/7 Advanced Multi-Streamer", page_icon="🎥", layout="wide"
)

# Folder Paths
UPLOAD_DIR = "uploads"
STREAMS_DIR = "streams"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STREAMS_DIR, exist_ok=True)

# CSS for Animations & Styling
st.markdown(
    """
    <style>
    @keyframes pulse {
        0% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.03); opacity: 0.8; }
        100% { transform: scale(1); opacity: 1; }
    }
    .live-badge {
        background-color: #ff4b4b;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        animation: pulse 2s infinite;
    }
    .time-card {
        background: #1f2937;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #10b981;
        margin-bottom: 10px;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# --- HELPER FUNCTIONS ---
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


def get_pid_status(pid):
  """Check Linux process state (Running / Paused / Stopped)."""
  try:
    os.kill(pid, 0)
    try:
      with open(f"/proc/{pid}/status", "r") as f:
        for line in f:
          if line.startswith("State:"):
            state = line.split(":")[1].strip().split()[0]
            if state in ["T", "t"]:
              return "Paused ⏸"
            return "Running 🟢"
    except Exception:
      return "Running 🟢"
  except (OSError, ProcessLookupError):
    return "Stopped ⏹"


def get_active_streams():
  """List all saved stream metadata and update statuses."""
  streams = []
  for file in os.listdir(STREAMS_DIR):
    if file.endswith(".json"):
      path = os.path.join(STREAMS_DIR, file)
      try:
        with open(path, "r") as f:
          data = json.load(f)
          data["status"] = get_pid_status(data["pid"])
          streams.append(data)
      except Exception:
        pass
  return streams


# --- MAIN APP UI ---
st.title("🎥 24/7 Advanced Multi-Streamer Dashboard")

tabs = st.tabs([
    "🚀 Start New Stream",
    "📡 Active Streams Control",
    "📁 Uploaded Videos Library",
])

# ---------------------------------------------------------
# TAB 1: START NEW STREAM
# ---------------------------------------------------------
with tabs[0]:
  st.subheader("1️⃣ Videos Select Karein (Limit: Up to 10 Videos)")

  # Option 1: File Uploader
  new_uploads = st.file_uploader(
      "Nayi Videos Upload Karein",
      type=["mp4", "mkv", "mov"],
      accept_multiple_files=True,
  )

  if new_uploads:
    for uploaded_file in new_uploads:
      save_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
      if not os.path.exists(save_path):
        with open(save_path, "wb") as f:
          f.write(uploaded_file.getbuffer())
    st.success(f"{len(new_uploads)} video(s) Upload Library mein save ho gayi!")

  # Option 2: Select from Library
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
      st.subheader("2️⃣ Videos Loop Numbers Set Karein")

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
              key=f"loop_{idx}",
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

      # Live Timing & Calculation Panel
      st.subheader("⏱ Total Stream Calculation & Timing")

      now = datetime.now()
      estimated_end = now + timedelta(seconds=total_calculated_seconds)

      st.markdown(
          f"""
        <div class="time-card">
            <h4>⏳ Total Stream Duration: <b>{format_seconds(total_calculated_seconds)}</b></h4>
            <p style="margin: 5px 0;">🚀 <b>Start Time (Abhi):</b> {now.strftime('%I:%M:%S %p (%d-%b-%Y)')}</p>
            <p style="margin: 5px 0;">🏁 <b>Estimated End Time:</b> {estimated_end.strftime('%I:%M:%S %p (%d-%b-%Y)')}</p>
        </div>
        """,
          unsafe_allow_html=True,
      )

      # Server Settings
      st.subheader("3️⃣ Streaming Server Settings")
      rtmp_url = st.text_input(
          "Stream URL (Server URL)",
          value="rtmp://a.rtmp.youtube.com/live2",
      )
      stream_key = st.text_input(
          "Stream Key",
          type="password",
          placeholder="xxxx-xxxx-xxxx-xxxx-xxxx",
      )

      continuous_loop = st.checkbox(
          "🔄 Loop Entire Playlist Continuously (24/7 Mode)", value=True
      )

      if st.button("Start Live Stream 🚀", type="primary"):
        if not stream_key or not rtmp_url:
          st.error("Stream Key aur URL fill karna lazmi hai!")
        else:
          stream_id = f"stream_{int(time.time())}"
          concat_file_path = os.path.join(
              STREAMS_DIR, f"concat_{stream_id}.txt"
          )

          # Build Concat Text File
          with open(concat_file_path, "w") as f:
            for item in video_loop_config:
              abs_path = os.path.abspath(item["path"])
              for _ in range(item["loops"]):
                f.write(f"file '{abs_path}'\n")

          base_url = rtmp_url.strip().rstrip("/")
          clean_key = stream_key.strip()
          full_stream_url = f"{base_url}/{clean_key}"

          # Build FFmpeg Command
          loop_flag = "-stream_loop -1" if continuous_loop else ""
          cmd = f'ffmpeg {loop_flag} -f concat -safe 0 -i "{concat_file_path}" -c:v libx264 -preset ultrafast -b:v 2500k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 -f flv "{full_stream_url}"'

          process = subprocess.Popen(cmd, shell=True)

          # Save Metadata
          stream_info = {
              "id": stream_id,
              "pid": process.pid,
              "start_time": now.strftime("%I:%M %p (%d-%b-%Y)"),
              "start_epoch": time.time(),
              "end_time": estimated_end.strftime("%I:%M %p (%d-%b-%Y)"),
              "total_duration": total_calculated_seconds,
              "rtmp_url": base_url,
              "videos_count": len(video_loop_config),
              "concat_file": concat_file_path,
          }

          with open(
              os.path.join(STREAMS_DIR, f"{stream_id}.json"), "w"
          ) as info_f:
            json.dump(stream_info, info_f)

          st.success("🚀 Nayi Live Stream Successfully Start Ho Gayi!")
          st.rerun()

# ---------------------------------------------------------
# TAB 2: ACTIVE STREAMS CONTROL
# ---------------------------------------------------------
with tabs[1]:
  st.subheader("📡 Purani Aur Active Live Streams List")

  active_streams = get_active_streams()

  if not active_streams:
    st.info("Filhal koi stream active nahi hai.")
  else:
    for s in active_streams:
      with st.container():
        st.markdown(
            f"### 🔴 Stream ID: `{s['id']}` | Status: **{s['status']}**"
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("⏰ Start Time", s["start_time"])
        c2.metric("🏁 Expected End Time", s["end_time"])
        c3.metric(
            "⏳ Sequence Duration", format_seconds(s["total_duration"])
        )
        c4.metric("🎥 Videos Included", f"{s['videos_count']} Videos")

        # Control Buttons
        b_col1, b_col2, b_col3 = st.columns(3)

        pid = s["pid"]

        with b_col1:
          if st.button("Pause ⏸", key=f"pause_{s['id']}"):
            try:
              os.kill(pid, signal.SIGSTOP)
              st.warning("Stream Pause kar di gayi hai.")
              st.rerun()
            except Exception as e:
              st.error(f"Error: {e}")

        with b_col2:
          if st.button("Resume ▶", key=f"resume_{s['id']}"):
            try:
              os.kill(pid, signal.SIGCONT)
              st.success("Stream Resume ho gayi hai.")
              st.rerun()
            except Exception as e:
              st.error(f"Error: {e}")

        with b_col3:
          if st.button("Stop 🛑", key=f"stop_{s['id']}"):
            try:
              os.kill(pid, signal.SIGKILL)
              # Clean files
              json_p = os.path.join(STREAMS_DIR, f"{s['id']}.json")
              if os.path.exists(json_p):
                os.remove(json_p)
              if os.path.exists(s.get("concat_file", "")):
                os.remove(s["concat_file"])
              st.error("Stream Stop aur remove kar di gayi hai.")
              st.rerun()
            except Exception as e:
              st.error(f"Error: {e}")

        st.divider()

# ---------------------------------------------------------
# TAB 3: UPLOADED VIDEOS LIBRARY
# ---------------------------------------------------------
with tabs[2]:
  st.subheader("📁 Uploaded Videos History & Details")

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
