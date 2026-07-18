
// Load Three.js dynamically
var s = document.createElement('script');
s.src = 'cad/three.min.js';
s.onload = function() { initScene(); };
document.head.appendChild(s);

var scene, cam, ren, meshes = [], origPos = [], loaded = 0;
var DAYS = ['MON','TUE','WED','THU','FRI','SAT','SUN'];
var DA = (2*Math.PI)/7;
var orb = {t:Math.PI/4, p:Math.PI/7}, rad = 230, pan = {x:0, y:30, z:0};
var exploded = false, wireOn = false, explodeT = 0;
var currentDay = 0, animating = false, isPlaying = false;
var dispensedPills = [];
var autoTimer = null, timelineProgress = 0, currentStepIndex = 0;

var PARTS = [
  {f:'cad/stl_models/01_base_plate.stl',     n:'Base Plate',  c:0x475569, ex:[0,-25,0]},
  {f:'cad/stl_models/02_housing_shell.stl',   n:'Housing',     c:0x90a4ae, ex:[0,0,0], tr:true},
  {f:'cad/stl_models/03_carousel_wheel.stl',  n:'Carousel',    c:0xcfd8dc, ex:[0,12,0]},
  {f:'cad/stl_models/04_ratchet_wheel.stl',   n:'Ratchet',     c:0xfbbf24, ex:[0,35,0]},
  {f:'cad/stl_models/05_pawl_arm.stl',        n:'Pawl',        c:0xf59e0b, ex:[-45,35,0]},
  {f:'cad/stl_models/06_plunger_shaft.stl',   n:'Plunger',     c:0x7dd3fc, ex:[0,50,0]},
  {f:'cad/stl_models/07_return_spring.stl',   n:'Spring',      c:0xf87171, ex:[30,50,0]},
  {f:'cad/stl_models/08_palm_button.stl',     n:'Button',      c:0x38bdf8, ex:[0,72,0]},
  {f:'cad/stl_models/09_dispenser_cup.stl',   n:'Cup',         c:0x0891b2, ex:[70,-12,0]}, // cyan clinical match
  {f:'cad/stl_models/10_central_axle.stl',    n:'Axle',        c:0x64748b, ex:[0,0,0]},
  {f:'cad/stl_models/11_pills.stl',           n:'Pills',       c:0xfbbf24, ex:[0,12,0]}
];

// ===== Text-to-Speech Engine (Indian Female Voice) =====
function speak(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  var u = new SpeechSynthesisUtterance(text);
  u.rate = 0.88;
  u.pitch = 1.1;
  u.volume = 1.0;
  var voices = window.speechSynthesis.getVoices();
  var sel = null;
  // Priority 1: en-IN female voice
  for (var i = 0; i < voices.length; i++) {
    var lang = voices[i].lang.replace('_','-').toLowerCase();
    if (lang === 'en-in' || lang.indexOf('en-in') === 0) { sel = voices[i]; break; }
  }
  // Priority 2: any English female voice
  if (!sel) {
    for (var i = 0; i < voices.length; i++) {
      var lang = voices[i].lang.replace('_','-').toLowerCase();
      var nm = voices[i].name.toLowerCase();
      if (lang.indexOf('en') === 0 && (nm.indexOf('zira') >= 0 || nm.indexOf('hazel') >= 0 || nm.indexOf('female') >= 0)) {
        sel = voices[i]; break;
      }
    }
  }
  if (sel) u.voice = sel;
  window.speechSynthesis.speak(u);
}
if (window.speechSynthesis) {
  window.speechSynthesis.getVoices();
  window.speechSynthesis.onvoiceschanged = function() { window.speechSynthesis.getVoices(); };
}

// Presentation Schedule (Total ~150s / 2.5 Minutes)
var steps = [
  { d: 18000, s: 0, t: '1. Device Introduction',
    voice: null, // Custom audio file plays for this step
    act: function(){ resetAll(); } },

  { d: 18000, s: 1, t: '2. Struggle with Traditional Methods',
    voice: 'Now let us understand the problem. Elderly patients with arthritis, joint pain, or stroke survivors cannot open child-proof caps or align small lids. These tasks demand two active hands and fine finger dexterity, which these patients simply do not have.',
    act: function(){ } },

  { d: 18000, s: 2, t: '3. Rotadex Solution',
    voice: 'Our solution is the Rotadex. It converts fine motor finger movements into a single effortless downward palm press. The device stays stable on the table with its weighted base and non-slip feet. No pinching, no twisting, just one simple push.',
    act: function(){ } },

  { d: 15000, s: 3, t: '4. First Dispense — Monday',
    voice: 'Watch the dispensing simulation. The user presses the blue dome with their palm. The plunger pushes the pawl into the ratchet wheel, rotating the carousel by 51.4 degrees. Mondays pills slide into the green scoop cup.',
    act: function(){ doDispense(); } },

  { d: 12000, s: 3, t: '5. Second Dispense — Tuesday',
    voice: 'Pressing again advances the carousel to Tuesday. The return spring automatically resets the button after each press. The user needs zero finger dexterity.',
    act: function(){ doDispense(); } },

  { d: 15000, s: 4, t: '6. Exploded View',
    voice: 'Now we explode the assembly to see all 11 internal components. You can see the yellow ratchet wheel, the orange pawl arm, the red helical return spring, and the blue plunger shaft. The scoop cup is shown in cyan.',
    act: function(){ exploded = true; } },

  { d: 12000, s: 4, t: '7. Wireframe Mesh',
    voice: 'Switching to wireframe mode. The total mesh contains 8,664 triangles. The spring alone has 1,920 triangles modeled as a true helical coil geometry.',
    act: function(){ toggleWire(); } },

  { d: 15000, s: 5, t: '8. Features & Conclusion',
    voice: 'Restoring the solid view. In conclusion, the Rotadex is fully mechanical, requires no batteries, and is ready for manufacturing. Key features include one-handed operation, anti-reverse safety, gravity-fed dispensing, and automatic spring reset. Thank you very much.',
    act: function(){ toggleWire(); exploded = false; } }
];

function parseSTL(text) {
  var v = [], nm = [], cn = null, tv = [];
  var lines = text.split('\n');
  for (var i = 0; i < lines.length; i++) {
    var t = lines[i].trim();
    if (t.indexOf('facet normal') === 0) {
      var p = t.split(/\s+/);
      cn = [parseFloat(p[2]), parseFloat(p[3]), parseFloat(p[4])];
    } else if (t.indexOf('vertex') === 0) {
      var p = t.split(/\s+/);
      tv.push(parseFloat(p[1]), parseFloat(p[2]), parseFloat(p[3]));
      if (tv.length === 9) { v.push.apply(v, tv); nm.push.apply(nm, cn.concat(cn, cn)); tv = []; }
    }
  }
  var g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.Float32BufferAttribute(v, 3));
  g.setAttribute('normal', new THREE.Float32BufferAttribute(nm, 3));
  return g;
}

function camUp() {
  cam.position.x = pan.x + rad * Math.cos(orb.p) * Math.cos(orb.t);
  cam.position.y = pan.y + rad * Math.sin(orb.p);
  cam.position.z = pan.z + rad * Math.cos(orb.p) * Math.sin(orb.t);
  cam.lookAt(pan.x, pan.y, pan.z);
}

function initScene() {
  var container = document.getElementById('canvas-container');
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0f172a); // dark premium clinical slate

  cam = new THREE.PerspectiveCamera(38, container.clientWidth / container.clientHeight, 0.1, 2000);

  ren = new THREE.WebGLRenderer({antialias: true});
  ren.setSize(container.clientWidth, container.clientHeight);
  ren.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  ren.shadowMap.enabled = true;
  ren.toneMapping = THREE.ACESFilmicToneMapping;
  container.appendChild(ren.domElement);

  // Lights
  scene.add(new THREE.AmbientLight(0x94a3b8, 0.6));
  var kl = new THREE.DirectionalLight(0xffffff, 0.95);
  kl.position.set(80, 180, 120);
  kl.castShadow = true;
  scene.add(kl);
  var fl = new THREE.DirectionalLight(0x0891b2, 0.35); // Cyan accents
  fl.position.set(-80, 40, -80);
  scene.add(fl);

  // Ground grid
  var gnd = new THREE.Mesh(
    new THREE.PlaneGeometry(500, 500),
    new THREE.MeshStandardMaterial({color: 0x0f172a, roughness: 0.95})
  );
  gnd.rotation.x = -Math.PI / 2;
  gnd.position.y = -8;
  gnd.receiveShadow = true;
  scene.add(gnd);

  var grid = new THREE.GridHelper(300, 30, 0x1e293b, 0x1e293b);
  grid.position.y = -7;
  scene.add(grid);

  // Day labels around the wheel
  for (var i = 0; i < DAYS.length; i++) {
    var c = document.createElement('canvas');
    c.width = 128; c.height = 64;
    var ctx = c.getContext('2d');
    ctx.font = 'bold 28px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#0891b2';
    ctx.fillText(DAYS[i], 64, 32);
    var tex = new THREE.CanvasTexture(c);
    var sp = new THREE.Sprite(new THREE.SpriteMaterial({map: tex, transparent: true, depthTest: false}));
    var angle = i * DA + DA / 2;
    sp.position.set(72 * Math.cos(angle), 30, 72 * Math.sin(angle));
    sp.scale.set(18, 9, 1);
    scene.add(sp);
  }

  camUp();
  loadParts();
  setupOrbitControls();
  animate();
}

function loadParts() {
  for (var i = 0; i < PARTS.length; i++) {
    (function(idx) {
      var xhr = new XMLHttpRequest();
      xhr.open('GET', PARTS[idx].f, true);
      xhr.onload = function() {
        if (xhr.status === 200) {
          var geo = parseSTL(xhr.responseText);
          var p = PARTS[idx];
          var mat = new THREE.MeshPhysicalMaterial({
            color: p.c,
            emissive: p.c,
            emissiveIntensity: 0.05,
            roughness: 0.28,
            metalness: 0.15,
            clearcoat: 0.4,
            transparent: !!p.tr,
            opacity: p.tr ? 0.3 : 1,
            side: THREE.DoubleSide
          });
          var mesh = new THREE.Mesh(geo, mat);
          mesh.castShadow = true;
          mesh.receiveShadow = true;
          scene.add(mesh);
          meshes[idx] = mesh;
          origPos[idx] = mesh.position.clone();
          loaded++;
          if (loaded === PARTS.length) {
            document.getElementById('loading-txt').style.display = 'none';
            document.getElementById('start-btn').style.display = 'block';
          }
        }
      };
      xhr.send();
    })(i);
  }
}

function setupOrbitControls() {
  var cv = ren.domElement;
  var drag = false, prev = {x:0, y:0};
  cv.addEventListener('mousedown', function(e) {
    drag = true;
    prev = {x: e.clientX, y: e.clientY};
  });
  cv.addEventListener('mousemove', function(e) {
    if (!drag) return;
    var dx = e.clientX - prev.x, dy = e.clientY - prev.y;
    orb.t -= dx * 0.005;
    orb.p = Math.max(-1, Math.min(1.3, orb.p + dy * 0.005));
    camUp();
    prev = {x: e.clientX, y: e.clientY};
  });
  cv.addEventListener('mouseup', function() { drag = false; });
  cv.addEventListener('mouseleave', function() { drag = false; });
}

function animate() {
  requestAnimationFrame(animate);
  if (isPlaying && !exploded) {
    orb.t += 0.002;
    camUp();
  }
  var et = exploded ? 1 : 0;
  explodeT += (et - explodeT) * 0.05;
  for (var i = 0; i < meshes.length; i++) {
    if (!meshes[i] || !origPos[i]) continue;
    var ex = PARTS[i].ex;
    meshes[i].position.x = origPos[i].x + ex[0] * explodeT;
    meshes[i].position.y = origPos[i].y + ex[1] * explodeT;
    meshes[i].position.z = origPos[i].z + ex[2] * explodeT;
  }
  ren.render(scene, cam);
}

// Dispense logic
function doDispense() {
  if (animating) return;
  animating = true;
  var btn = meshes[7], car = meshes[2], pills = meshes[10];
  var btnY = origPos[7] ? origPos[7].y : 0;

  var activePill = new THREE.Mesh(
    new THREE.SphereGeometry(3.5, 16, 16),
    new THREE.MeshStandardMaterial({
      color: 0xfbbf24,
      roughness: 0.35,
      metalness: 0.1,
      emissive: 0x92400e,
      emissiveIntensity: 0.05
    })
  );
  activePill.castShadow = true;
  activePill.receiveShadow = true;
  activePill.position.set(45, 0, 20);
  scene.add(activePill);
  dispensedPills.push(activePill);

  var phase = 0, t = 0;
  function step() {
    t += 0.025;
    if (phase === 0) {
      if (btn) btn.position.y = btnY - Math.sin(Math.min(t, 1) * Math.PI) * 6;
      if (t >= 1) { phase = 1; t = 0; }
    } else if (phase === 1) {
      if (car) car.rotation.y += DA * 0.03;
      if (pills) pills.rotation.y += DA * 0.03;
      
      var slideT = Math.min(t, 1);
      activePill.position.x = 45 + slideT * 30;
      activePill.position.y = -Math.sin(slideT * Math.PI) * 3;
      activePill.position.z = 20 - slideT * 9;
      
      if (t >= 1) {
        phase = 2; t = 0;
        currentDay = (currentDay + 1) % 7;
        document.getElementById('dayLbl').textContent = DAYS[currentDay];
      }
    } else if (phase === 2) {
      if (btn) btn.position.y = btnY - Math.sin(Math.max(0, (1 - t)) * Math.PI) * 2;
      if (t >= 0.5) {
        animating = false;
        if (btn) btn.position.y = btnY;
        return;
      }
    }
    requestAnimationFrame(step);
  }
  step();
}

function beginPresentation() {
  document.getElementById('start-overlay').style.display = 'none';
  isPlaying = true;
  document.getElementById('play-btn').disabled = false;
  
  // Play custom voice audio file
  var audio = document.getElementById('voiceAudio');
  audio.play().catch(function(e) { console.log('Audio autoplay blocked:', e); });

  runTour();
}

function runTour() {
  if (currentStepIndex >= steps.length) {
    isPlaying = false;
    document.getElementById('play-btn').textContent = 'Restart';
    document.getElementById('phaseText').textContent = 'Phase: Complete';
    return;
  }
  
  var s = steps[currentStepIndex];
  document.getElementById('phaseText').textContent = 'Phase: ' + s.t;
  
  // Update Slide Content
  document.querySelectorAll('.slide-content').forEach(function(el) { el.classList.remove('active'); });
  document.getElementById('slide-' + s.s).classList.add('active');
  
  // Speak narration (TTS for slides after intro; intro uses custom audio)
  if (s.voice) {
    speak(s.voice);
  }
  
  // Apply visual action
  s.act();
  
  // Timeline Animation
  var totalStepTime = s.d;
  var stepElapsed = 0;
  var stepInterval = setInterval(function() {
    if (!isPlaying) {
      clearInterval(stepInterval);
      return;
    }
    stepElapsed += 100;
    var progressVal = ((currentStepIndex / steps.length) * 100) + ((stepElapsed / totalStepTime) * (100 / steps.length));
    document.getElementById('timeline-progress').style.width = Math.min(progressVal, 100) + '%';
  }, 100);

  autoTimer = setTimeout(function() {
    clearInterval(stepInterval);
    if (isPlaying) {
      currentStepIndex++;
      runTour();
    }
  }, s.d);
}

function togglePlay() {
  if (isPlaying) {
    isPlaying = false;
    clearTimeout(autoTimer);
    document.getElementById('play-btn').textContent = 'Resume';
    document.getElementById('voiceAudio').pause();
    if (window.speechSynthesis) window.speechSynthesis.cancel();
  } else {
    if (currentStepIndex >= steps.length) {
      currentStepIndex = 0;
      resetAll();
    }
    isPlaying = true;
    document.getElementById('play-btn').textContent = 'Pause';
    document.getElementById('voiceAudio').play().catch(function(){});
    runTour();
  }
}

function toggleExplode() {
  exploded = !exploded;
  document.getElementById('hudExplode').classList.toggle('active', exploded);
}

function toggleWire() {
  wireOn = !wireOn;
  document.getElementById('hudWire').classList.toggle('active', wireOn);
  for (var i = 0; i < meshes.length; i++) {
    if (meshes[i]) meshes[i].material.wireframe = wireOn;
  }
}

function resetAll() {
  orb = {t:Math.PI/4, p:Math.PI/7}; rad = 230; pan = {x:0, y:30, z:0};
  exploded = false; wireOn = false; currentDay = 0;
  document.getElementById('dayLbl').textContent = DAYS[0];
  document.querySelectorAll('.inter-btn').forEach(function(b){ b.classList.remove('active'); });
  for (var i = 0; i < meshes.length; i++) {
    if (meshes[i]) {
      meshes[i].material.wireframe = false;
      meshes[i].rotation.y = 0;
    }
  }
  for (var j = 0; j < dispensedPills.length; j++) {
    scene.remove(dispensedPills[j]);
  }
  dispensedPills = [];
  camUp();
}

window.addEventListener('resize', function() {
  var container = document.getElementById('canvas-container');
  if (cam && ren) {
    cam.aspect = container.clientWidth / container.clientHeight;
    cam.updateProjectionMatrix();
    ren.setSize(container.clientWidth, container.clientHeight);
  }
});
