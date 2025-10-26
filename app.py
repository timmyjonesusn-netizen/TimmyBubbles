from flask import Flask, render_template_string, send_from_directory
import os

app = Flask(__name__)

# -------------------------------------------------
# CONFIG: where your videos actually live
# -------------------------------------------------
# EDIT THIS LINE so it points to your TimmyVideoStore folder.
# You are on iPhone storage, so in your environment this path might look like
# "../TimmyVideoStore" or "../../TimmyVideoStore" depending on where app.py lives.
#
# Here's the plan:
# - If app.py is in "Visual Code/yourproject"
# - And TimmyVideoStore is next to Visual Code (same top level 'On My iPhone')
# Try "../TimmyVideoStore"
#
VIDEO_FOLDER = "../TimmyVideoStore"  # <-- adjust this if needed

# -------------------------------------------------
# MAIN PAGE HTML
# -------------------------------------------------
page_html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width,initial-scale=1.0,user-scalable=no,maximum-scale=1.0">
<meta charset="utf-8" />
<title>TimmyTime LIVE</title>

<style>
/* ====== GLOBAL LOOK ====== */
:root {
  --bg-grad: radial-gradient(circle at 20% 30%, #1a0029 0%, #000000 70%);
  --panel-grad: radial-gradient(circle at 20% 20%, rgba(255,0,255,0.08) 0%, rgba(0,0,0,0.6) 70%);
  --border-glow: 0 0 15px rgba(255,0,255,0.6), 0 0 40px rgba(0,150,255,0.4);
  --text-glow: 0 0 10px #fff, 0 0 30px #ff00ff, 0 0 60px #ff00ff;
  --card-bg: rgba(0,0,0,0.35);
  --card-border: rgba(255,0,255,0.4);
  --card-radius: 16px;
  --playlist-border: rgba(255,255,255,0.12);
  --playlist-bg: rgba(0,0,0,0.4);
  --playlist-radius: 14px;
  --white: #fff;
  --aqua: #69ffd8;
  --shadow-strong: 0 20px 60px rgba(0,0,0,0.9);
  --max-width: 480px;
}

/* page lock */
html, body {
  margin: 0;
  padding: 0;
  background: var(--bg-grad);
  background-attachment: fixed;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", Roboto, sans-serif;
  color: var(--white);
  width: 100%;
  height: 100%;
  overflow: hidden; /* no iOS white bounce on body */
  -webkit-user-select: none;
  user-select: none;
}

/* scrollable inner shell */
.app-shell {
  position: relative;
  box-sizing: border-box;
  width: 100%;
  max-width: var(--max-width);
  height: 100%;
  margin: 0 auto;
  padding: 16px;
  overflow-y: auto;
  overscroll-behavior: contain;
  border: 1px solid rgba(255,0,255,0.4);
  border-radius: 18px;
  box-shadow: var(--border-glow);
  background: var(--panel-grad);
}

/* header / counter */
.counter-wrap {
  text-align: center;
  padding: 8px 12px 20px;
}

.counter-topline {
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--white);
  text-shadow: var(--text-glow);
}

.counter-number {
  font-size: 4rem;
  font-weight: 800;
  line-height: 1.0;
  margin-top: 8px;
  color: var(--white);
  text-shadow: var(--text-glow);
}

.counter-subline {
  font-size: 1.8rem;
  font-weight: 700;
  margin-top: 12px;
  color: var(--white);
  text-shadow: var(--text-glow);
}

/* tapable hitbox */
.counter-number-touchzone {
  display: inline-block;
  padding: 8px 12px;
  border-radius: 12px;
}

/* video frame */
.video-wrap {
  background: #000;
  border-radius: 16px;
  box-shadow: 0 0 15px #ff00ff, 0 0 60px rgba(255,0,255,0.4);
  border: 1px solid rgba(255,0,255,0.5);
  margin-top: 20px;
  overflow: hidden;
}

.video-wrap video {
  width: 100%;
  height: auto;
  display: block;
  background:#000;
}

/* playlist list box */
.playlist-list {
  margin-top: 24px;
  border: 1px solid var(--card-border);
  border-radius: var(--card-radius);
  background: var(--card-bg);
  box-shadow: var(--shadow-strong), var(--border-glow);
  overflow: hidden;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.playlist-btn {
  display: block;
  width: 100%;
  background: var(--playlist-bg);
  border-bottom: 1px solid var(--playlist-border);
  padding: 20px;
  box-sizing: border-box;
  font-size: 1.6rem;
  font-weight: 700;
  line-height: 1.2;
  color: var(--white);
  text-decoration: none;
  text-shadow: 0 0 10px #fff, 0 0 30px #ffffffaa;
}

.playlist-btn:last-child {
  border-bottom: 0;
}

.playlist-btn:active {
  background: rgba(255,0,255,0.15);
}

/* sig */
.sig-line {
  color: var(--aqua);
  text-align: center;
  font-size: 1rem;
  font-weight: 500;
  padding: 24px 12px 80px;
  text-shadow: 0 0 10px rgba(105,255,216,0.8), 0 0 30px rgba(105,255,216,0.4);
}

/* bubbles layer */
#bubbles {
  position: fixed;
  left: 0;
  top: 0;
  width:100%;
  height:100%;
  overflow:hidden;
  pointer-events: auto; /* can tap to pop */
  z-index: 0;
}

.bubble {
  position:absolute;
  border-radius:50%;
  background: radial-gradient(circle at 30% 30%, rgba(255,0,255,0.9) 0%, rgba(0,0,0,0) 70%);
  box-shadow:
    0 0 10px rgba(255,0,255,0.8),
    0 0 40px rgba(0,150,255,0.6),
    0 0 80px rgba(255,0,255,0.4);
  animation: floatUp linear infinite;
}

@keyframes floatUp {
  0%   { transform: translateY(0) scale(1);     opacity:1; }
  100% { transform: translateY(-200vh) scale(0.6); opacity:0; }
}

/* stacking order */
.app-shell {
  position: relative;
  z-index: 5;
}
.counter-wrap,
.video-wrap,
.playlist-list,
.sig-line {
  position: relative;
  z-index: 10;
}

/* mobile font scale */
@media (max-width:480px){
  .counter-topline { font-size: 1.6rem; }
  .counter-number  { font-size: 3rem; }
  .counter-subline { font-size: 1.4rem; }
  .playlist-btn    { font-size: 1.4rem; }
}
</style>
</head>

<body>

<!-- bubble effects behind everything -->
<div id="bubbles"></div>

<!-- main UI panel -->
<div class="app-shell" id="appShell">

  <!-- COUNTER -->
  <div class="counter-wrap">
    <div class="counter-topline">Now Serving</div>

    <div class="counter-number counter-number-touchzone" id="count-number">
      999,999
    </div>

    <div class="counter-subline">First Punch Only</div>
  </div>

  <!-- VIDEO PLAYER -->
  <div class="video-wrap">
    <video id="mainVideo"
      controls
      preload="auto"
      poster=""
      playsinline
    >
      <source src="/videos/Info.mp4" type="video/mp4">
      Your browser does not support the video tag.
    </video>
  </div>

  <!-- PLAYLISTS -->
  <div class="playlist-list">
    <a class="playlist-btn"
      href="https://suno.com/playlist/PUT-YOUR-PLAYLIST-1-ID"
      target="_blank" rel="noopener noreferrer">
      🔊 Playlist 1
    </a>

    <a class="playlist-btn"
      href="https://suno.com/playlist/PUT-YOUR-PLAYLIST-2-ID"
      target="_blank" rel="noopener noreferrer">
      🔥 Playlist 2
    </a>

    <a class="playlist-btn"
      href="https://suno.com/playlist/PUT-YOUR-PLAYLIST-3-ID"
      target="_blank" rel="noopener noreferrer">
      💀 Playlist 3
    </a>

    <a class="playlist-btn"
      href="https://suno.com/playlist/PUT-YOUR-PLAYLIST-4-ID"
      target="_blank" rel="noopener noreferrer">
      💅 Playlist 4
    </a>

    <a class="playlist-btn"
      href="https://suno.com/playlist/b11f5b9a-b2d1-46f2-a307-e62491ae2479"
      target="_blank" rel="noopener noreferrer">
      🚀 Playlist 5
    </a>
  </div>

  <!-- SIGNATURE -->
  <div class="sig-line">
    Made by Timmy · iPhone 17 Pro Max² · tb
  </div>

</div><!-- /app-shell -->

<script>
/* Stop body bounce; only scroll inside .app-shell */
const appShell = document.getElementById("appShell");
appShell.addEventListener('touchmove', (e)=>{}, {passive:false});

document.addEventListener('touchmove', function(e){
  if(!appShell.contains(e.target)){
    e.preventDefault();
  }
}, {passive:false});

/* Tap counter to edit number */
function editCount(evt){
  evt.stopPropagation();
  const el = document.getElementById("count-number");
  let cur = el.innerText.trim();
  let next = prompt("Set new number:", cur);
  if(next !== null && next !== ""){
    el.innerText = next;
  }
}
document.getElementById("count-number").addEventListener("click", editCount);

/* Floating bubbles that pop on tap */
const bubbleContainer = document.getElementById("bubbles");

function makeBubble(){
  const b = document.createElement("div");
  b.className = "bubble";

  const size = 20 + Math.random()*70; // 20px - 90px
  b.style.width = size + "px";
  b.style.height = size + "px";

  const startX = Math.random()*100;
  b.style.left = startX + "vw";

  const dur = 6 + Math.random()*10;
  b.style.animationDuration = dur + "s";

  b.addEventListener("click", (evt)=>{
    evt.stopPropagation();
    b.style.transition = "all 0.15s ease-out";
    b.style.transform = "scale(1.3)";
    b.style.opacity = "0";
    setTimeout(()=>{ b.remove(); }, 150);
  }, {passive:true});

  bubbleContainer.appendChild(b);

  setTimeout(()=>{ b.remove(); }, dur*1000 + 200);
}

setInterval(()=>{
  const howMany = 1 + Math.floor(Math.random()*3);
  for(let i=0;i<howMany;i++){
    makeBubble();
  }
}, 1200);
</script>

</body>
</html>
"""

# -------------------------------------------------
# ROUTES
# -------------------------------------------------

@app.route("/")
def home():
    return render_template_string(page_html)

@app.route("/videos/<path:filename>")
def serve_video(filename):
    # Serve files directly from TimmyVideoStore
    return send_from_directory(VIDEO_FOLDER, filename)

# -------------------------------------------------
# RUN LOCAL ONLY
# -------------------------------------------------
if __name__ == "__main__":
    # This is LOCAL. No Render, no gunicorn.
    # 0.0.0.0 lets you hit it from same Wi-Fi if you want,
    # but it's still just whatever device is running it.
    app.run(host="0.0.0.0", port=5000, debug=True)
