from flask import Flask, render_template_string, send_from_directory
import threading, webbrowser, time, socket, os, random

app = Flask(__name__)

html = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>TimmyBubbles</title>
<style>
:root {
  --bgGrad: radial-gradient(circle at 20% 30%, #1a0029 0%, #000 70%);
  --borderGrad: linear-gradient(135deg,#ff66ff 0%,#8a00ff 50%,#ff66ff 100%);
}

html,body{
  margin:0;
  padding:0;
  width:100%;
  height:100%;
  overflow-y:auto;
  overflow-x:hidden;
  overscroll-behavior:none;
  -webkit-overflow-scrolling:touch;
  background:var(--bgGrad);
  font-family:-apple-system,BlinkMacSystemFont,"Arial",sans-serif;
  color:#fff;
  text-align:center;
}

/* Bubble background */
canvas#bubbles{
  position:fixed;
  top:0;left:0;
  width:100%;height:100%;
  z-index:0;
}

/* Floating card style */
.card-shell{
  position:relative;
  width:90%;
  max-width:420px;
  margin:2rem auto;
  padding:1rem 1rem 1.25rem;
  border-radius:16px;
  background:rgba(0,0,0,0.03);
  backdrop-filter:blur(10px) saturate(140%);
  -webkit-backdrop-filter:blur(10px) saturate(140%);
  box-shadow:0 20px 50px rgba(0,0,0,0.8);
  border:1px solid rgba(255,255,255,0.08);
  z-index:2;
}
.card-shell::before{
  content:"";
  position:absolute;
  inset:0;
  border-radius:16px;
  padding:1px;
  background:var(--borderGrad);
  mask:linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask:linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite:exclude;
  -webkit-mask-composite:xor;
  pointer-events:none;
}

/* Counter */
#count-number{
  display:block;
  font-size:3rem;
  font-weight:700;
  margin:0.2rem 0 1rem;
  text-shadow:
    0 0 15px rgba(255,102,255,1),
    0 0 30px rgba(170,0,255,0.9),
    0 0 60px rgba(255,120,50,0.7),
    0 0 90px rgba(50,140,255,0.5);
  cursor:pointer;
}

/* Video */
.video-wrap{
  width:100%;
  border-radius:12px;
  overflow:hidden;
  background:#000;
  border:1px solid rgba(255,255,255,0.18);
  box-shadow:0 15px 40px rgba(0,0,0,0.9);
  margin-bottom:.75rem;
  position:relative;
}
#hero-video{
  width:100%;
  display:block;
  background:#000;
  border-radius:12px;
  opacity:0;
  animation:vidFade 0.6s ease-out forwards;
}
@keyframes vidFade {
  0%{opacity:0;filter:blur(8px) brightness(0.4);}
  60%{opacity:1;filter:blur(2px) brightness(1);}
  100%{opacity:1;filter:blur(0) brightness(1);}
}

/* Playlist buttons */
.playlist-wrap{
  display:flex;
  flex-direction:column;
  gap:.6rem;
}
.playlist-btn{
  display:block;
  text-decoration:none;
  color:#fff;
  font-size:1rem;
  font-weight:600;
  padding:.7rem 1rem;
  border-radius:10px;
  background:rgba(0,0,0,0.18);
  border:1px solid rgba(255,255,255,0.22);
  box-shadow:0 12px 30px rgba(0,0,0,0.8);
}
.playlist-btn:active{
  background:rgba(255,255,255,0.15);
  box-shadow:0 0 20px rgba(255,102,255,1),
             0 0 40px rgba(170,0,255,0.7);
}

/* Signature */
.sig-line{
  font-size:.7rem;
  color:#ccc;
  text-shadow:0 0 8px rgba(255,102,255,1);
  opacity:0.8;
  margin-top:.75rem;
}
</style>
</head>
<body>
<canvas id="bubbles"></canvas>

<!-- Counter -->
<div class="card-shell">
  <div>Now Serving</div>
  <div id="count-number" onclick="editCount(event)">999,999</div>
  <div>First Punch Only</div>
</div>

<!-- Video -->
<div class="card-shell video-wrap">
  <video id="hero-video" src="/media/clip.mp4" playsinline autoplay loop muted preload="auto"></video>
</div>

<!-- Playlists -->
<div class="card-shell">
  <div class="playlist-wrap">
    <a class="playlist-btn" href="https://suno.com/playlist/01b65a04-d231-4574-bbb6-713997ca5b44" target="_blank">🔊 Playlist 1</a>
    <a class="playlist-btn" href="https://suno.com/playlist/2ec04889-1c23-4e2d-9c27-8a2b6475da4b" target="_blank">🔥 Playlist 2</a>
    <a class="playlist-btn" href="https://suno.com/playlist/f378a880-6712-4147-a7b6-ff564ee0a3e3" target="_blank">💀 Playlist 3</a>
    <a class="playlist-btn" href="https://suno.com/playlist/1d9e6979-5362-4cee-8962-56429962b7a3" target="_blank">💅 Playlist 4</a>
    <a class="playlist-btn" href="https://suno.com/playlist/b11f5b9a-b2d1-46f2-a307-e62491ae2479" target="_blank">🚀 Playlist 5</a>
  </div>
  <div class="sig-line">Made by Timmy · iPhone 17 Pro Max² .tb</div>
</div>

<script>
/* editable counter */
function editCount(evt){
  const el=document.getElementById("count-number");
  let cur=el.innerText.trim();
  let next=prompt("Set new number:",cur);
  if(next!==null&&next!==""){el.innerText=next;}
}

/* fade-in video fix for iOS autoplay */
document.addEventListener("DOMContentLoaded",()=>{
  const vid=document.getElementById("hero-video");
  if(vid){const p=vid.play();if(p&&p.catch){p.catch(()=>{setTimeout(()=>{vid.play().catch(()=>{});},500);});}}
});

/* bubbles */
const c=document.getElementById("bubbles"),ctx=c.getContext("2d");
function sizeCanvas(){c.width=window.innerWidth;c.height=window.innerHeight;}
sizeCanvas();window.addEventListener("resize",sizeCanvas);

const palette=["rgba(255,102,255,0.6)","rgba(170,0,255,0.6)","rgba(255,120,50,0.6)","rgba(50,140,255,0.6)"];
let bubbles=[];for(let i=0;i<80;i++)bubbles.push(make());
function make(){return{x:Math.random()*c.width,y:Math.random()*c.height,r:Math.random()*22+6,color:palette[Math.floor(Math.random()*palette.length)],v:Math.random()*0.8+0.3,popped:false,popScale:1,popAlpha:1};}
function popNearest(x,y){let closest=null,dMin=Infinity;for(let b of bubbles){let dx=b.x-x,dy=b.y-y,d2=dx*dx+dy*dy;if(d2<dMin){dMin=d2;closest=b;}}if(closest)closest.popped=true;}
document.addEventListener("click",e=>popNearest(e.clientX,e.clientY),{passive:true});
function draw(){
  ctx.clearRect(0,0,c.width,c.height);
  for(let b of bubbles){
    if(!b.popped){ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,Math.PI*2);ctx.fillStyle=b.color;ctx.fill();
      b.y-=b.v;if(b.y+b.r<0){Object.assign(b,make());b.y=c.height+b.r;}}
    else{b.popScale*=0.7;b.popAlpha*=0.6;
      if(b.popAlpha>0.05){ctx.beginPath();ctx.arc(b.x,b.y,b.r*b.popScale,0,Math.PI*2);
        ctx.fillStyle="rgba(255,102,255,"+b.popAlpha.toFixed(2)+")";ctx.fill();}
      else{Object.assign(b,make());}}
  }
  requestAnimationFrame(draw);
}
draw();
</script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(html)

@app.route("/media/<path:filename>")
def media(filename):
    return send_from_directory(os.getcwd(), filename)

def get_ip():
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8",80))
        ip=s.getsockname()[0]
    except Exception:
        ip="127.0.0.1"
    finally:
        s.close()
    return ip

if __name__=="__main__":
    port=random.randint(5050,5090)
    ip=get_ip()
    print(f"💎 TimmyBubbles running at http://{ip}:{port}")
    def run(): app.run(host="0.0.0.0",port=port,debug=False,use_reloader=False)
    t=threading.Thread(target=run,daemon=True);t.start()
    time.sleep(1)
    webbrowser.open(f"http://127.0.0.1:{port}")
    while True: time.sleep(1)
