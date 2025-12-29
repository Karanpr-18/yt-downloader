import streamlit as st
import yt_dlp
import os
import tempfile
import time
import shutil
import re

# 1. Page Configuration
st.set_page_config(
    page_title="Universal Downloader",
    page_icon="🎬",
    layout="centered"
)

# 2. Session State Management
if 'video_info' not in st.session_state:
    st.session_state.video_info = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""

# 3. Smart FFmpeg Detection
def get_ffmpeg_path():
    # Try getting ffmpeg from imageio_ffmpeg
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        path = get_ffmpeg_exe()
        if path and os.path.exists(path): return path
    except ImportError: pass

    # Try getting ffmpeg from static_ffmpeg
    try:
        import static_ffmpeg
        static_ffmpeg.add_paths()
    except ImportError: pass

    # Check common paths
    cwd = os.getcwd()
    possible_paths = [
        os.path.join(cwd, 'ffmpeg'), os.path.join(cwd, 'ffmpeg.exe'),
        os.path.join(cwd, 'bin', 'ffmpeg'), os.path.join(cwd, 'bin', 'ffmpeg.exe'),
    ]
    for path in possible_paths:
        if os.path.exists(path) and os.access(path, os.X_OK): return path
    
    # Check system path
    return shutil.which('ffmpeg')

FFMPEG_PATH = get_ffmpeg_path()

# 4. Custom CSS (Aesthetic Aurora UI)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global Reset & Base */
    .stApp {
        background-color: #030014; /* Deep space dark */
        background-image: 
            radial-gradient(circle at 50% -20%, #4c1d95 0%, transparent 40%),
            radial-gradient(circle at 100% 40%, #1e1b4b 0%, transparent 30%),
            radial-gradient(circle at 0% 40%, #1e1b4b 0%, transparent 30%);
        color: #e2e8f0;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Clean up Streamlit padding */
    .block-container {
        padding-top: 3.5rem;
        padding-bottom: 5rem;
        max-width: 760px;
    }

    /* Header Styling */
    .header-container {
        text-align: center;
        margin-bottom: 4rem;
        animation: fadeDown 1s cubic-bezier(0.2, 0.8, 0.2, 1);
        padding: 0 1rem;
    }
    
    .main-title {
        font-size: 4rem;
        font-weight: 800;
        background: linear-gradient(135deg, #fff 0%, #c4b5fd 50%, #818cf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.04em;
        margin-bottom: 0.75rem;
        text-shadow: 0 0 40px rgba(129, 140, 248, 0.3);
        line-height: 1.1;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.2rem;
        font-weight: 500;
        letter-spacing: 0.01em;
        background: rgba(255,255,255,0.05);
        display: inline-block;
        padding: 6px 16px;
        border-radius: 50px;
        border: 1px solid rgba(255,255,255,0.05);
        backdrop-filter: blur(5px);
    }

    /* INPUT & SEARCH BUTTON STYLING */
    /* Target the text input box */
    .stTextInput > div > div > input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        color: white !important;
        border-radius: 16px !important;
        padding: 14px 20px !important;
        font-size: 1.05rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #818cf8 !important; /* Indigo 400 */
        box-shadow: 0 0 0 4px rgba(129, 140, 248, 0.15) !important;
        background-color: rgba(15, 23, 42, 0.9) !important;
        transform: translateY(-1px);
    }

    /* Primary Search Button */
    div[data-testid="column"] .stButton button {
        border-radius: 16px !important;
        font-weight: 700 !important;
        border: none !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.9rem !important;
        height: auto !important;
        min-height: 54px;
        background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
        box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(79, 70, 229, 0.5);
    }
    
    .stButton > button:active {
        transform: translateY(0px);
    }

    /* RESULT CARD STYLING */
    /* Targeting the specific container with border=True */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 28px;
        padding: 28px;
        margin-top: 2rem;
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4);
        animation: slideUp 0.6s cubic-bezier(0.2, 0.8, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    /* Add a subtle glow accent to the top of the card */
    div[data-testid="stVerticalBlockBorderWrapper"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(129, 140, 248, 0.5), transparent);
    }

    /* Hide the default generic border color if possible, handled by border above */
    
    .video-title {
        font-size: 1.5rem;
        font-weight: 700;
        line-height: 1.3;
        color: #f8fafc;
        margin-bottom: 16px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }

    .thumbnail-img {
        border-radius: 16px;
        width: 100%;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        border: 1px solid rgba(255,255,255,0.1);
        transition: transform 0.3s ease;
    }
    
    .thumbnail-img:hover {
        transform: scale(1.02);
    }

    /* Tags */
    .meta-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 24px;
    }
    
    .tag {
        background: rgba(30, 41, 59, 0.6);
        color: #cbd5e1;
        padding: 6px 14px;
        border-radius: 10px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.05);
        display: flex;
        align-items: center;
        gap: 6px;
        transition: background 0.2s;
    }
    
    .tag:hover {
        background: rgba(30, 41, 59, 0.9);
        color: #fff;
    }

    /* Action Button (Download) */
    .download-action button {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: white !important;
        box-shadow: 0 10px 20px -5px rgba(37, 99, 235, 0.4);
        width: 100%;
        font-size: 1.1rem !important;
        padding: 0.8rem !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
    }
    .download-action button:hover {
        box-shadow: 0 15px 30px -5px rgba(37, 99, 235, 0.5);
        filter: brightness(1.1);
        transform: translateY(-2px);
    }
    
    /* Success Button Highlight (Updated) */
    .save-file-btn button {
        background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%) !important;
        background-size: 200% auto !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.5);
        border-radius: 18px !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        padding: 1rem 2rem !important;
        transition: all 0.4s ease !important;
        animation: pulse-glow 2s infinite;
    }
    
    .save-file-btn button:hover {
        background-position: right center !important;
        transform: translateY(-4px) scale(1.02) !important;
        box-shadow: 0 15px 40px rgba(16, 185, 129, 0.7) !important;
    }
    
    @keyframes pulse-glow {
        0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.6); }
        70% { box-shadow: 0 0 0 14px rgba(16, 185, 129, 0); }
        100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
    }

    /* Text Pulse Animation */
    @keyframes text-pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }

    /* Streamlit Standard Progress Bar Override */
    .stProgress > div > div > div > div {
        background-image: linear-gradient(90deg, #818cf8, #c4b5fd);
        height: 10px;
        border-radius: 10px;
    }
    
    div[data-testid="stStatusWidget"] {
        background-color: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255,255,255,0.1);
        color: #e2e8f0;
        border-radius: 16px;
    }

    /* Animations */
    @keyframes fadeDown {
        from { opacity: 0; transform: translateY(-30px); filter: blur(5px); }
        to { opacity: 1; transform: translateY(0); filter: blur(0); }
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); filter: blur(5px); }
        to { opacity: 1; transform: translateY(0); filter: blur(0); }
    }

</style>
""", unsafe_allow_html=True)

# 5. Header
st.markdown("""
    <div class="header-container">
        <h1 class="main-title">Universal YT Downloader</h1>
        <div class="subtitle">✨ Premium Video & Audio Extraction</div>
    </div>
""", unsafe_allow_html=True)

if not FFMPEG_PATH:
    st.warning("⚠️ FFmpeg not found. Merging capabilities are limited.", icon="⚠️")

# 6. Search Section
# We use vertical_alignment="bottom" to ensure the button aligns perfectly with the input box
input_col, btn_col = st.columns([1, 0.25], gap="medium", vertical_alignment="bottom")

with input_col:
    url_input = st.text_input("URL", placeholder="Paste YouTube link here...", label_visibility="visible")

with btn_col:
    # We rely on the global CSS targeting this button in this specific column structure
    search_clicked = st.button("Search", use_container_width=True)

# Logic to update state
if search_clicked or (url_input and url_input != st.session_state.current_url):
    if url_input:
        st.session_state.current_url = url_input
        st.session_state.video_info = None
        
        with st.spinner("✨ Fetching magic..."):
            try:
                ydl_opts_meta = {'quiet': True, 'no_warnings': True}
                with yt_dlp.YoutubeDL(ydl_opts_meta) as ydl:
                    info = ydl.extract_info(url_input, download=False)
                    st.session_state.video_info = {
                        'title': info.get('title', 'Unknown'),
                        'thumbnail': info.get('thumbnail', None),
                        'uploader': info.get('uploader', 'Unknown'),
                        'duration': info.get('duration', 0),
                        'views': info.get('view_count', 0),
                        'url': url_input
                    }
            except Exception as e:
                st.error(f"Failed to fetch metadata. Please check the URL.")
                st.session_state.current_url = ""

# 7. Result Section
if st.session_state.video_info:
    info = st.session_state.video_info
    
    # Calculate duration string
    duration_str = "N/A"
    if info['duration']:
        m, s = divmod(info['duration'], 60)
        h, m = divmod(m, 60)
        if h > 0:
            duration_str = f"{int(h)}:{int(m):02d}:{int(s):02d}"
        else:
            duration_str = f"{int(m)}:{int(s):02d}"
            
    views_str = f"{info['views']:,}" if info['views'] else "N/A"

    # Use native st.container with border=True to act as the "Glass Card"
    # The CSS targets div[data-testid="stVerticalBlockBorderWrapper"] to style this specific container
    with st.container(border=True):
        
        # Layout using columns inside the container
        c1, c2 = st.columns([1.2, 1.8], gap="medium")
        
        with c1:
            if info['thumbnail']:
                st.markdown(f'<img src="{info["thumbnail"]}" class="thumbnail-img">', unsafe_allow_html=True)
            else:
                st.markdown('<div class="thumbnail-img" style="height:180px; background:#27272a;"></div>', unsafe_allow_html=True)
                
        with c2:
            st.markdown(f'<div class="video-title">{info["title"]}</div>', unsafe_allow_html=True)
            
            st.markdown(f"""
                <div class="meta-tags">
                    <div class="tag">👤 {info['uploader']}</div>
                    <div class="tag">⏱️ {duration_str}</div>
                    <div class="tag">👁️ {views_str}</div>
                </div>
            """, unsafe_allow_html=True)
            
            # Spacer
            st.write("")
            
            # Download Action
            st.markdown('<div class="download-action">', unsafe_allow_html=True)
            # Using a unique key to prevent state issues
            download_clicked = st.button("Download High Quality MP4", key="dl_btn", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    # 8. Download Process Logic
    if download_clicked:
        st.write("") # Spacer
        
        # Create a visual container for the status to live in
        status_container = st.container()
        
        with status_container:
            with st.status("🚀 Initializing download engine...", expanded=True) as status:
                try:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        # Progress Bar setup (using placeholder to swap later)
                        progress_container = st.empty()
                        progress_bar = progress_container.progress(0)
                        progress_text = st.empty()
                        
                        def progress_hook(d):
                            if d['status'] == 'downloading':
                                try:
                                    total = d.get('total_bytes') or d.get('total_bytes_estimate')
                                    downloaded = d.get('downloaded_bytes', 0)
                                    if total:
                                        p = downloaded / total
                                        # Update the standard progress bar
                                        progress_bar.progress(min(p, 1.0))
                                        
                                        percent = f"{p*100:.1f}%"
                                        
                                        # Helper to remove ANSI color codes
                                        def clean_ansi(text):
                                            if not text: return "..."
                                            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                                            return ansi_escape.sub('', str(text))
                                            
                                        speed = clean_ansi(d.get('_speed_str', 'N/A'))
                                        eta = clean_ansi(d.get('_eta_str', 'N/A'))
                                        
                                        # Styled Progress Text
                                        progress_text.markdown(f"""
                                            <div style="text-align: center; font-weight: 500; color: #cbd5e1; font-size: 0.9rem; margin-top: 10px;">
                                                <span style="color: #818cf8; font-weight: 600;">{percent}</span> completed
                                                <span style="opacity: 0.3; margin: 0 10px;">|</span>
                                                Speed: <span style="color: #e2e8f0;">{speed}</span>
                                                <span style="opacity: 0.3; margin: 0 10px;">|</span>
                                                ETA: <span style="color: #e2e8f0;">{eta}</span>
                                            </div>
                                        """, unsafe_allow_html=True)
                                except: pass
                            elif d['status'] == 'finished':
                                progress_bar.progress(1.0)
                                progress_text.markdown("""
                                    <div style="text-align: center; color: #cbd5e1; font-weight: 500; margin-top: 10px;">
                                        📥 Download finished. Preparing to merge...
                                    </div>
                                """, unsafe_allow_html=True)

                        def post_processor_hook(d):
                            if d['status'] == 'started':
                                # Keep the standard progress bar (at 100%) and show styled merging text
                                progress_bar.progress(1.0)
                                
                                progress_text.markdown("""
                                    <div style="text-align: center; font-weight: 500; color: #cbd5e1; font-size: 0.9rem; margin-top: 10px;">
                                        <span style="color: #10b981; font-weight: 600;">100%</span> completed
                                        <span style="opacity: 0.3; margin: 0 10px;">|</span>
                                        Status: <span style="color: #fbbf24; font-weight: 600; animation: text-pulse 1.5s infinite;">⚙️ Merging Video & Audio...</span>
                                    </div>
                                """, unsafe_allow_html=True)
                            elif d['status'] == 'finished':
                                progress_text.markdown("""
                                    <div style="text-align: center; color: #4ade80; font-weight: 600; margin-top: 10px;">
                                        ✨ Processing Complete!
                                    </div>
                                """, unsafe_allow_html=True)

                        out_tmpl = os.path.join(tmpdir, '%(title)s.%(ext)s')
                        
                        dl_opts = {
                            'outtmpl': out_tmpl,
                            'quiet': True,
                            'no_warnings': True,
                            'restrictfilenames': True,
                            'format': 'bestvideo+bestaudio/best', # Requests best quality
                            'merge_output_format': 'mp4',
                            'progress_hooks': [progress_hook],
                            'postprocessor_hooks': [post_processor_hook],
                        }

                        if FFMPEG_PATH:
                            dl_opts['ffmpeg_location'] = FFMPEG_PATH

                        with yt_dlp.YoutubeDL(dl_opts) as ydl_down:
                            ydl_down.download([info['url']])
                        
                        # Find the file
                        files = [f for f in os.listdir(tmpdir) if os.path.isfile(os.path.join(tmpdir, f))]
                        
                        if files:
                            filename = files[0]
                            filepath = os.path.join(tmpdir, filename)
                            
                            with open(filepath, "rb") as f:
                                file_data = f.read()
                            
                            status.update(label="✅ Ready for transfer!", state="complete", expanded=False)
                            
                            # Success Message
                            st.balloons()
                            
                            # The actual download button that sends file to user
                            st.markdown("###") # Spacing
                            col_spacer, col_btn, col_spacer2 = st.columns([1, 2, 1])
                            
                            with col_btn:
                                st.markdown('<div class="save-file-btn">', unsafe_allow_html=True)
                                st.download_button(
                                    label=f"💾 Save '{filename}' to Device",
                                    data=file_data,
                                    file_name=filename,
                                    mime="video/mp4",
                                    use_container_width=True
                                )
                                st.markdown('</div>', unsafe_allow_html=True)
                        else:
                            status.update(label="❌ Error: File not found", state="error")
                
                except Exception as e:
                    status.update(label="❌ Download Failed", state="error")
                    st.error(f"Error details: {str(e)}")