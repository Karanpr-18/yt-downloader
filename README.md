# 🎬 Universal Downloader

An elegant, **Streamlit-powered YouTube Video Downloader** that delivers a premium UI experience along with high‑quality video & audio downloading using `yt-dlp`. Built with attention to UX — smooth animations, glassmorphism design, smart FFmpeg handling, and real‑time progress feedback.

---

## ✨ Features

* 🚀 **Fast & Reliable** — powered by `yt-dlp`
* 🎨 **Modern Aurora UI** — custom CSS with glassmorphism and animations
* 🔍 **Real‑time Metadata Fetching** — title, thumbnail, uploader, duration & views
* 📥 **High Quality Downloading** — best available video + audio merged to MP4
* 📊 **Live Progress Tracking** — speed, ETA, percentage & merge status
* 🧠 **Smart FFmpeg Detection** — automatically locates or adapts
* 🎈 **Beautiful Finishers** — balloons & success visual effects
* 🖥️ **Cross‑platform** — Works on Windows / Linux / Mac

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit** for UI
* **yt‑dlp** for extraction
* **FFmpeg** for merging streams

---

## 🔧 Installation

Clone the repository:

```bash
git clone https://github.com/Karanpr-18/yt-downloader
cd your-repo
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Or manually install core packages:

```bash
pip install streamlit yt-dlp imageio-ffmpeg static-ffmpeg
```

---

## ▶️ Usage

1) Run the Streamlit app:

```bash
streamlit run yt_downloader.py
```

**2) Simply double‑click:**

* `yt-downloader.bat` (Windows) → launches the app instantly with one double‑click

Then:
1️⃣ Paste a YouTube URL
2️⃣ Click **Search**
3️⃣ Preview details
4️⃣ Hit **Download High Quality MP4**

Sit back & let the magic happen ✨

---
<img width="1001" height="440" alt="image" src="https://github.com/user-attachments/assets/23003d24-de11-4b4e-8dc2-9b8580ac63c1" />


## ⚙️ FFmpeg Handling

The project auto‑detects FFmpeg using:

1️⃣ `imageio_ffmpeg`
2️⃣ `static_ffmpeg`
3️⃣ Local `/bin` or root directory paths
4️⃣ System PATH fallback

If FFmpeg is not found, the app still works but merging capabilities may be limited.

---

## 🧩 Additional Files

* `yt_downloader.py` — main Streamlit app logic
* `yt-downloader.bat` — Windows launcher helper

---

## ❗ Disclaimer

This tool is for **educational purposes only**. Please ensure you respect content ownership laws and only download media you have rights to.

---


## 📜 License

MIT License — free to modify & use.

