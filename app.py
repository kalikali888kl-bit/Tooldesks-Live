from datetime import datetime, timedelta
import glob
import json
import os
import subprocess
import time
import streamlit as st

st.set_page_config(
    page_title="24/7 Multi-Video Live Streamer", page_icon="🎥", layout="centered"
)

INFO_FILE = "stream_info.json"
CONCAT_FILE = "concat_list.txt"


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

    # Clean up temp files
    if os.path.exists(INFO_FILE):
      os.remove(INFO_FILE)
    if os.path.exists(CONCAT_FILE):
      os.remove(CONCAT_FILE)

    for temp_f in glob.glob("temp_vid_*.mp4"):
      try:
        os.remove(temp_f)
      except Exception:
        pass
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


def save_stream_info(total_duration, rtmp_url, playlist_summary):
  """Save stream metadata including start, end time, and video details."""
  start_dt = datetime.now()
  end_dt = start_dt + timedelta(seconds=total_duration)

  data = {
      "start_epoch": time.time(),
      "total_duration": total_duration,
      "end_epoch": time.time() + total_duration,
      "start_time_str": start_dt.strftime("%I:%M:%S %p (%d-%b-%Y)"),
      "end_time_str": end_dt.strftime("%I:%M:%S %p (%d-%b-%Y)"),
      "rtmp_url": rtmp_url,
      "playlist_summary": playlist_summary,
  }
  with open(INFO_FILE, "w") as f:
    json.dump(data, f)


def load_stream_info():
  """Load active stream info."""
  if os.path.exists(INFO_FILE):
    try:
      with open(INFO_FILE, "r") as f:
        return json.load(f)
    except Exception:
      pass
  return None


# --- Custom CSS for Animation ---
st.markdown(
    """
<style>
@keyframes pulse {
    0% { transform: scale(0.98); opacity: 0.9; }
    50% { transform: scale(1.02); opacity: 1; }
    100% { transform: scale(0.98); opacity: 0.9; }
}
.animated-box-start {
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    color: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(30, 60, 114, 0.4);
    animation: pulse 3s infinite ease-in-out;
}
.animated-box-end {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    color: white;
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 4px 15px rgba(56, 239, 125, 0.4);
    animation: pulse 3s infinite ease-in-out;
}
.time-title { font-size: 14px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; }
.time-val { font-size: 18px; font-weight: bold; margin-top: 5px; }
</style>
""",
    unsafe_allow_html=True,
)

st.title("🎥 Multi-Video Live Stream Manager")
st.write(
    "1 se 10 videos upload karein, har video ke custom loops set karein aur Live"
    " Stream chalayein!"
)

# Multi-file Uploader (Max 10)
uploaded_files = st.file_uploader(
    "Apni Video Files Select Karein (Max 10 Videos)",
    type=["mp4", "mkv", "mov"],
    accept_multiple_files=True,
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

playlist_data = []
total_playlist_seconds = 0.0

if uploaded_files:
  if len(uploaded_files) > 10:
    st.error("⚠️ Aap zyaada se zyaada 10 videos select kar sakte hain!")
  else:
    st.subheader("⚙️ Video Loops & Playlist Configuration")

    for idx, file in enumerate(uploaded_files):
      temp_path = f"temp_vid_{idx}.mp4"

      # Save file temporarily if not existing to calculate exact duration
      if not os.path.exists(temp_path):
        with open(temp_path, "wb") as f:
          f.write(file.getbuffer())

      dur = get_video_duration(temp_path)

      col_file, col_loop, col_dur = st.columns([3, 2, 2])

      with col_file:
        st.markdown(f"**Video {idx+1}:** `{file.name}`")
        st.caption(f"Single Duration: {format_seconds(dur)}")

      with col_loop:
        loops = st.number_input(
            f"Loop Count",
            min_value=1,
            max_value=50,
            value=1,
            key=f"loop_cnt_{idx}",
        )

      with col_dur:
        subtotal = dur * loops
        st.markdown(f"**Total:** `{format_seconds(subtotal)}`")

      total_playlist_seconds += subtotal
      playlist_data.append({
          "path": temp_path,
          "name": file.name,
          "duration": dur,
          "loops": loops,
          "subtotal": subtotal,
      })
      st.divider()

    st.info(
        f"⏱️ **Total Complete Stream Duration:**"
        f" `{format_seconds(total_playlist_seconds)}`"
    )

# Action Buttons
c_start, c_stop = st.columns(2)

with c_start:
  if st.button("Start Live Streaming 🚀", type="primary"):
    if not uploaded_files or not stream_key or not rtmp_url:
      st.error(
          "Tamam fields fill karein aur kam se kam 1 video upload karein!"
      )
    elif len(uploaded_files) > 10:
      st.error("Maximum 10 videos ki limit hai!")
    else:
      stop_all_ffmpeg()

      # Write concat list for FFmpeg
      with open(CONCAT_FILE, "w") as concat_f:
        playlist_summary = []
        for item in playlist_data:
          abs_path = os.path.abspath(item["path"])
          for _ in range(item["loops"]):
            concat_f.write(f"file '{abs_path}'\n")

          playlist_summary.append(
              f"{item['name']} ({item['loops']}x Loop = "
              f"{format_seconds(item['subtotal'])})"
          )

      base_url = rtmp_url.strip().rstrip("/")
      clean_key = stream_key.strip()
      full_stream_url = f"{base_url}/{clean_key}"

      save_stream_info(total_playlist_seconds, base_url, playlist_summary)

      # FFmpeg command using concat
      cmd = f'ffmpeg -re -f concat -safe 0 -i "{CONCAT_FILE}" -c:v libx264 -preset ultrafast -b:v 2500k -maxrate 2500k -bufsize 5000k -pix_fmt yuv420p -g 50 -c:a aac -b:a 128k -ar 44100 -f flv "{full_stream_url}"'

      subprocess.Popen(cmd, shell=True)
      st.success("🚀 Playlist Live Streaming Shuru Ho Gayi Hai!")
      st.rerun()

with c_stop:
  if st.button("Stop Streaming 🛑"):
    if is_ffmpeg_running():
      stop_all_ffmpeg()
      st.warning("🛑 Live Stream mukammal roki gayi hai.")
      st.rerun()
    else:
      st.info("Koi active stream nahi chal rahi.")

# --- LIVE DASHBOARD & ANIMATED TIMERS ---
st.divider()

if is_ffmpeg_running():
  st.success("🟢 Live Status: Stream Active Hai!")

  info = load_stream_info()

  if info:
    st.subheader("📊 Stream Live Analytics & Animated Timers")

    start_epoch = info.get("start_epoch", time.time())
    total_duration = info.get("total_duration", 1.0)
    end_epoch = info.get("end_epoch", start_epoch + total_duration)

    elapsed = max(0.0, time.time() - start_epoch)
    remaining = max(0.0, end_epoch - time.time())
    progress_ratio = min(1.0, max(0.0, elapsed / total_duration))

    # Animated Start & End Time Display
    col_anim1, col_anim2 = st.columns(2)

    with col_anim1:
      st.markdown(
          f"""
            <div class="animated-box-start">
                <div class="time-title">🚀 Stream Start Time</div>
                <div class="time-val">{info.get('start_time_str', 'N/A')}</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    with col_anim2:
      st.markdown(
          f"""
            <div class="animated-box-end">
                <div class="time-title">🏁 Estimated End Time</div>
                <div class="time-val">{info.get('end_time_str', 'N/A')}</div>
            </div>
            """,
          unsafe_allow_html=True,
      )

    st.write("")

    # Real-time Duration Metrics
    m1, m2, m3 = st.columns(3)
    m1.metric("⏳ Elapsed Time", format_seconds(elapsed))
    m2.metric("⏱ Remaining Time", format_seconds(remaining))
    m3.metric("🎯 Total Duration", format_seconds(total_duration))

    st.write(f"**Overall Playlist Progress:** {int(progress_ratio * 100)}%")
    st.progress(progress_ratio)

    # Playlist Breakdown Summary
    st.markdown("### 📋 Active Playlist Sequence")
    for summary_line in info.get("playlist_summary", []):
      st.markdown(f"- `{summary_line}`")

    if st.button("🔄 Refresh Real-Time Timers"):
      st.rerun()
else:
  st.info("⚪ Live Status: Filhal koi stream active nahi hai.")
