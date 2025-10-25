// static/main.js
// Keep this file; it handles all the UI logic.

(async function(){
  const counterEl = document.getElementById("counter");
  const videoEl = document.getElementById("heroVideo");
  const videoSelect = document.getElementById("videoSelect");
  const setVideoBtn = document.getElementById("setVideoBtn");
  const bubbleLayer = document.getElementById("bubbleLayer");

  // helper fetch wrapper
  async function api(path, opts){
    const res = await fetch(path, opts);
    if (!res.ok) {
      const txt = await res.text();
      throw new Error(txt || res.statusText);
    }
    return res.json();
  }

  // load videos list and active selection
  async function loadVideos(){
    try{
      const data = await api("/api/videos");
      videoSelect.innerHTML = "";
      data.videos.forEach(v=>{
        const opt = document.createElement("option");
        opt.value = v;
        opt.textContent = v;
        if (data.active_video === v) opt.selected = true;
        videoSelect.appendChild(opt);
      });
      if (data.active_video) {
        setActiveVideo(data.active_video);
      } else if (data.videos.length){
        setActiveVideo(data.videos[0]);
      } else {
        // no videos: show placeholder
        videoEl.poster = "/static/placeholder.png";
      }
    }catch(e){
      console.warn("Failed to load videos:", e);
    }
  }

  async function setActiveVideo(filename){
    if (!filename) return;
    // point video src to /videos/<filename>
    if (videoEl.getAttribute("src") !== `/videos/${filename}`){
      videoEl.pause();
      videoEl.setAttribute("src", `/videos/${filename}`);
      videoEl.load();
      // autoplay attempts; some mobile browsers require user gesture to unmute/play
      try { await videoEl.play(); } catch(e) { /* ignore */ }
    }
  }

  setVideoBtn.addEventListener("click", async ()=>{
    const filename = videoSelect.value;
    try{
      await api("/api/set_video", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({filename})
      });
      await setActiveVideo(filename);
      flashOutline(setVideoBtn);
    }catch(e){
      alert("Set failed: " + e.message);
    }
  });

  // increment counter and update UI
  async function hitAndUpdate(){
    try{
      const data = await api("/api/hit", {method:"POST"});
      counterEl.textContent = numberWithCommas(data.count);
      if (data.active_video) setActiveVideo(data.active_video);
    }catch(e){
      console.warn("Hit failed:", e);
    }
  }

  function numberWithCommas(x){
    if (x===undefined || x===null) return "—";
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  // small flash effect for the set button
  function flashOutline(el){
    el.animate([{boxShadow:"0 0 0 0 rgba(255,154,60,0.0)"},
                {boxShadow:"0 0 12px 4px rgba(255,154,60,0.18)"},
                {boxShadow:"0 0 0 0 rgba(255,154,60,0.0)"}], {duration:600});
  }

  // --- Bubble system ---
  const colorPool = [
    ['#ffffff', 0.14],
    ['#8c3bff', 0.34],
    ['#ff50e6', 0.34],
    ['#ff9a3c', 0.18]
  ];
  function pickColor(){
    // weighted pick
    const r = Math.random();
    let acc = 0;
    for (const c of colorPool){
      acc += c[1];
      if (r <= acc) return c[0];
    }
    return colorPool[0][0];
  }

  function spawnBubble(opts = {}){
    const bw = bubbleLayer.clientWidth;
    const bh = bubbleLayer.clientHeight;
    const size = opts.size || Math.floor(12 + Math.random()*140); // px
    const left = (Math.random() * 110) - 5; // allow slight overflow
    const color = opts.color || pickColor();

    const b = document.createElement("div");
    b.className = "bubble";
    b.style.width = size + "px";
    b.style.height = size + "px";
    b.style.left = left + "%";
    b.style.bottom = "-20%";
    b.style.background = `radial-gradient(circle at 30% 30%, rgba(255,255,255,0.85) 0%, ${color} 30%, rgba(0,0,0,0) 100%)`;
    b.style.opacity = (0.12 + Math.random()*0.9).toString();
    b.style.transform = `translateY(0) scale(${0.9 + Math.random()*0.3})`;
    b.style.borderRadius = "50%";
    b.style.animation = `bubbleUp ${10 + Math.random()*26}s linear forwards`;
    b.style.pointerEvents = "none";
    b.style.filter = `drop-shadow(0 6px 18px rgba(0,0,0,0.45))`;
    b.style.transition = "opacity 0.4s linear";

    // add neon pulse
    const pulseDuration = 3 + Math.random()*4;
    b.style.animation += `, neonPulse ${pulseDuration}s ease-in-out ${Math.random()*pulseDuration}s infinite`;

    bubbleLayer.appendChild(b);

    // remove after animation finishes (give it generous time)
    setTimeout(()=> {
      b.style.opacity = "0";
      setTimeout(()=> b.remove(), 1200);
    }, (12000 + Math.random()*26000));
  }

  // CSS keyframe injection for bubble rising (since not in CSS file)
  const styleSheet = document.createElement("style");
  styleSheet.innerHTML = `
    @keyframes bubbleUp {
      0% { transform: translateY(0) }
      100% { transform: translateY(-140vh) }
    }
    @keyframes neonPulse {
      0%{ transform: translateY(0) scale(1); filter: drop-shadow(0 0 6px rgba(255,80,230,0.9)); }
      50%{ transform: translateY(-6px) scale(1.03); filter: drop-shadow(0 0 22px rgba(140,59,255,0.6)); }
      100%{ transform: translateY(0) scale(1); filter: drop-shadow(0 0 6px rgba(255,80,230,0.9)); }
    }
  `;
  document.head.appendChild(styleSheet);

  // continuous spawn loop with mix of sizes and rates
  function startBubbles(){
    // burst small fast lane
    setInterval(()=> { spawnBubble({size: 10 + Math.random()*36}); }, 350 + Math.random()*300);

    // slower medium bubbles
    setInterval(()=> { spawnBubble({size: 30 + Math.random()*80}); }, 900 + Math.random()*1200);

    // occasional big bubbles
    setInterval(()=> { if (Math.random()<0.35) spawnBubble({size: 90 + Math.random()*180}); }, 2400 + Math.random()*2000);
  }

  // initial calls
  await loadVideos();
  await hitAndUpdate();
  startBubbles();

  // refresh counter every 30s (don't auto-increment when refreshing)
  setInterval(async ()=> {
    try {
      const data = await api("/api/count");
      counterEl.textContent = numberWithCommas(data.count);
    } catch(e){}
  }, 30000);

  // mobile friendly: if user taps video, toggle muted/play
  videoEl.addEventListener("click", async () => {
    if (videoEl.paused) {
      try { await videoEl.play(); } catch(e){}
    } else {
      videoEl.pause();
    }
  });

})();
