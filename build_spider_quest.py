# build_spider_quest.py
# Generates:
# - /books/*.pdf (two sizes)
# - PWA app files: index.html, style.css, script.js, manifest.json, service-worker.js, icons
# - Embeds base64 of PDFs into script.js for "Open in New Tab" AND keeps raw files for direct links.

from PIL import Image, ImageDraw, ImageFont
import os, base64, json

ROOT = os.path.abspath(".")
BOOKS = os.path.join(ROOT, "books")
os.makedirs(BOOKS, exist_ok=True)

def font(sz, bold=False):
    path = "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"
    fallback = "/Library/Fonts/Arial.ttf"
    try:
        return ImageFont.truetype(fallback if not bold else "/Library/Fonts/Arial Bold.ttf", sz)
    except:
        # generic fallback
        return ImageFont.load_default()

def add_art_placeholder(draw, box, title, note):
    x0,y0,x1,y1 = box
    draw.rectangle(box, fill=(255,248,230))
    dash = 12
    for x in range(x0, x1, dash*2):
        draw.line([(x, y0), (min(x+dash, x1), y0)], fill=(255,140,0), width=4)
        draw.line([(x, y1), (min(x+dash, x1), y1)], fill=(255,140,0), width=4)
    for y in range(y0, y1, dash*2):
        draw.line([(x0, y), (x0, min(y+dash, y1))], fill=(255,140,0), width=4)
        draw.line([(x1, y), (x1, min(y+dash, y1))], fill=(255,140,0), width=4)
    tF = font(36, True); nF = font(22)
    draw.text((x0+20, y0+10), f"ART: {title}", font=tF, fill=(80,40,0))
    import textwrap
    cur = y0+60
    for ln in textwrap.wrap(note, width=60):
        draw.text((x0+20, cur), ln, font=nF, fill=(100,60,0))
        cur += 28

PAGES = [
    ("Cover", "Spiders! Eight Legs of Awesome\nTagline: Eight legs. Endless surprises.",
     "Cover Illustration", "Big friendly spider on a rainbow web. Title letters woven into strands."),
    ("Introduction", "Some people say 'Eek!' when they see a spider. But not you! You’re about to discover how amazing they are.",
     "Kid Meets Spider", "Kid with magnifying glass; smiling garden spider on a flower."),
    ("Body Parts", "Two body parts: cephalothorax (head+chest) and abdomen (tummy).",
     "Labeled Diagram", "Eyes, fangs, pedipalps, cephalothorax, abdomen, spinnerets."),
    ("Eight Legs", "Eight legs help spiders move fast, climb walls, and hang upside-down.",
     "Action Poses", "Dancing, climbing, hanging."),
    ("Silk Factory", "Silk comes from tiny nozzles called spinnerets at the tip of the abdomen.",
     "Spinneret Close-up", "Multiple spinnerets extruding silk."),
    ("Web Wonders", "Orb webs, funnel webs, sheet webs—each spider builds its own style.",
     "Web Types", "Three web types side-by-side with builder spiders."),
    ("Jumping Spiders", "Daredevils! They jump up to 50 times their body length.",
     "Super Jump", "Cape, motion streaks."),
    ("Tarantulas", "Big, furry, gentle to humans, fierce to bugs.",
     "Burrow Buddy", "Fluffy tarantula peeking from burrow."),
    ("Black Widow", "Red hourglass says: Danger! Admire from afar.",
     "Iconic Hourglass", "Stylized widow with caution motifs."),
    ("Daddy Longlegs", "Surprise: not true spiders—distant cousins.",
     "Family Photo", "Spider vs daddy longlegs lineup."),
    ("Spider Vision", "Most have eight eyes. Some see great, some not so much.",
     "Eye Array", "Close-up eyes; goofy glasses."),
    ("Hunters vs Trappers", "Hunters chase prey; trappers wait in webs.",
     "Two Styles", "Sneakers vs hammock."),
    ("Spider Senses", "They feel tiny vibrations through their legs—like a phone buzz.",
     "Vibration Waves", "Waves traveling along silk."),
    ("Super Silk Uses", "Silk for egg sacs, sleeping bags, safety ropes.",
     "Silk Toolkit", "Three-panel: egg sac, sleeping bag, dragline."),
    ("Baby Spiders", "Spiderlings hatch and sometimes balloon on silk.",
     "Ballooning", "Spiderlings drifting on breeze."),
    ("Dangerous to People?", "Most are harmless and eat pests.",
     "Bug Busters", "Spider with 'Bug Buster' badge."),
    ("Record Breakers", "Biggest: Goliath birdeater. Smallest: Samoan moss spider.",
     "Size Scale", "Plate vs sprinkle."),
    ("Camouflage Masters", "Some blend with flowers, leaves, or sticks.",
     "Flower Disguise", "Crab spider as a petal."),
    ("Spider Strength", "Silk is stronger than steel of same thickness—also stretchy!",
     "Silk Lifter", "Silk dumbbell."),
    ("Spiders Everywhere", "They live almost everywhere—except Antarctica.",
     "World Map", "Waving spiders; snowflake over Antarctica."),
    ("Myth Busting", "Myth: Spiders crawl into your mouth at night. Truth: Nope.",
     "Myth vs Truth", "Silly myth vs friendly truth."),
    ("Famous Spiders", "Charlotte, Anansi, Shelob—spiders star in stories worldwide.",
     "Storybook", "Non-infringing vignettes."),
    ("You and Spiders", "Watch one next time—you might be surprised.",
     "Garden Watch", "Child observing orb-weaver."),
    ("Quiz Time", "1) True/False: All spiders spin webs. 2) Biggest spider? 3) Legs?",
     "Game Show", "Stage lights; spider host."),
    ("Closing", "Small creatures, big jobs. Now you’re a spider expert!",
     "Farewell Web", "Golden web wave.")
]

def make_book(path, size_px):
    W,H = size_px
    DPI=300
    margin = int(0.08 * min(W,H))
    headF = font(int(0.045*min(W,H)), True)
    bodyF = font(int(0.035*min(W,H)))
    smallF = font(int(0.028*min(W,H)))
    pages = []
    for i,(title, body, atitle, anote) in enumerate(PAGES, start=1):
        img = Image.new("RGB", (W,H), (255,255,255))
        d = ImageDraw.Draw(img)
        d.text((margin, margin), title, font=headF, fill=(20,20,20))
        # left text
        col_x = margin
        col_y = int(margin*1.8)
        col_w = int(W*0.48) - margin
        words = body.split()
        line = ""; lh = int(bodyF.size*1.35); cur = col_y
        for w in words:
            test = (line + " " + w).strip()
            if d.textlength(test, font=bodyF) <= col_w:
                line = test
            else:
                d.text((col_x, cur), line, font=bodyF, fill=(30,30,30)); cur += lh; line = w
        if line:
            d.text((col_x, cur), line, font=bodyF, fill=(30,30,30))
        # art placeholder
        x0 = int(W*0.52); y0 = int(margin*1.2); x1 = W - margin; y1 = int(H*0.62)
        add_art_placeholder(d, (x0,y0,x1,y1), atitle, anote)
        # footer
        d.text((margin, H - margin), f"Page {i} • {int(W/300)}x{int(H/300)}in @300DPI", font=smallF, fill=(120,120,120))
        pages.append(img)
    pages[0].save(path, "PDF", resolution=300, save_all=True, append_images=pages[1:])

# Generate both PDFs
square_pdf = os.path.join(BOOKS, "Spiders_Eight_Legs_of_Awesome_8p5x8p5.pdf")
portrait_pdf = os.path.join(BOOKS, "Spiders_Eight_Legs_of_Awesome_8x10.pdf")
make_book(square_pdf, (2550,2550))     # 8.5x8.5 @300 dpi
make_book(portrait_pdf, (2400,3000))   # 8x10 @300 dpi

# Encode PDFs for embedded open-in-tab
with open(square_pdf,"rb") as f: square_b64 = base64.b64encode(f.read()).decode("ascii")
with open(portrait_pdf,"rb") as f: portrait_b64 = base64.b64encode(f.read()).decode("ascii")

# --- PWA files ---
INDEX = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#ffd166">
<link rel="manifest" href="manifest.json">
<link rel="icon" href="icon-192.png">
<title>Spider Quest (PWA)</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<div id="app">
  <header>
    <h1>🕷️ Spider Quest</h1>
    <p>Play. Learn. Earn badges. (2nd–3rd grade)</p>
    <div class="controls">
      <button id="btnInstall" class="ghost">Install App</button>
      <button id="btnDashboard">Parent/Teacher Dashboard</button>
      <button id="btnBooks">Books (Download PDFs)</button>
      <label class="switch">
        <input type="checkbox" id="audioToggle" checked><span class="slider"></span>
      </label><span class="label">Audio</span>
    </div>
  </header>
  <nav>
    <button id="btnGarden">Sunny Garden (Web Builder)</button>
    <button id="btnBackyard">Backyard at Night (Bug Catcher)</button>
    <button id="btnQuiz">Fact Frenzy (Quiz)</button>
    <button id="btnReset">Reset</button>
  </nav>
  <section id="hud">
    <div id="badgeBar">Badges: <span id="badges"></span></div>
    <div id="factCard">Tip: Spiders have two body parts!</div>
  </section>
  <main><canvas id="gameCanvas" width="900" height="600"></canvas></main>
  <footer><small>Spider Quest • PWA • Works offline after first load</small></footer>
</div>

<!-- Dashboard Modal -->
<div id="modal" class="modal hidden">
  <div class="modal-content">
    <div class="modal-header"><h2>Parent/Teacher Dashboard</h2><button id="closeModal" class="close">✕</button></div>
    <div class="modal-body">
      <section class="panel"><h3>Progress</h3><ul id="progressList"></ul></section>
      <section class="panel"><h3>Learning Stats</h3>
        <div id="stats">
          <p>Total Play Time: <span id="statTime">0m</span></p>
          <p>Quizzes Completed: <span id="statQuizzes">0</span></p>
          <p>Correct Answers: <span id="statCorrect">0</span></p>
          <p>Bug Catch Scores (last 5): <span id="statBugs">-</span></p>
        </div>
      </section>
      <section class="panel"><h3>Controls</h3>
        <div class="controls-row"><label>Audio:</label><input type="checkbox" id="dashAudioToggle" checked></div>
        <div class="controls-row"><label>Reset All Progress:</label><button id="dashReset" class="danger">Reset</button></div>
      </section>
    </div>
  </div>
</div>

<!-- Books Modal -->
<div id="modalBooks" class="modal hidden">
  <div class="modal-content">
    <div class="modal-header"><h2>Download the Books</h2><button id="closeModalBooks" class="close">✕</button></div>
    <div class="modal-body" style="grid-template-columns:1fr;">
      <section class="panel">
        <h3>Choose a format</h3>
        <p>Both options are embedded (works offline) and also available in the <code>/books</code> folder.</p>
        <div style="display:flex; gap:12px; flex-wrap:wrap;">
          <button id="dlSquare" style="background:#90ee90; border:0; padding:10px 14px; border-radius:12px; font-weight:700; cursor:pointer;">Download 8.5×8.5 (Square)</button>
          <button id="openSquare" style="background:#ffe680; border:0; padding:10px 14px; border-radius:12px; font-weight:700; cursor:pointer;">Open in New Tab (Square)</button>
          <button id="dlPortrait" style="background:#add8e6; border:0; padding:10px 14px; border-radius:12px; font-weight:700; cursor:pointer;">Download 8×10 (Portrait)</button>
          <button id="openPortrait" style="background:#ffe680; border:0; padding:10px 14px; border-radius:12px; font-weight:700; cursor:pointer;">Open in New Tab (Portrait)</button>
        </div>
        <h4 style="margin-top:10px;">Direct File Links (Right-click → “Save Link As…”) </h4>
        <ul>
          <li><a href="./books/Spiders_Eight_Legs_of_Awesome_8p5x8p5.pdf" target="_blank">Open Raw File (Square)</a></li>
          <li><a href="./books/Spiders_Eight_Legs_of_Awesome_8x10.pdf" target="_blank">Open Raw File (Portrait)</a></li>
        </ul>
      </section>
    </div>
  </div>
</div>

<script src="script.js"></script>
</body></html>
"""

STYLE = """*{box-sizing:border-box}
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif;margin:0;background:linear-gradient(180deg,#fff7e6,#ffe6f2);color:#222}
header{text-align:center;padding:12px 10px}
h1{margin:6px 0}
.controls{display:flex;gap:8px;justify-content:center;align-items:center;flex-wrap:wrap;margin-top:6px}
nav{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;padding:8px}
nav button{padding:10px 14px;border:0;border-radius:12px;background:#8be9fd;cursor:pointer;font-weight:700}
nav button:hover{transform:translateY(-2px)}
#hud{display:flex;justify-content:space-between;gap:8px;padding:0 16px;align-items:center}
#badgeBar{padding:6px 10px;background:#ffd166;border-radius:8px}
#factCard{padding:6px 10px;background:#caffbf;border-radius:8px}
main{display:flex;justify-content:center;padding:12px}
canvas{border:6px solid #ff6;border-radius:12px;background:#fefefe;box-shadow:0 6px 18px rgba(0,0,0,.15)}
footer{text-align:center;padding:10px;color:#444}
.ghost{background:#eee}
.switch{position:relative;display:inline-block;width:54px;height:28px}
.switch input{display:none}
.slider{position:absolute;cursor:pointer;top:0;left:0;right:0;bottom:0;background:#ccc;transition:.2s;border-radius:28px}
.slider:before{position:absolute;content:"";height:22px;width:22px;left:3px;bottom:3px;background:white;transition:.2s;border-radius:50%}
input:checked + .slider{background:#4CAF50}
input:checked + .slider:before{transform:translateX(26px)}
.label{font-size:14px;margin-left:4px}
.modal{position:fixed;inset:0;background:rgba(0,0,0,.4);display:flex;align-items:center;justify-content:center;padding:12px}
.modal.hidden{display:none}
.modal-content{background:#fff;border-radius:14px;max-width:900px;width:100%;box-shadow:0 8px 24px rgba(0,0,0,.2);overflow:hidden}
.modal-header{display:flex;justify-content:space-between;align-items:center;padding:12px 16px;background:#ffd166}
.modal-body{display:grid;gap:12px;grid-template-columns:1fr 1fr; padding:16px}
.panel{background:#fffaf0;border:2px dashed #ffb703;border-radius:12px;padding:12px}
.close{background:#0000;border:0;font-size:20px;cursor:pointer}
.danger{background:#ff6b6b;color:#fff;border:0;padding:8px 12px;border-radius:10px;cursor:pointer}
.controls-row{display:flex;align-items:center;gap:12px;margin-top:6px}
@media (max-width:800px){.modal-body{grid-template-columns:1fr}}
"""

SCRIPT = """(()=>{{
  // PWA install + SW
  let deferredPrompt=null;
  const btnInstall=document.getElementById('btnInstall');
  window.addEventListener('beforeinstallprompt',(e)=>{{e.preventDefault();deferredPrompt=e;btnInstall.style.display='inline-block';}});
  btnInstall.addEventListener('click',async()=>{{if(!deferredPrompt)return;deferredPrompt.prompt();await deferredPrompt.userChoice;deferredPrompt=null;btnInstall.textContent='Installed?';}});
  if('serviceWorker'in navigator) navigator.serviceWorker.register('service-worker.js');

  const canvas=document.getElementById('gameCanvas');
  const ctx=canvas.getContext('2d');
  const badgesEl=document.getElementById('badges');
  const factCard=document.getElementById('factCard');
  const audioToggle=document.getElementById('audioToggle');

  // Base64 PDFs (embedded)
  const PDF_EMBED = {{
    square: 'data:application/pdf;base64,{{square_b64}}',
    portrait: 'data:application/pdf;base64,{{portrait_b64}}'
  }};
  function downloadDataUrl(filename, dataUrl){{
    const a=document.createElement('a'); a.href=dataUrl; a.download=filename; document.body.appendChild(a); a.click(); setTimeout(()=>a.remove(),0);
  }}
  const btnBooks=document.getElementById('btnBooks');
  const modalBooks=document.getElementById('modalBooks');
  const closeModalBooks=document.getElementById('closeModalBooks');
  const dlSquare=document.getElementById('dlSquare');
  const dlPortrait=document.getElementById('dlPortrait');
  const openSquare=document.getElementById('openSquare');
  const openPortrait=document.getElementById('openPortrait');
  btnBooks.addEventListener('click',()=>modalBooks.classList.remove('hidden'));
  closeModalBooks.addEventListener('click',()=>modalBooks.classList.add('hidden'));
  dlSquare.addEventListener('click',()=>downloadDataUrl('Spiders_Eight_Legs_of_Awesome_8p5x8p5.pdf', PDF_EMBED.square));
  dlPortrait.addEventListener('click',()=>downloadDataUrl('Spiders_Eight_Legs_of_Awesome_8x10.pdf', PDF_EMBED.portrait));
  function openInNewTab(dataUrl){{ const w=window.open(); if(!w){{alert('Popup blocked. Allow popups and retry.'); return;}} w.location=dataUrl; }}
  openSquare.addEventListener('click',()=>openInNewTab(PDF_EMBED.square));
  openPortrait.addEventListener('click',()=>openInNewTab(PDF_EMBED.portrait));

  const AudioFx=(()=>{{const ac=new (window.AudioContext||window.webkitAudioContext)(); function play(f=440,d=0.12,t='sine',v=0.2){{if(!audioToggle.checked)return;const o=ac.createOscillator(),g=ac.createGain();o.type=t;o.frequency.value=f;g.gain.value=v;o.connect(g).connect(ac.destination);o.start();o.stop(ac.currentTime+d);}} return {{success:()=>{{play(660,.1,'triangle',.25);setTimeout(()=>play(880,.1,'triangle',.22),100);}}, fail:()=>play(220,.18,'sawtooth',.18), click:()=>play(520,.05,'square',.12)}};}})();

  const Store={{
    k:'spiderQuestProgress_v2',
    load(){{
      try{{
        const raw=localStorage.getItem(this.k);
        return raw ? JSON.parse(raw) : {{time:0,quizzes:0,correct:0,bugScores:[],badges:[]}};
      }}catch{{
        return {{time:0,quizzes:0,correct:0,bugScores:[],badges:[]}};
      }}
    }},
    save(d){{ localStorage.setItem(this.k, JSON.stringify(d)); }}
  }};
  const Data=Store.load();
  const State={{mode:'garden',startTime:Date.now(),badges:new Set(Data.badges||[]),infoTips:["Spiders have two body parts!","Most spiders have 8 eyes.","Some spiders jump 50x their body length.","Spider silk comes from spinnerets.","Not all spiders make webs!"]}};
  function setTip(){{factCard.textContent="Tip: "+State.infoTips[Math.floor(Math.random()*State.infoTips.length)];}}
  function saveProgress(){{const now=Date.now(),elapsed=Math.floor((now-State.startTime)/1000);Data.time+=elapsed;Data.badges=Array.from(State.badges);Store.save(Data);State.startTime=now;}}
  function addBadge(name){{if(!State.badges.has(name)){{State.badges.add(name);Data.badges=Array.from(State.badges);Store.save(Data);AudioFx.success();}} badgesEl.textContent=Array.from(State.badges).join(' • ');}}

  // Dashboard
  const modal=document.getElementById('modal'); const btnDash=document.getElementById('btnDashboard'); const btnClose=document.getElementById('closeModal');
  const dashAudioToggle=document.getElementById('dashAudioToggle'); const dashReset=document.getElementById('dashReset');
  const progressList=document.getElementById('progressList'); const statTime=document.getElementById('statTime'); const statQuizzes=document.getElementById('statQuizzes'); const statCorrect=document.getElementById('statCorrect'); const statBugs=document.getElementById('statBugs');
  btnDash.addEventListener('click',()=>{{refreshDashboard(); modal.classList.remove('hidden');}});
  btnClose.addEventListener('click',()=>modal.classList.add('hidden'));
  dashAudioToggle.checked=audioToggle.checked; dashAudioToggle.addEventListener('change',()=>audioToggle.checked=dashAudioToggle.checked);
  dashReset.addEventListener('click',()=>{{if(!confirm('Reset all progress?'))return; Data.time=0;Data.quizzes=0;Data.correct=0;Data.bugScores=[];Data.badges=[];Store.save(Data);State.badges.clear();badgesEl.textContent='';AudioFx.fail();alert('Progress reset.');refreshDashboard();}});
  function refreshDashboard(){{progressList.innerHTML=''; Array.from(State.badges).forEach(b=>{{const li=document.createElement('li'); li.textContent='Badge: '+b; progressList.appendChild(li);}}); statTime.textContent=Math.floor(Data.time/60)+'m'; statQuizzes.textContent=Data.quizzes; statCorrect.textContent=Data.correct; statBugs.textContent=(Data.bugScores.slice(-5).join(', ')||'-');}}

  // Scenes
  function clear(){{ctx.clearRect(0,0,canvas.width,canvas.height);}}
  const WebBuilder=(()=>{{const anchors=[],connections=[]; let dragging=null,targetRings=3,completed=false;
    function init(){{anchors.length=0;connections.length=0;dragging=null;completed=false;targetRings=3;const cx=canvas.width/2,cy=canvas.height/2;for(let r=1;r<=5;r++){{const radius=50*r+40;for(let i=0;i<12;i++){{const ang=(Math.PI*2/12)*i;anchors.push({{x:cx+Math.cos(ang)*radius,y:cy+Math.sin(ang)*radius,hit:false}});}}}} draw(); setTip();}}
    function draw(){{clear(); ctx.fillStyle='#e6fffa'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#222'; ctx.font='24px sans-serif'; ctx.fillText('Web Builder: Drag to connect dots into rings!',20,30);
      anchors.forEach(a=>{{ctx.beginPath();ctx.arc(a.x,a.y,6,0,Math.PI*2);ctx.fillStyle=a.hit?'#00b894':'#0984e3';ctx.fill();}});
      ctx.strokeStyle='#6c5ce7'; ctx.lineWidth=3; connections.forEach(s=>{{ctx.beginPath();ctx.moveTo(s.x1,s.y1);ctx.lineTo(s.x2,s.y2);ctx.stroke();}});
      if(completed){{ctx.fillStyle='#2d3436'; ctx.font='28px sans-serif'; ctx.fillText('Great web! Badge earned: Web Master',20,canvas.height-30);}}}}
    function onDown(mx,my){{dragging=nearest(mx,my); if(dragging){{dragging.hit=true; AudioFx.click();}}}}
    function onMove(mx,my){{if(dragging){{draw(); ctx.strokeStyle='#636e72'; ctx.setLineDash([6,6]); ctx.beginPath(); ctx.moveTo(dragging.x,dragging.y); ctx.lineTo(mx,my); ctx.stroke(); ctx.setLineDash([]);}}}}
    function onUp(mx,my){{if(!dragging)return; const end=nearest(mx,my); if(end&&end!==dragging){{connections.push({{x1:dragging.x,y1:dragging.y,x2:end.x,y2:end.y}}); AudioFx.success();}} else {{AudioFx.fail();}} dragging.hit=false; dragging=null; if(connections.length>=targetRings*6&&!completed){{completed=true; addBadge('Web Master');}} draw();}}
    function nearest(mx,my){{let best=null,bd=9999; anchors.forEach(a=>{{const d=Math.hypot(a.x-mx,a.y-my); if(d<12&&d<bd){{bd=d;best=a;}}}}); return best;}}
    return {{init, onDown, onMove, onUp}};
  }})();
  const BugCatcher=(()=>{{const bugs=[]; let score=0,time=30,timer=null,over=false;
    function init(){{bugs.length=0;score=0;time=30;over=false;for(let i=0;i<10;i++)spawn(); if(timer)clearInterval(timer); timer=setInterval(()=>{{time--; if(time<=0){{over=true; clearInterval(timer); addBadge('Bug Buster'); Data.bugScores.push(score); Store.save(Data);}} draw();}},1000); setTip(); draw();}}
    function spawn(){{const good=Math.random()<0.7; bugs.push({{x:Math.random()*canvas.width,y:Math.random()*canvas.height,vx:(Math.random()*2-1)*3,vy:(Math.random()*2-1)*3,good}});}}
    function update(){{bugs.forEach(b=>{{b.x+=b.vx; b.y+=b.vy; if(b.x<0||b.x>canvas.width)b.vx*=-1; if(b.y<0||b.y>canvas.height)b.vy*=-1;}});}}
    function draw(){{clear(); ctx.fillStyle='#fff0f6'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#222'; ctx.font='24px sans-serif'; ctx.fillText('Bug Catcher: Click the prey. Avoid stingers!',20,30); ctx.fillText('Score: '+score,20,60); ctx.fillText('Time: '+time,140,60);
      bugs.forEach(b=>{{ctx.beginPath();ctx.arc(b.x,b.y,12,0,Math.PI*2);ctx.fillStyle=b.good?'#55efc4':'#fd79a8';ctx.fill();ctx.fillStyle='#222';ctx.beginPath();ctx.arc(b.x-4,b.y-2,2,0,Math.PI*2);ctx.fill();ctx.beginPath();ctx.arc(b.x+4,b.y-2,2,0,Math.PI*2);ctx.fill();}});
      if(!over) requestAnimationFrame(()=>{{update(); draw();}}); else {{ctx.fillStyle='#2d3436'; ctx.font='28px sans-serif'; ctx.fillText('Nice hunting! Badge earned: Bug Buster',20,canvas.height-30); AudioFx.success();}}}}
    function onClick(mx,my){{if(over)return; for(let i=bugs.length-1;i>=0;i--){{const b=bugs[i]; const d=Math.hypot(b.x-mx,b.y-my); if(d<14){{ if(b.good){{score+=5;AudioFx.success();}} else {{score-=3;AudioFx.fail();}} bugs.splice(i,1); spawn(); break;}}}}}}
    return {{init,onClick}};
  }})();
  const Quiz=(()=>{{const q=[{{t:'How many legs do spiders have?',a:['6','8','10'],i:1}},{{t:'Where does silk come from?',a:['Spinnerets','Antennae','Feet'],i:0}},{{t:'Do all spiders make webs?',a:['Yes','No'],i:1}}]; let idx=0,correct=0,done=false;
    function init(){{idx=0;correct=0;done=false;draw();setTip();}}
    function draw(){{clear(); ctx.fillStyle='#e3f2ff'; ctx.fillRect(0,0,canvas.width,canvas.height); ctx.fillStyle='#222'; ctx.font='26px sans-serif'; ctx.fillText('Fact Frenzy Quiz!',20,40);
      if(done){{ctx.fillText(`Score: ${{correct}}/${{q.length}}`,20,80); ctx.fillText('Badge earned: Silk Genius',20,120); return;}}
      const item=q[idx]; wrapText(item.t,20,90,860,30); item.a.forEach((opt,i)=>drawBtn(40,160+i*70,820,50,`${{String.fromCharCode(65+i)}}. ${{opt}}`,i));}}
    function wrapText(text,x,y,maxW,lh){{const words=text.split(' '); let line='',cy=y; for(const w of words){{const t=(line+' '+w).trim(); if(ctx.measureText(t).width<=maxW) line=t; else {{ctx.fillText(line,x,cy); cy+=lh; line=w;}}}} if(line) ctx.fillText(line,x,cy);}}
    const buttons=[{{}},{{}},{{}}];
    function drawBtn(x,y,w,h,label,i){{ctx.fillStyle='#ffd6a5'; ctx.fillRect(x,y,w,h); ctx.strokeStyle='#f08'; ctx.lineWidth=3; ctx.strokeRect(x,y,w,h); ctx.fillStyle='#222'; ctx.font='22px sans-serif'; ctx.fillText(label,x+12,y+32); if(!buttons[i]) buttons[i]={{x,y,w,h}}; else Object.assign(buttons[i],{{x,y,w,h}});}}
    function onClick(mx,my){{if(done) return; const item=q[idx]; for(let i=0;i<item.a.length;i++){{const b=buttons[i]; if(!b) continue; if(mx>=b.x&&mx<=b.x+b.w&&my>=b.y&&my<=b.y+b.h){{ if(i===item.i){{correct++;AudioFx.success();}} else {{AudioFx.fail();}} idx++; if(idx>=q.length){{done=true; addBadge('Silk Genius'); Data.quizzes++; Data.correct+=correct; Store.save(Data);}} draw(); break; }}}}}
    return {{init,onClick}};
  }})();

  const btnGarden=document.getElementById('btnGarden'); const btnBackyard=document.getElementById('btnBackyard'); const btnQuiz=document.getElementById('btnQuiz'); const btnReset=document.getElementById('btnReset');
  let current=null; function setMode(m){{saveProgress(); if(m==='garden') current=WebBuilder; if(m==='backyard') current=BugCatcher; if(m==='quiz') current=Quiz; current.init();}}
  btnGarden.addEventListener('click',()=>setMode('garden')); btnBackyard.addEventListener('click',()=>setMode('backyard')); btnQuiz.addEventListener('click',()=>setMode('quiz'));
  btnReset.addEventListener('click',()=>{{Data.time=0;Data.quizzes=0;Data.correct=0;Data.bugScores=[];Data.badges=[];Store.save(Data); State.badges.clear(); badgesEl.textContent=''; factCard.textContent='Ready!'; AudioFx.fail(); setMode('garden');}});
  canvas.addEventListener('mousedown',(e)=>{{const r=canvas.getBoundingClientRect(); const mx=e.clientX-r.left,my=e.clientY-r.top; if(!current)return; if(current.onDown) current.onDown(mx,my); if(current.onClick) current.onClick(mx,my);}});
  canvas.addEventListener('mousemove',(e)=>{{const r=canvas.getBoundingClientRect(); const mx=e.clientX-r.left,my=e.clientY-r.top; if(!current||!current.onMove)return; current.onMove(mx,my);}});
  window.addEventListener('mouseup',(e)=>{{const r=canvas.getBoundingClientRect(); const mx=e.clientX-r.left,my=e.clientY-r.top; if(!current||!current.onUp)return; current.onUp(mx,my);}});
  // start
  setMode('garden');
}})();
"""
# Inject base64s into script without using f-strings
SCRIPT = SCRIPT.replace('{{square_b64}}', square_b64).replace('{{portrait_b64}}', portrait_b64)

MANIFEST = {
  "name": "Spider Quest",
  "short_name": "SpiderQuest",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#fff7e6",
  "theme_color": "#ffd166",
  "icons": [
    {"src":"icon-192.png","sizes":"192x192","type":"image/png"},
    {"src":"icon-512.png","sizes":"512x512","type":"image/png"}
  ]
}
SW = """const CACHE_NAME='spider-quest-v2';
const ASSETS=['./','./index.html','./style.css','./script.js','./manifest.json','./icon-192.png','./icon-512.png','./books/Spiders_Eight_Legs_of_Awesome_8p5x8p5.pdf','./books/Spiders_Eight_Legs_of_Awesome_8x10.pdf'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE_NAME).then(c=>c.addAll(ASSETS)))});
self.addEventListener('activate',e=>{e.waitUntil(self.clients.claim())});
self.addEventListener('fetch',e=>{e.respondWith(caches.match(e.request).then(r=>r||fetch(e.request)))}});
"""


# write files
open("index.html","w").write(INDEX)
open("style.css","w").write(STYLE)
open("script.js","w").write(SCRIPT)
open("manifest.json","w").write(json.dumps(MANIFEST, indent=2))
open("service-worker.js","w").write(SW)

# quick icons
from PIL import Image
for s in [192,512]:
    img = Image.new("RGBA", (s,s), (255,255,255,0))
    d = ImageDraw.Draw(img)
    d.ellipse((0,0,s-1,s-1), fill=(255,230,120,255))
    cx, cy = s//2, s//2 + int(s*0.05); r = int(s*0.22)
    d.ellipse((cx-r,cy-r,cx+r,cy+r), fill=(60,60,60,255))
    eye = max(2, s//18)
    d.ellipse((cx-r//2-eye, cy-eye, cx-r//2+eye, cy+eye), fill=(255,255,255,255))
    d.ellipse((cx+r//2-eye, cy-eye, cx+r//2+eye, cy+eye), fill=(255,255,255,255))
    d.line((cx-r,cy, cx-r-int(s*0.28), cy-int(s*0.14)), fill=(60,60,60,255), width=max(1,s//32))
    d.line((cx+r,cy, cx+r+int(s*0.28), cy-int(s*0.14)), fill=(60,60,60,255), width=max(1,s//32))
    img.save(f"icon-{s}.png")

print("Build complete. Open index.html via a local server (python3 -m http.server) and test.")

