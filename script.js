(() => {
  console.log("Spider Quest booting…");

  // PWA install + SW
  let deferredPrompt = null;
  const btnInstall = document.getElementById('btnInstall');

  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    btnInstall.style.display = 'inline-block';
  });

  btnInstall?.addEventListener('click', async () => {
    try {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      await deferredPrompt.userChoice;
      deferredPrompt = null;
      btnInstall.textContent = 'Installed?';
    } catch (err) {
      console.warn('Install prompt error:', err);
    }
  });

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('service-worker.js')
      .then(() => console.log('Service worker registered.'))
      .catch(err => console.warn('SW register failed:', err));
  }

  const canvas = document.getElementById('gameCanvas');
  const ctx = canvas.getContext('2d');
  const badgesEl = document.getElementById('badges');
  const factCard = document.getElementById('factCard');
  const audioToggle = document.getElementById('audioToggle');

  // ===== Books (plain file links) =====
  const BOOK_SQUARE = './books/Spiders_Eight_Legs_of_Awesome_8p5x8p5.pdf';
  const BOOK_PORTRAIT = './books/Spiders_Eight_Legs_of_Awesome_8x10.pdf';

  const btnBooks = document.getElementById('btnBooks');
  const modalBooks = document.getElementById('modalBooks');
  const closeModalBooks = document.getElementById('closeModalBooks');
  const dlSquare = document.getElementById('dlSquare');
  const dlPortrait = document.getElementById('dlPortrait');
  const openSquare = document.getElementById('openSquare');
  const openPortrait = document.getElementById('openPortrait');

  btnBooks.addEventListener('click', () => modalBooks.classList.remove('hidden'));
  closeModalBooks.addEventListener('click', () => modalBooks.classList.add('hidden'));

  function downloadFile(href, filename) {
    const a = document.createElement('a');
    a.href = href;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
  }
  function openFileNewTab(href) { window.open(href, '_blank'); }

  dlSquare.addEventListener('click', () => downloadFile(BOOK_SQUARE, 'Spiders_Eight_Legs_of_Awesome_8p5x8p5.pdf'));
  dlPortrait.addEventListener('click', () => downloadFile(BOOK_PORTRAIT, 'Spiders_Eight_Legs_of_Awesome_8x10.pdf'));
  openSquare.addEventListener('click', () => openFileNewTab(BOOK_SQUARE));
  openPortrait.addEventListener('click', () => openFileNewTab(BOOK_PORTRAIT));

  // ===== Audio =====
  const AudioFx = (() => {
    const ac = new (window.AudioContext || window.webkitAudioContext)();
    function play(freq = 440, duration = 0.12, type = 'sine', volume = 0.2) {
      if (!audioToggle.checked) return;
      const o = ac.createOscillator();
      const g = ac.createGain();
      o.type = type; o.frequency.value = freq;
      g.gain.value = volume;
      o.connect(g).connect(ac.destination);
      o.start();
      o.stop(ac.currentTime + duration);
    }
    return {
      success: () => { play(660, 0.1, 'triangle', 0.25); setTimeout(() => play(880, 0.1, 'triangle', 0.22), 100); },
      fail: () => play(220, 0.18, 'sawtooth', 0.18),
      click: () => play(520, 0.05, 'square', 0.12)
    };
  })();

  // ===== Store / State =====
  const Store = {
    k: 'spiderQuestProgress_v2',
    load() {
      try {
        return JSON.parse(localStorage.getItem(this.k)) || { time: 0, quizzes: 0, correct: 0, bugScores: [], badges: [] };
      } catch { return { time: 0, quizzes: 0, correct: 0, bugScores: [], badges: [] }; }
    },
    save(d) { localStorage.setItem(this.k, JSON.stringify(d)); }
  };
  const Data = Store.load();
  const State = {
    mode: 'garden',
    startTime: Date.now(),
    badges: new Set(Data.badges || []),
    infoTips: [
      "Spiders have two body parts!",
      "Most spiders have 8 eyes.",
      "Some spiders jump 50x their body length.",
      "Spider silk comes from spinnerets.",
      "Not all spiders make webs!"
    ]
  };

  function setTip() {
    const tip = State.infoTips[Math.floor(Math.random() * State.infoTips.length)];
    factCard.textContent = "Tip: " + tip;
  }
  function saveProgress() {
    const now = Date.now();
    const elapsed = Math.floor((now - State.startTime) / 1000);
    Data.time += elapsed;
    Data.badges = Array.from(State.badges);
    Store.save(Data);
    State.startTime = now;
  }
  function addBadge(name) {
    if (!State.badges.has(name)) {
      State.badges.add(name);
      Data.badges = Array.from(State.badges);
      Store.save(Data);
      AudioFx.success();
    }
    badgesEl.textContent = Array.from(State.badges).join(' • ');
  }

  // ===== Dashboard =====
  const modal = document.getElementById('modal');
  const btnDash = document.getElementById('btnDashboard');
  const btnClose = document.getElementById('closeModal');
  const dashAudioToggle = document.getElementById('dashAudioToggle');
  const dashReset = document.getElementById('dashReset');
  const progressList = document.getElementById('progressList');
  const statTime = document.getElementById('statTime');
  const statQuizzes = document.getElementById('statQuizzes');
  const statCorrect = document.getElementById('statCorrect');
  const statBugs = document.getElementById('statBugs');

  btnDash.addEventListener('click', () => { refreshDashboard(); modal.classList.remove('hidden'); });
  btnClose.addEventListener('click', () => modal.classList.add('hidden'));
  dashAudioToggle.checked = audioToggle.checked;
  dashAudioToggle.addEventListener('change', () => audioToggle.checked = dashAudioToggle.checked);
  dashReset.addEventListener('click', () => {
    if (!confirm('Reset all progress?')) return;
    Data.time = 0; Data.quizzes = 0; Data.correct = 0; Data.bugScores = []; Data.badges = [];
    Store.save(Data);
    State.badges.clear(); badgesEl.textContent = '';
    AudioFx.fail();
    alert('Progress reset.');
    refreshDashboard();
  });

  function refreshDashboard() {
    progressList.innerHTML = '';
    Array.from(State.badges).forEach(b => {
      const li = document.createElement('li'); li.textContent = 'Badge: ' + b;
      progressList.appendChild(li);
    });
    const mins = Math.floor(Data.time / 60);
    statTime.textContent = mins + 'm';
    statQuizzes.textContent = Data.quizzes;
    statCorrect.textContent = Data.correct;
    statBugs.textContent = (Data.bugScores.slice(-5).join(', ') || '-');
  }

  // ===== Scenes =====
  function clear() { ctx.clearRect(0, 0, canvas.width, canvas.height); }

  // Web Builder
  const WebBuilder = (() => {
    const anchors = [];
    const connections = [];
    let dragging = null;
    let targetRings = 3;
    let completed = false;

    function init() {
      anchors.length = 0; connections.length = 0; dragging = null; completed = false; targetRings = 3;
      const cx = canvas.width / 2, cy = canvas.height / 2;
      const rings = 5;
      for (let r = 1; r <= rings; r++) {
        const radius = 50 * r + 40;
        for (let i = 0; i < 12; i++) {
          const ang = (Math.PI * 2 / 12) * i;
          anchors.push({ x: cx + Math.cos(ang) * radius, y: cy + Math.sin(ang) * radius, hit: false });
        }
      }
      draw(); setTip();
    }

    function draw() {
      clear();
      ctx.fillStyle = '#e6fffa';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#222';
      ctx.font = '24px sans-serif';
      ctx.fillText('Web Builder: Drag to connect dots into rings!', 20, 30);

      anchors.forEach(a => {
        ctx.beginPath();
        ctx.arc(a.x, a.y, 6, 0, Math.PI * 2);
        ctx.fillStyle = a.hit ? '#00b894' : '#0984e3';
        ctx.fill();
      });

      ctx.strokeStyle = '#6c5ce7';
      ctx.lineWidth = 3;
      connections.forEach(seg => {
        ctx.beginPath();
        ctx.moveTo(seg.x1, seg.y1);
        ctx.lineTo(seg.x2, seg.y2);
        ctx.stroke();
      });

      if (completed) {
        ctx.fillStyle = '#2d3436';
        ctx.font = '28px sans-serif';
        ctx.fillText('Great web! Badge earned: Web Master', 20, canvas.height - 30);
      }
    }

    function onDown(mx, my) {
      dragging = nearestAnchor(mx, my);
      if (dragging) { dragging.hit = true; AudioFx.click(); }
    }
    function onMove(mx, my) {
      if (dragging) {
        draw();
        ctx.strokeStyle = '#636e72';
        ctx.setLineDash([6, 6]);
        ctx.beginPath();
        ctx.moveTo(dragging.x, dragging.y);
        ctx.lineTo(mx, my);
        ctx.stroke();
        ctx.setLineDash([]);
      }
    }
    function onUp(mx, my) {
      if (!dragging) return;
      const end = nearestAnchor(mx, my);
      if (end && end !== dragging) {
        connections.push({ x1: dragging.x, y1: dragging.y, x2: end.x, y2: end.y });
        AudioFx.success();
      } else {
        AudioFx.fail();
      }
      dragging.hit = false;
      dragging = null;
      if (connections.length >= targetRings * 6 && !completed) {
        completed = true;
        addBadge('Web Master');
      }
      draw();
    }

    function nearestAnchor(mx, my) {
      let best = null, bd = 9999;
      anchors.forEach(a => {
        const d = Math.hypot(a.x - mx, a.y - my);
        if (d < 12 && d < bd) { bd = d; best = a; }
      });
      return best;
    }

    return { init, draw, onDown, onMove, onUp };
  })();

  // Bug Catcher
  const BugCatcher = (() => {
    const bugs = [];
    let score = 0, time = 30, timerId = null, over = false;

    function init() {
      bugs.length = 0; score = 0; time = 30; over = false;
      for (let i = 0; i < 10; i++) spawnBug();
      if (timerId) clearInterval(timerId);
      timerId = setInterval(() => {
        time--;
        if (time <= 0) {
          over = true; clearInterval(timerId); addBadge('Bug Buster');
          Data.bugScores.push(score); Store.save(Data);
        }
        draw();
      }, 1000);
      setTip();
      draw();
    }

    function spawnBug() {
      const good = Math.random() < 0.7; // 70% edible
      const bug = {
        x: Math.random() * canvas.width, y: Math.random() * canvas.height,
        vx: (Math.random() * 2 - 1) * 3, vy: (Math.random() * 2 - 1) * 3, good
      };
      bugs.push(bug);
    }

    function update() {
      bugs.forEach(b => {
        b.x += b.vx; b.y += b.vy;
        if (b.x < 0 || b.x > canvas.width) b.vx *= -1;
        if (b.y < 0 || b.y > canvas.height) b.vy *= -1;
      });
    }

    function draw() {
      clear();
      ctx.fillStyle = '#fff0f6';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#222';
      ctx.font = '24px sans-serif';
      ctx.fillText('Bug Catcher: Click the prey. Avoid stingers!', 20, 30);
      ctx.fillText('Score: ' + score, 20, 60);
      ctx.fillText('Time: ' + time, 140, 60);

      bugs.forEach(b => {
        ctx.beginPath();
        ctx.arc(b.x, b.y, 12, 0, Math.PI * 2);
        ctx.fillStyle = b.good ? '#55efc4' : '#fd79a8';
        ctx.fill();
        ctx.fillStyle = '#222';
        ctx.beginPath(); ctx.arc(b.x - 4, b.y - 2, 2, 0, Math.PI * 2); ctx.fill();
        ctx.beginPath(); ctx.arc(b.x + 4, b.y - 2, 2, 0, Math.PI * 2); ctx.fill();
      });

      if (!over) requestAnimationFrame(() => { update(); draw(); });
      else {
        ctx.fillStyle = '#2d3436';
        ctx.font = '28px sans-serif';
        ctx.fillText('Nice hunting! Badge earned: Bug Buster', 20, canvas.height - 30);
        AudioFx.success();
      }
    }

    function onClick(mx, my) {
      if (over) return;
      for (let i = bugs.length - 1; i >= 0; i--) {
        const b = bugs[i];
        const d = Math.hypot(b.x - mx, b.y - my);
        if (d < 14) {
          if (b.good) { score += 5; AudioFx.success(); }
          else { score -= 3; AudioFx.fail(); }
          bugs.splice(i, 1);
          spawnBug();
          break;
        }
      }
    }

    return { init, onClick };
  })();

  // Quiz
  const Quiz = (() => {
    const q = [
      { t: 'How many legs do spiders have?', a: ['6', '8', '10'], i: 1 },
      { t: 'Where does silk come from?', a: ['Spinnerets', 'Antennae', 'Feet'], i: 0 },
      { t: 'Do all spiders make webs?', a: ['Yes', 'No'], i: 1 }
    ];
    let idx = 0, correct = 0, done = false;

    function init() { idx = 0; correct = 0; done = false; draw(); setTip(); }

    function draw() {
      clear();
      ctx.fillStyle = '#e3f2ff';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = '#222';
      ctx.font = '26px sans-serif';
      ctx.fillText('Fact Frenzy Quiz!', 20, 40);

      if (done) {
        ctx.fillText(`Score: ${correct}/${q.length}`, 20, 80);
        ctx.fillText('Badge earned: Silk Genius', 20, 120);
        return;
      }

      const item = q[idx];
      wrapText(item.t, 20, 90, 860, 30);
      item.a.forEach((opt, i) => {
        drawButton(40, 160 + i * 70, 820, 50, `${String.fromCharCode(65 + i)}. ${opt}`, i);
      });
    }

    function wrapText(text, x, y, maxW, lh) {
      const words = text.split(' ');
      let line = ''; let cy = y;
      for (const w of words) {
        const t = (line + ' ' + w).trim();
        if (ctx.measureText(t).width <= maxW) line = t;
        else { ctx.fillText(line, x, cy); cy += lh; line = w; }
      }
      if (line) ctx.fillText(line, x, cy);
    }

    const buttons = [{}, {}, {}];
    function drawButton(x, y, w, h, label, i) {
      ctx.fillStyle = '#ffd6a5';
      ctx.fillRect(x, y, w, h);
      ctx.strokeStyle = '#f08'; ctx.lineWidth = 3; ctx.strokeRect(x, y, w, h);
      ctx.fillStyle = '#222'; ctx.font = '22px sans-serif';
      ctx.fillText(label, x + 12, y + 32);
      if (!buttons[i]) buttons[i] = { x, y, w, h };
      else Object.assign(buttons[i], { x, y, w, h });
    }

    function onClick(mx, my) {
      if (done) return;
      const item = q[idx];
      for (let i = 0; i < item.a.length; i++) {
        const b = buttons[i];
        if (!b) continue;
        if (mx >= b.x && mx <= b.x + b.w && my >= b.y && my <= b.y + b.h) {
          if (i === item.i) { correct++; AudioFx.success(); }
          else { AudioFx.fail(); }
          idx++;
          if (idx >= q.length) { done = true; addBadge('Silk Genius'); Data.quizzes++; Data.correct += correct; Store.save(Data); }
          draw();
          break;
        }
      }
    }

    return { init, onClick };
  })();

  // Routing
  const btnGarden = document.getElementById('btnGarden');
  const btnBackyard = document.getElementById('btnBackyard');
  const btnQuiz = document.getElementById('btnQuiz');
  const btnReset = document.getElementById('btnReset');

  let current = null;
  function setMode(mode) {
    saveProgress();
    if (mode === 'garden') { current = WebBuilder; current.init(); }
    if (mode === 'backyard') { current = BugCatcher; current.init(); }
    if (mode === 'quiz') { current = Quiz; current.init(); }
  }

  btnGarden.addEventListener('click', () => setMode('garden'));
  btnBackyard.addEventListener('click', () => setMode('backyard'));
  btnQuiz.addEventListener('click', () => setMode('quiz'));
  btnReset.addEventListener('click', () => {
    Data.time = 0; Data.quizzes = 0; Data.correct = 0; Data.bugScores = []; Data.badges = [];
    Store.save(Data); State.badges.clear(); badgesEl.textContent = ''; factCard.textContent = 'Ready!';
    AudioFx.fail(); setMode('garden');
  });

  // Canvas input
  canvas.addEventListener('mousedown', (e) => {
    const r = canvas.getBoundingClientRect(); const mx = e.clientX - r.left, my = e.clientY - r.top;
    if (!current) return;
    if (current.onDown) current.onDown(mx, my);
    if (current.onClick) current.onClick(mx, my);
  });
  canvas.addEventListener('mousemove', (e) => {
    const r = canvas.getBoundingClientRect(); const mx = e.clientX - r.left, my = e.clientY - r.top;
    if (!current || !current.onMove) return;
    current.onMove(mx, my);
  });
  window.addEventListener('mouseup', (e) => {
    const r = canvas.getBoundingClientRect(); const mx = e.clientX - r.left, my = e.clientY - r.top;
    if (!current || !current.onUp) return;
    current.onUp(mx, my);
  });

  // Start
  setMode('garden');
})();
