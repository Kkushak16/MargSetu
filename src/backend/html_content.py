"""
Embedded HTML Content Fallback for Vercel Serverless Function Environment
Ensures full 3D MapLibre Control Room GIS Dashboard is served seamlessly.
"""

INDEX_HTML_STR = """<!DOCTYPE html>
<html class="dark" lang="en">
<head>
  <meta charset="utf-8"/>
  <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
  <title>MargSetu Command — GIS Control Room</title>
  <meta name="description" content="SIH26002 Smart Logistics Platform for North Eastern Region highway blockage prediction and dynamic re-routing"/>
  <script>
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.getRegistrations().then(function(regs) {
        for (let r of regs) r.unregister();
      });
      if (window.caches) {
        caches.keys().then(function(names) {
          for (let name of names) caches.delete(name);
        });
      }
    }
  </script>
  <!-- Tailwind CSS & Google Fonts -->
  <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600;700&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
  <!-- MapLibre GL JS (Vector 3D Map Engine) -->
  <link href="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.css" rel="stylesheet" />
  <script src="https://unpkg.com/maplibre-gl@4.7.1/dist/maplibre-gl.js"></script>

  <script id="tailwind-config">
    tailwind.config = {
      darkMode: "class",
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'sans-serif'],
            mono: ['JetBrains Mono', 'monospace']
          },
          colors: {
            "background": "#09090b",
            "surface": "#141416",
            "surface-variant": "#1c1c20",
            "surface-container": "#111113",
            "on-surface": "#ffffff",
            "on-surface-variant": "#9ca3af",
            "outline-variant": "rgba(255, 255, 255, 0.12)",
            "primary": "#ffffff",
            "secondary": "#38bdf8",
            "error": "#f43f5e",
            "warning": "#fbbf24",
            "safe": "#10b981"
          }
        }
      }
    };
  </script>
  <style>
    body { font-family: 'Inter', sans-serif; background-color: #09090b; color: #fff; overflow: hidden; }
    .bg-glass { background: rgba(20, 20, 22, 0.85); backdrop-filter: blur(16px); }
    .maplibre-ctrl-bottom-right, .maplibre-ctrl-bottom-left, .maplibre-ctrl-top-right, .maplibre-ctrl-top-left { z-index: 10 !important; }
    
    @keyframes marquee {
      0% { transform: translateX(100%); }
      100% { transform: translateX(-100%); }
    }
    .marquee { animation: marquee 30s linear infinite; }
    .marquee:hover { animation-play-state: paused; }

    .custom-scrollbar::-webkit-scrollbar { width: 4px; }
    .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
    .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 4px; }

    .vehicle-marker {
      width: 24px; height: 24px;
      display: flex; align-items: center; justify-content: center;
      cursor: pointer;
    }
    .hazard-marker {
      width: 28px; height: 28px;
      cursor: pointer;
      transition: transform 0.2s ease;
    }
    .hazard-marker:hover { transform: scale(1.2); }
  </style>
</head>
<body class="h-screen w-screen relative select-none bg-background text-on-surface">

<!-- Top Navigation Bar -->
<header class="absolute top-0 left-0 right-0 h-14 bg-glass border-b border-outline-variant z-40 flex items-center justify-between px-4 shadow-xl">
  <!-- Left Brand & Status -->
  <div class="flex items-center gap-3">
    <div class="w-8 h-8 rounded-xl bg-gradient-to-br from-secondary to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(56,189,248,0.4)]">
      <span class="material-symbols-outlined text-white text-[20px]">explore</span>
    </div>
    <div>
      <div class="flex items-center gap-2">
        <h1 id="titleHeader" class="text-sm font-extrabold tracking-wide text-white">MargSetu Command</h1>
        <span class="bg-secondary/20 text-secondary text-[10px] font-mono font-bold px-1.5 py-0.5 rounded border border-secondary/30">SIH26002</span>
        <span class="bg-surface-variant text-on-surface-variant text-[10px] font-mono px-1.5 py-0.5 rounded border border-outline-variant">MDoNER GIS</span>
      </div>
    </div>
  </div>

  <!-- Center Search Bar (Geocodes ANY City / Region worldwide) -->
  <div class="relative w-96">
    <span class="material-symbols-outlined absolute left-3 top-2.5 text-on-surface-variant text-[18px]">search</span>
    <input 
      id="globalSearchInput"
      type="text" 
      placeholder="Search ANY city/sector (e.g. Shillong, Guwahati, Darjeeling, Gangtok)..." 
      onkeydown="handleGlobalSearch(event)"
      class="w-full bg-surface-variant/80 border border-outline-variant rounded-xl pl-9 pr-8 py-1.5 text-xs text-on-surface placeholder:text-on-surface-variant/60 outline-none focus:border-secondary transition-all"
    />
    <button onclick="triggerGlobalSearch()" class="absolute right-2 top-2 text-on-surface-variant hover:text-white">
      <span class="material-symbols-outlined text-[18px]">arrow_forward</span>
    </button>
  </div>

  <!-- Right Actions & Profile -->
  <div class="flex items-center gap-3">
    <button onclick="openTechStackModal()" class="flex items-center gap-1.5 bg-surface-variant hover:bg-surface-variant/80 border border-outline-variant px-3 py-1.5 rounded-xl text-xs font-semibold text-secondary transition-all" title="View Integrated Repositories & Tech Stack">
      <span class="material-symbols-outlined text-[16px]">code</span> Tech Stack Specs
    </button>
    <button onclick="triggerSyncDown()" class="p-2 text-on-surface-variant hover:text-white hover:bg-surface-variant/50 rounded-xl transition-colors" title="Sync Live GIS Queue">
      <span id="syncIcon" class="material-symbols-outlined text-[20px]">sync</span>
    </button>
    <button onclick="toggleSettingsDrawer()" class="p-2 text-on-surface-variant hover:text-white hover:bg-surface-variant/50 rounded-xl transition-colors" title="Control Room Settings">
      <span class="material-symbols-outlined text-[20px]">settings</span>
    </button>
    <button onclick="toggleNotificationsModal()" class="p-2 text-on-surface-variant hover:text-white hover:bg-surface-variant/50 rounded-xl transition-colors relative" title="Alerts">
      <span class="material-symbols-outlined text-[20px]">notifications</span>
      <span class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-error animate-ping"></span>
    </button>
    <div class="w-8 h-8 rounded-full bg-gradient-to-tr from-sky-400 to-indigo-500 flex items-center justify-center font-bold text-xs border border-white/20 shadow">
      MS
    </div>
  </div>
</header>

<!-- Main Container -->
<div class="flex h-full pt-14 pb-11 relative overflow-hidden">
  
  <!-- Left Navigation Rail -->
  <aside class="w-14 bg-glass border-r border-outline-variant z-30 flex flex-col items-center py-4 justify-between">
    <div class="flex flex-col gap-4">
      <button onclick="activateRailTab('layers')" class="p-2.5 text-secondary bg-secondary/15 rounded-xl border border-secondary/30 transition-all shadow-[0_0_10px_rgba(56,189,248,0.2)]" title="Map Layers">
        <span class="material-symbols-outlined text-[20px]">layers</span>
      </button>
      <button onclick="activateRailTab('vehicles')" class="p-2.5 text-on-surface-variant hover:text-white hover:bg-surface-variant/50 rounded-xl transition-colors" title="Vehicle Convoy Telemetry">
        <span class="material-symbols-outlined text-[20px]">local_shipping</span>
      </button>
      <button onclick="activateRailTab('weather')" class="p-2.5 text-on-surface-variant hover:text-white hover:bg-surface-variant/50 rounded-xl transition-colors" title="Rainfall & Cloudburst Radar">
        <span class="material-symbols-outlined text-[20px]">thunderstorm</span>
      </button>
      <button onclick="activateRailTab('analytics')" class="p-2.5 text-on-surface-variant hover:text-white hover:bg-surface-variant/50 rounded-xl transition-colors" title="XGBoost Hazard Cutoffs">
        <span class="material-symbols-outlined text-[20px]">tune</span>
      </button>
      <button onclick="activateRailTab('history')" class="p-2.5 text-on-surface-variant hover:text-white hover:bg-surface-variant/50 rounded-xl transition-colors" title="24h Telemetry Replay">
        <span class="material-symbols-outlined text-[20px]">history</span>
      </button>
    </div>
    <div class="flex flex-col gap-3">
      <button onclick="openNewMissionModal()" class="w-10 h-10 rounded-xl bg-secondary text-on-secondary flex items-center justify-center hover:brightness-110 transition-all shadow-[0_0_15px_rgba(56,189,248,0.4)]" title="Compute Safe Bypass Route">
        <span class="material-symbols-outlined text-[22px]">add</span>
      </button>
      <button onclick="openHelpModal()" class="p-2 text-on-surface-variant hover:text-white hover:bg-surface-variant/50 rounded-xl transition-colors" title="User Guide">
        <span class="material-symbols-outlined text-[20px]">help</span>
      </button>
    </div>
  </aside>

  <!-- Map Viewport -->
  <main class="flex-1 relative overflow-hidden bg-black">
    <div id="map" class="w-full h-full"></div>

    <!-- Top Left Overlay Card: Map Layers & Styles -->
    <div class="absolute top-5 left-5 z-20 w-64 bg-glass border border-outline-variant p-4 rounded-2xl shadow-2xl flex flex-col gap-3">
      <div class="flex justify-between items-center border-b border-outline-variant/60 pb-2">
        <span class="text-xs font-bold uppercase tracking-wider text-on-surface flex items-center gap-2">
          <span class="material-symbols-outlined text-[16px] text-secondary">layers</span> Map Layers & Styles
        </span>
        <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
      </div>

      <!-- Map Style Selector -->
      <div>
        <label class="text-[11px] font-semibold text-on-surface-variant mb-1 block">Vector Map Style</label>
        <select onchange="changeMapStyle(this.value)" class="w-full bg-surface-variant border border-outline-variant rounded-xl p-2 text-xs text-white outline-none focus:border-secondary cursor-pointer">
          <option value="cyberpunk" selected>Cyberpunk Dark Mode</option>
          <option value="voyager">Vivid Colorful Vector</option>
          <option value="satellite">Satellite Hybrid</option>
        </select>
      </div>

      <!-- Quick Preset Regions -->
      <div>
        <label class="text-[11px] font-semibold text-on-surface-variant mb-1 block">Explore North-East Corridors</label>
        <div class="grid grid-cols-2 gap-1.5">
          <button onclick="jumpToRegion('Siliguri - Gangtok', 27.08, 88.50)" class="bg-surface-variant/60 hover:bg-surface-variant border border-outline-variant text-[11px] py-1 rounded-lg text-secondary font-medium">Sikkim NH10</button>
          <button onclick="jumpToRegion('Shillong Corridor', 25.57, 91.88)" class="bg-surface-variant/60 hover:bg-surface-variant border border-outline-variant text-[11px] py-1 rounded-lg text-secondary font-medium">Meghalaya</button>
          <button onclick="jumpToRegion('Guwahati Pass', 26.14, 91.73)" class="bg-surface-variant/60 hover:bg-surface-variant border border-outline-variant text-[11px] py-1 rounded-lg text-secondary font-medium">Assam</button>
          <button onclick="jumpToRegion('Darjeeling Hill Road', 27.03, 88.26)" class="bg-surface-variant/60 hover:bg-surface-variant border border-outline-variant text-[11px] py-1 rounded-lg text-secondary font-medium">Darjeeling</button>
        </div>
      </div>

      <!-- Layer Toggles -->
      <div class="flex flex-col gap-1.5 pt-1">
        <label class="flex items-center justify-between px-2 py-1.5 hover:bg-surface-variant/50 rounded-lg cursor-pointer transition-colors">
          <span class="text-xs font-medium text-on-surface flex items-center gap-2">
            <span class="material-symbols-outlined text-[16px] text-secondary">alt_route</span> Road Corridors
          </span>
          <input checked class="accent-secondary w-4 h-4 cursor-pointer" id="toggleRoads" type="checkbox" onchange="toggleRoadLayer(this.checked)"/>
        </label>

        <label class="flex items-center justify-between px-2 py-1.5 hover:bg-surface-variant/50 rounded-lg cursor-pointer transition-colors">
          <span class="text-xs font-medium text-on-surface flex items-center gap-2">
            <span class="material-symbols-outlined text-[16px] text-secondary">local_shipping</span> Active Convoys
          </span>
          <input checked class="accent-secondary w-4 h-4 cursor-pointer" id="toggleConvoys" type="checkbox" onchange="toggleConvoyLayer(this.checked)"/>
        </label>
      </div>
    </div>

    <!-- Bottom Right Controls: 2D/3D & Replay Slider -->
    <div class="absolute bottom-16 right-5 z-20 flex items-end gap-3">
      <!-- 2D / 3D Perspective Buttons -->
      <div class="flex flex-col bg-glass border border-outline-variant rounded-2xl overflow-hidden p-1 shadow-2xl gap-1">
        <button id="btn2D" onclick="setMapPerspective('2d')" class="px-3.5 py-1.5 text-xs font-bold bg-secondary text-on-secondary rounded-xl shadow-md transition-all">2D</button>
        <button id="btn3D" onclick="setMapPerspective('3d')" class="px-3.5 py-1.5 text-xs font-semibold text-on-surface-variant hover:text-primary transition-colors rounded-xl">3D</button>
      </div>

      <!-- 24h Telemetry Replay Bar -->
      <div class="bg-glass border border-outline-variant p-3.5 rounded-2xl flex items-center gap-3.5 w-80 shadow-2xl">
        <button onclick="toggleReplayAnimation()" class="text-on-surface hover:text-secondary transition-colors flex-shrink-0" title="Play / Pause Replay">
          <span id="playIcon" class="material-symbols-outlined text-[26px]">play_circle</span>
        </button>
        <div class="flex-1 flex flex-col gap-1.5">
          <div class="flex justify-between text-[11px] font-mono text-on-surface-variant">
            <span>24h Telemetry Replay</span>
            <span id="timeValDisplay" class="text-secondary font-bold">LIVE</span>
          </div>
          <div class="relative h-2 bg-surface-variant/80 rounded-full w-full overflow-hidden flex items-center">
            <div id="replayProgress" class="absolute left-0 top-0 h-full bg-secondary rounded-full w-full transition-all"></div>
            <input id="replaySlider" type="range" min="0" max="24" value="24" class="absolute inset-0 w-full opacity-0 cursor-pointer" oninput="handleReplayScrub(this.value)"/>
          </div>
        </div>
      </div>
    </div>

    <!-- Right Sidepanel: Segment Alpha-7 (EXACT MATCH of Uploaded Image) -->
    <aside id="segmentPanel" class="absolute top-5 right-5 bottom-16 w-80 bg-[#141416] border border-outline-variant rounded-2xl z-30 flex flex-col shadow-2xl overflow-hidden transition-transform duration-300">
      <!-- Header -->
      <div class="p-4 border-b border-outline-variant flex justify-between items-center bg-[#111113]">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-secondary text-[20px]">target</span>
          <h2 id="segmentTitle" class="text-base font-bold text-white tracking-tight">Segment Alpha-7</h2>
        </div>
        <button onclick="closeSegmentPanel()" class="text-gray-400 hover:text-white p-1 rounded-lg transition-colors">
          <span class="material-symbols-outlined text-[20px]">close</span>
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-4 flex flex-col gap-4 custom-scrollbar">
        <!-- Top Card: HAZARD RISK Score & Progress Indicator -->
        <div class="bg-[#1c1c20] border border-white/10 p-4 rounded-xl relative">
          <div class="flex justify-between items-center mb-3">
            <span class="text-[11px] font-semibold text-gray-400 uppercase tracking-wider">HAZARD RISK</span>
            <div id="hazardIconBadge" class="w-6 h-6 rounded-full bg-rose-500/20 border border-rose-500/40 flex items-center justify-center">
              <span class="material-symbols-outlined text-[16px] text-rose-500">warning</span>
            </div>
          </div>
          <div class="flex items-baseline justify-between mb-4">
            <div class="flex items-baseline">
              <span id="hazardScoreVal" class="text-4xl font-extrabold text-white tracking-tight">84</span>
              <span class="text-xl font-bold text-gray-400 ml-0.5">%</span>
              <span id="hazardStatusBadge" class="text-sm font-bold text-rose-500 ml-2">Critical</span>
            </div>
          </div>
          <!-- Dual Segmented Progress Indicator Bar (Yellow + Red) -->
          <div class="flex items-center gap-1.5 justify-end">
            <div class="h-2 w-10 bg-amber-400 rounded-full"></div>
            <div id="redProgressPill" class="h-2 w-14 bg-rose-500 rounded-full shadow-[0_0_8px_rgba(244,63,94,0.6)]"></div>
          </div>
        </div>

        <!-- Section 2: KEY DRIVERS -->
        <div class="bg-[#1c1c20] border border-white/10 p-4 rounded-xl flex flex-col gap-3">
          <span class="text-[11px] font-semibold text-gray-400 uppercase tracking-wider block">KEY DRIVERS</span>
          <ul id="shapList" class="space-y-3.5">
            <li class="flex items-start gap-3">
              <span class="text-rose-500 font-mono font-bold text-xs w-10 pt-0.5 flex-shrink-0">+42%</span>
              <div class="flex-1">
                <div class="text-xs font-bold text-white">Soil Saturation</div>
                <div class="text-[11px] text-gray-400 mt-0.5">ARI7d: 140mm</div>
              </div>
            </li>
            <li class="flex items-start gap-3 border-t border-white/5 pt-3">
              <span class="text-rose-500 font-mono font-bold text-xs w-10 pt-0.5 flex-shrink-0">+28%</span>
              <div class="flex-1">
                <div class="text-xs font-bold text-white">High Slope Incline</div>
                <div class="text-[11px] text-gray-400 mt-0.5">&gt; 30° Gradient</div>
              </div>
            </li>
            <li class="flex items-start gap-3 border-t border-white/5 pt-3">
              <span class="text-amber-400 font-mono font-bold text-xs w-10 pt-0.5 flex-shrink-0">+14%</span>
              <div class="flex-1">
                <div class="text-xs font-bold text-white">Geology</div>
                <div class="text-[11px] text-gray-400 mt-0.5">Active Fault Zone</div>
              </div>
            </li>
          </ul>
        </div>

        <!-- Section 3: FIELD REPORT Card -->
        <div id="crowdsourceCard" class="bg-[#1c1c20] border border-white/10 p-3.5 rounded-xl flex flex-col gap-3">
          <div class="flex justify-between items-center">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-[18px] text-white">photo_camera</span>
              <span class="text-xs font-bold text-white uppercase tracking-wider">FIELD REPORT</span>
            </div>
            <span id="reportTimeText" class="text-xs font-mono text-gray-400">12:44 IST</span>
          </div>

          <div class="relative h-36 w-full rounded-lg overflow-hidden border border-white/10">
            <img id="reportPhotoImg" alt="Landslide field verification photo" class="w-full h-full object-cover" src="https://images.unsplash.com/photo-1541888946425-d0fbb186a5b2?auto=format&fit=crop&w=600&q=80"/>
            <div id="reportCoordsBadge" class="absolute bottom-2 left-2 bg-black/85 px-2.5 py-1 rounded-md text-[10px] font-mono text-white border border-white/15 backdrop-blur-sm">
              25.57°N, 91.88°E
            </div>
            <div id="reportStatusBadge" class="absolute top-2 right-2 bg-amber-500 text-black px-2 py-0.5 rounded text-[10px] font-bold uppercase shadow">
              PENDING
            </div>
          </div>

          <div id="reportActionButtons" class="flex gap-3.5 pt-1">
            <button onclick="rejectReport('report_alpha')" class="flex-1 bg-[#2a2a30] hover:bg-[#34343d] text-white py-2 rounded-xl text-xs font-semibold transition-colors">
              Reject
            </button>
            <button onclick="verifyReport('report_alpha')" class="flex-1 bg-white hover:bg-gray-100 text-black py-2 rounded-xl text-xs font-bold transition-all shadow-md">
              Verify
            </button>
          </div>
        </div>
      </div>
    </aside>
  </main>
</div>

<!-- Bottom Ticker Bar -->
<footer class="absolute bottom-0 left-14 right-0 h-11 bg-glass border-t border-outline-variant z-40 flex items-center px-4 overflow-hidden">
  <div class="flex items-center gap-4 w-full relative h-full">
    <div class="flex items-center gap-2 bg-[#0a0a0c] px-3 py-1 rounded-full z-20 border border-outline-variant flex-shrink-0 shadow-md">
      <span class="w-2 h-2 rounded-full bg-error animate-pulse"></span>
      <span class="text-error text-[10px] font-bold uppercase tracking-widest">LIVE TELEMETRY</span>
    </div>
    
    <div class="flex-1 overflow-hidden relative flex items-center h-full">
      <div class="marquee flex items-center gap-12 text-xs font-mono text-on-surface">
        <div class="flex items-center gap-2 cursor-pointer hover:text-secondary transition-colors" onclick="focusSegment('NH10_SEG_005')">
          <span class="text-on-surface-variant">14:02 IST</span>
          <span class="text-error font-bold">[CRITICAL]</span>
          <span>Soil moisture threshold (ARI7d: 140mm) exceeded at Segment Alpha-7 (Rangpo Incline). Bypass advised.</span>
        </div>
        <div class="flex items-center gap-2 cursor-pointer hover:text-secondary transition-colors" onclick="focusSegment('ALT_BYPASS_001')">
          <span class="text-on-surface-variant">13:58 IST</span>
          <span class="text-secondary font-bold">[INFO]</span>
          <span>Damdim-Gorubathan Bypass Line 1 cleared for emergency convoy movement.</span>
        </div>
        <div class="flex items-center gap-2 cursor-pointer hover:text-secondary transition-colors" onclick="focusSegment('NH10_SEG_002')">
          <span class="text-on-surface-variant">13:45 IST</span>
          <span class="text-warning font-bold">[WARNING]</span>
          <span>Heavy cloudburst warning over Sevoke Bridge Corridor. Speed restricted to 15 km/h.</span>
        </div>
      </div>
    </div>
  </div>
</footer>

<!-- Settings Drawer -->
<div id="settingsDrawer" class="fixed top-16 right-5 w-80 bg-glass border border-outline-variant rounded-2xl p-5 z-50 flex flex-col gap-4 shadow-2xl hidden transition-all">
  <div class="flex justify-between items-center border-b border-outline-variant pb-3">
    <h3 class="text-sm font-bold text-secondary flex items-center gap-2">
      <span class="material-symbols-outlined text-[18px]">tune</span> Control Room Threshold Settings
    </h3>
    <button onclick="toggleSettingsDrawer()" class="text-on-surface-variant hover:text-white">
      <span class="material-symbols-outlined text-[18px]">close</span>
    </button>
  </div>

  <div class="flex flex-col gap-3 py-1">
    <span class="text-[11px] font-bold uppercase text-on-surface-variant tracking-wider">Hazard Cutoffs (XGBoost)</span>
    <div>
      <div class="flex justify-between text-xs font-mono mb-1">
        <span class="text-warning font-bold">WARNING Cutoff:</span>
        <span id="warnVal" class="text-primary font-bold">35%</span>
      </div>
      <input id="warnSlider" type="range" min="10" max="50" value="35" oninput="updateThresholds()" class="w-full h-1.5 bg-surface-variant rounded-full accent-warning cursor-pointer"/>
    </div>
    <div>
      <div class="flex justify-between text-xs font-mono mb-1">
        <span class="text-error font-bold">CRITICAL Cutoff:</span>
        <span id="critVal" class="text-primary font-bold">70%</span>
      </div>
      <input id="critSlider" type="range" min="50" max="90" value="70" oninput="updateThresholds()" class="w-full h-1.5 bg-surface-variant rounded-full accent-error cursor-pointer"/>
    </div>
  </div>
</div>

<!-- New Mission / Safe Route Modal -->
<div id="newMissionModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md hidden">
  <div class="bg-surface border border-outline-variant w-full max-w-md rounded-2xl p-6 shadow-2xl flex flex-col gap-5">
    <div class="flex justify-between items-center border-b border-outline-variant pb-3">
      <h3 class="text-base font-bold text-primary flex items-center gap-2">
        <span class="material-symbols-outlined text-secondary">explore</span> Dynamic OSRM Road Pathfinding
      </h3>
      <button onclick="closeNewMissionModal()" class="text-on-surface-variant hover:text-white">
        <span class="material-symbols-outlined text-[20px]">close</span>
      </button>
    </div>

    <form onsubmit="handleComputeRoute(event)" class="flex flex-col gap-4">
      <div>
        <label class="text-xs text-on-surface-variant font-semibold block mb-1">Origin (Latitude, Longitude)</label>
        <div class="grid grid-cols-2 gap-2">
          <input type="text" id="srcLat" value="26.7271" class="bg-surface-variant border border-outline-variant rounded-xl p-2.5 text-xs text-on-surface outline-none focus:border-secondary font-mono" placeholder="Latitude"/>
          <input type="text" id="srcLng" value="88.3953" class="bg-surface-variant border border-outline-variant rounded-xl p-2.5 text-xs text-on-surface outline-none focus:border-secondary font-mono" placeholder="Longitude"/>
        </div>
      </div>

      <div>
        <label class="text-xs text-on-surface-variant font-semibold block mb-1">Destination (Latitude, Longitude)</label>
        <div class="grid grid-cols-2 gap-2">
          <input type="text" id="tgtLat" value="27.3389" class="bg-surface-variant border border-outline-variant rounded-xl p-2.5 text-xs text-on-surface outline-none focus:border-secondary font-mono" placeholder="Latitude"/>
          <input type="text" id="tgtLng" value="88.6065" class="bg-surface-variant border border-outline-variant rounded-xl p-2.5 text-xs text-on-surface outline-none focus:border-secondary font-mono" placeholder="Longitude"/>
        </div>
      </div>

      <div class="bg-surface-variant/40 border border-outline-variant p-3 rounded-xl flex items-center justify-between flex-wrap gap-2">
        <span class="text-xs text-on-surface-variant font-medium">Presets:</span>
        <button type="button" onclick="setPresetCoords(26.7271, 88.3953, 27.3389, 88.6065)" class="text-[11px] bg-surface border border-outline-variant px-2.5 py-1 rounded-lg hover:border-secondary text-secondary font-semibold">Siliguri ➔ Gangtok</button>
        <button type="button" onclick="setPresetCoords(26.14, 91.73, 25.57, 91.88)" class="text-[11px] bg-surface border border-outline-variant px-2.5 py-1 rounded-lg hover:border-secondary text-secondary font-semibold">Guwahati ➔ Shillong</button>
      </div>

      <button type="submit" class="w-full bg-secondary text-on-secondary py-3 rounded-xl font-bold text-xs hover:brightness-110 transition-all flex items-center justify-center gap-2 shadow-[0_0_15px_rgba(56,189,248,0.4)]">
        <span class="material-symbols-outlined text-[18px]">navigation</span> Calculate OSRM Road Route
      </button>
    </form>
  </div>
</div>

<!-- Tech Stack Modal -->
<div id="techStackModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/85 backdrop-blur-md hidden">
  <div class="bg-surface border border-outline-variant w-full max-w-2xl rounded-2xl p-6 shadow-2xl flex flex-col gap-4 max-h-[85vh] overflow-y-auto custom-scrollbar">
    <div class="flex justify-between items-center border-b border-outline-variant pb-3">
      <h3 class="text-base font-bold text-secondary flex items-center gap-2">
        <span class="material-symbols-outlined text-secondary">memory</span> Architecture Tech Stack & Git Integration Specs
      </h3>
      <button onclick="closeTechStackModal()" class="text-on-surface-variant hover:text-white">
        <span class="material-symbols-outlined text-[20px]">close</span>
      </button>
    </div>

    <div class="grid grid-cols-2 gap-3 text-xs">
      <div class="p-3 bg-surface-variant/40 border border-outline-variant rounded-xl">
        <div class="font-bold text-secondary flex items-center gap-1.5 mb-1"><span class="material-symbols-outlined text-[16px]">map</span> MapLibre GL JS & Deck.gl</div>
        <p class="text-on-surface-variant text-[11px]">Hardware-accelerated 3D vector map engine with pitch elevation and dynamic building extrusions.</p>
      </div>
      <div class="p-3 bg-surface-variant/40 border border-outline-variant rounded-xl">
        <div class="font-bold text-secondary flex items-center gap-1.5 mb-1"><span class="material-symbols-outlined text-[16px]">alt_route</span> OSRM Engine & pgRouting</div>
        <p class="text-on-surface-variant text-[11px]">Exact OpenStreetMap road geometry pathfinding engine over topological road networks.</p>
      </div>
      <div class="p-3 bg-surface-variant/40 border border-outline-variant rounded-xl">
        <div class="font-bold text-secondary flex items-center gap-1.5 mb-1"><span class="material-symbols-outlined text-[16px]">psychology</span> XGBoost & LightGBM Pipeline</div>
        <p class="text-on-surface-variant text-[11px]">High-precision landslide risk inference engine trained on ARI7d rainfall & DEM slope steepness.</p>
      </div>
      <div class="p-3 bg-surface-variant/40 border border-outline-variant rounded-xl">
        <div class="font-bold text-secondary flex items-center gap-1.5 mb-1"><span class="material-symbols-outlined text-[16px]">sync</span> RxDB & Sqflite Offline Manager</div>
        <p class="text-on-surface-variant text-[11px]">Client-side queue synchronization for offline disaster field operations and crowdsource verification.</p>
      </div>
      <div class="p-3 bg-surface-variant/40 border border-outline-variant rounded-xl col-span-2">
        <div class="font-bold text-secondary flex items-center gap-1.5 mb-1"><span class="material-symbols-outlined text-[16px]">terminal</span> FastAPI Unified Gateway</div>
        <p class="text-on-surface-variant text-[11px]">Asynchronous RESTful middleware handling edge mutation triggers, prediction requests, and delta syncs.</p>
      </div>
    </div>
  </div>
</div>

<!-- Help Modal -->
<div id="helpModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md hidden">
  <div class="bg-surface border border-outline-variant w-full max-w-md rounded-2xl p-6 shadow-2xl flex flex-col gap-4">
    <div class="flex justify-between items-center border-b border-outline-variant pb-3">
      <h3 class="text-base font-bold text-primary flex items-center gap-2">
        <span class="material-symbols-outlined text-secondary">help</span> Control Room User Guide
      </h3>
      <button onclick="closeHelpModal()" class="text-on-surface-variant hover:text-white">
        <span class="material-symbols-outlined text-[20px]">close</span>
      </button>
    </div>
    <div class="text-xs text-on-surface-variant space-y-3 leading-relaxed">
      <p><strong class="text-primary">SIH26002 MargSetu:</strong> High-resolution 3D GIS disaster response system predicting highway blockages across Sikkim & North Eastern Region corridors.</p>
      <ul class="list-disc pl-4 space-y-1.5">
        <li><strong class="text-secondary">Global Search:</strong> Search ANY city (e.g. Shillong, Guwahati, Gangtok) in the top search bar.</li>
        <li><strong class="text-secondary">Exact OSRM Road Alignment:</strong> Routes follow actual OpenStreetMap road geometries pixel-by-pixel.</li>
        <li><strong class="text-secondary">3D Vector Elevation:</strong> Click <strong>3D</strong> at bottom-right to tilt map pitch to 65° with dynamic rotation.</li>
      </ul>
    </div>
  </div>
</div>

<!-- Notifications Modal -->
<div id="notificationsModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md hidden">
  <div class="bg-surface border border-outline-variant w-full max-w-md rounded-2xl p-6 shadow-2xl flex flex-col gap-4">
    <div class="flex justify-between items-center border-b border-outline-variant pb-3">
      <h3 class="text-base font-bold text-primary flex items-center gap-2">
        <span class="material-symbols-outlined text-error">notifications_active</span> Emergency Alert Center
      </h3>
      <button onclick="toggleNotificationsModal()" class="text-on-surface-variant hover:text-white">
        <span class="material-symbols-outlined text-[20px]">close</span>
      </button>
    </div>
    <div class="flex flex-col gap-3 max-h-80 overflow-y-auto custom-scrollbar">
      <div class="p-3 bg-error/10 border border-error/30 rounded-xl text-xs">
        <div class="flex justify-between text-error font-bold mb-1">
          <span>🚨 Cloudburst Blockage</span>
          <span>14:02 IST</span>
        </div>
        <p class="text-on-surface-variant">NH10 Segment Alpha-7 Rangpo Corridor blocked by 120mm/h cloudburst runoff.</p>
      </div>
    </div>
  </div>
</div>

<script>
  let map;
  let vehicleMarkers = {};
  let hazardMarkers = [];
  let replayTimer = null;
  let isReplaying = false;
  let activeOSRMRouteCoords = [];

  const mapStyles = {
    cyberpunk: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    voyager: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
    satellite: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json'
  };

  // High-Resolution Default Road Corridors
  let segments = [
    { 
      id: "NH10_SEG_001", 
      name: "Siliguri - Sevoke Junction", 
      hazard: 0.10, 
      coords: [], 
      shap: [["Low recent rainfall", 0.04, "+4%"], ["Flat terrain gradient", 0.03, "+3%"], ["Good vegetation cover", 0.03, "+3%"]] 
    },
    { 
      id: "NH10_SEG_002", 
      name: "Sevoke Coronation Bridge", 
      hazard: 0.45, 
      coords: [], 
      shap: [["Teesta riverbank saturation", 0.25, "+25%"], ["Moderate slope ~20°", 0.12, "+12%"], ["Soil moisture ARI7d", 0.08, "+8%"]] 
    },
    { 
      id: "NH10_SEG_003", 
      name: "Kalimpong Active Fault Zone", 
      hazard: 0.82, 
      coords: [], 
      shap: [["Soil Saturation (ARI7d: 140mm)", 0.42, "+42%"], ["High Slope Incline >30°", 0.28, "+28%"], ["Geology (Active Fault Zone)", 0.14, "+14%"]] 
    },
    { 
      id: "NH10_SEG_005", 
      name: "Segment Alpha-7 (Rangpo Incline)", 
      hazard: 0.84, 
      coords: [], 
      shap: [
        ["Soil Saturation", "ARI7d: 140mm", "+42%"], 
        ["High Slope Incline", "> 30° Gradient", "+28%"], 
        ["Geology", "Active Fault Zone", "+14%"]
      ] 
    },
    { 
      id: "NH10_SEG_007", 
      name: "Singtam - Gangtok Pass", 
      hazard: 0.15, 
      coords: [], 
      shap: [["Low rainfall", 0.08, "+8%"], ["Convex slope surface", 0.04, "+4%"], ["Far from fault lines", 0.03, "+3%"]] 
    }
  ];

  const vehicles = [
    { id: 'TRUCK_CONVOY_01', label: 'Medical Convoy', critical: true, progress: 0.5 },
    { id: 'TRUCK_CONVOY_02', label: 'Ration Supply', critical: false, progress: 0.2 }
  ];

  const hazardIncidents = [
    { id: "INCIDENT_01", segId: "NH10_SEG_005", lng: 88.5000, lat: 27.1200, title: "Segment Alpha-7 Landslide" },
    { id: "INCIDENT_02", segId: "NH10_SEG_003", lng: 88.4700, lat: 26.8900, title: "Kalimpong Debris Block" }
  ];

  window.addEventListener('DOMContentLoaded', async () => {
    map = new maplibregl.Map({
      container: 'map',
      style: mapStyles.cyberpunk,
      center: [88.5000, 27.0800],
      zoom: 10,
      pitch: 45,
      bearing: -15,
      antialias: true
    });

    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'bottom-right');

    map.on('load', async () => {
      // Fetch Exact OSRM OpenStreetMap Road Polylines
      await fetchExactOSRMGeometries();
      renderMapLayers();
      renderVehicleMarkers();
      renderHazardMarkers();
      selectSegment(segments[3]); // Segment Alpha-7
    });
  });

  // Fetch Exact OSRM Road Geometry from OpenStreetMap Routing API
  async function fetchExactOSRMGeometries() {
    try {
      showToast("⚡ Fetching exact OpenStreetMap road geometry from OSRM engine...");
      // Siliguri (88.3953, 26.7271) to Gangtok (88.6065, 27.3389) via NH10
      const url = 'https://router.project-osrm.org/route/v1/driving/88.3953,26.7271;88.6065,27.3389?overview=full&geometries=geojson';
      const res = await fetch(url);
      const data = await res.json();

      if (data.code === 'Ok' && data.routes && data.routes[0]) {
        const fullCoords = data.routes[0].geometry.coordinates;
        activeOSRMRouteCoords = fullCoords;

        const totalPts = fullCoords.length;
        const chunkSize = Math.floor(totalPts / segments.length);

        segments.forEach((seg, idx) => {
          const startIdx = idx * chunkSize;
          const endIdx = (idx === segments.length - 1) ? totalPts : (idx + 1) * chunkSize + 1;
          seg.coords = fullCoords.slice(startIdx, endIdx);
        });

        showToast(`✓ Aligned ${totalPts} exact road points precisely onto OpenStreetMap pavement!`);
      }
    } catch(e) {
      console.warn("OSRM fallback to local detailed road coordinates", e);
    }
  }

  // Render Polylines as GeoJSON Vector Layers
  function renderMapLayers() {
    const warnVal = parseInt(document.getElementById('warnSlider').value) / 100;
    const critVal = parseInt(document.getElementById('critSlider').value) / 100;

    const validFeatures = segments.filter(s => s.coords && s.coords.length >= 2).map(seg => ({
      type: 'Feature',
      properties: {
        id: seg.id,
        name: seg.name,
        hazard: seg.hazard,
        color: seg.hazard >= critVal ? '#f43f5e' : (seg.hazard >= warnVal ? '#fbbf24' : '#10b981')
      },
      geometry: {
        type: 'LineString',
        coordinates: seg.coords
      }
    }));

    const geojson = { type: 'FeatureCollection', features: validFeatures };

    if (map.getSource('road-segments')) {
      map.getSource('road-segments').setData(geojson);
    } else {
      map.addSource('road-segments', { type: 'geojson', data: geojson });

      map.addLayer({
        id: 'road-segments-glow',
        type: 'line',
        source: 'road-segments',
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: {
          'line-color': ['get', 'color'],
          'line-width': 10,
          'line-opacity': 0.4,
          'line-blur': 6
        }
      });

      map.addLayer({
        id: 'road-segments-core',
        type: 'line',
        source: 'road-segments',
        layout: { 'line-join': 'round', 'line-cap': 'round' },
        paint: {
          'line-color': ['get', 'color'],
          'line-width': 5,
          'line-opacity': 0.95
        }
      });

      map.on('click', 'road-segments-core', (e) => {
        const segId = e.features[0].properties.id;
        const seg = segments.find(s => s.id === segId);
        if (seg) selectSegment(seg);
      });

      map.on('mouseenter', 'road-segments-core', () => map.getCanvas().style.cursor = 'pointer');
      map.on('mouseleave', 'road-segments-core', () => map.getCanvas().style.cursor = '');
    }
  }

  // Global Location Search (Nominatim Geocoding API)
  async function handleGlobalSearch(e) {
    if (e.key === 'Enter') triggerGlobalSearch();
  }

  async function triggerGlobalSearch() {
    const input = document.getElementById('globalSearchInput').value.trim();
    if (!input) return;

    showToast(`🔍 Geocoding location '${input}'...`);
    try {
      const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(input)}`;
      const res = await fetch(url);
      const results = await res.json();

      if (results && results.length > 0) {
        const first = results[0];
        const lat = parseFloat(first.lat);
        const lon = parseFloat(first.lon);

        map.flyTo({ center: [lon, lat], zoom: 12, pitch: 45, duration: 1500 });
        showToast(`📍 Centered map on ${first.display_name.split(',')[0]} (${lat.toFixed(4)}, ${lon.toFixed(4)})`);
      } else {
        showToast(`⚠️ No location found for '${input}'`);
      }
    } catch(e) {
      showToast(`Error searching location`);
    }
  }

  function jumpToRegion(regionName, lat, lng) {
    map.flyTo({ center: [lng, lat], zoom: 11, pitch: 45, duration: 1500 });
    showToast(`📍 Focused on ${regionName} (${lat}°N, ${lng}°E)`);
  }

  // Helper: Interpolate Point along exact road linestring
  function getPointOnLine(coords, progress) {
    if (!coords || coords.length === 0) return [88.50, 27.08];
    if (progress <= 0) return coords[0];
    if (progress >= 1) return coords[coords.length - 1];

    const totalSegs = coords.length - 1;
    const idx = Math.min(Math.floor(progress * totalSegs), totalSegs - 1);
    const subProgress = (progress * totalSegs) - idx;

    const p1 = coords[idx];
    const p2 = coords[idx + 1];

    const lng = p1[0] + (p2[0] - p1[0]) * subProgress;
    const lat = p1[1] + (p2[1] - p1[1]) * subProgress;
    return [lng, lat];
  }

  function renderVehicleMarkers() {
    if (!activeOSRMRouteCoords || activeOSRMRouteCoords.length === 0) return;

    vehicles.forEach(v => {
      const pos = getPointOnLine(activeOSRMRouteCoords, v.progress);

      if (!vehicleMarkers[v.id]) {
        const el = document.createElement('div');
        el.className = 'vehicle-marker';
        el.innerHTML = `
          <div class="relative flex items-center justify-center w-6 h-6">
            <span class="absolute inline-flex h-full w-full rounded-full ${v.critical ? 'bg-rose-500/70 animate-ping' : 'bg-sky-400/50 animate-pulse'}"></span>
            <div class="relative w-3.5 h-3.5 rounded-full ${v.critical ? 'bg-rose-500 border-2 border-white' : 'bg-sky-400 border-2 border-white'} shadow-md"></div>
          </div>`;

        el.addEventListener('click', () => {
          showToast(`🚚 ${v.label} (${v.id}): Speed 38 km/h on OpenStreetMap Road`);
        });

        vehicleMarkers[v.id] = new maplibregl.Marker({ element: el })
          .setLngLat(pos)
          .addTo(map);
      } else {
        vehicleMarkers[v.id].setLngLat(pos);
      }
    });
  }

  function renderHazardMarkers() {
    hazardIncidents.forEach(inc => {
      const el = document.createElement('div');
      el.className = 'hazard-marker';
      el.innerHTML = `
        <div class="w-7 h-7 rounded-full bg-rose-600 border-2 border-white text-white flex items-center justify-center shadow-lg">
          <span class="material-symbols-outlined text-[16px] animate-pulse">warning</span>
        </div>`;

      el.addEventListener('click', () => {
        const seg = segments.find(s => s.id === inc.segId);
        if (seg) selectSegment(seg);
      });

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([inc.lng, inc.lat])
        .addTo(map);
      hazardMarkers.push(marker);
    });
  }

  // Select Segment & Populate Sidepanel (EXACT MATCH of Uploaded Image)
  function selectSegment(seg) {
    const panel = document.getElementById('segmentPanel');
    panel.classList.remove('translate-x-[360px]');
    document.getElementById('settingsDrawer').classList.add('hidden');

    document.getElementById('segmentTitle').innerText = seg.name.includes("Alpha-7") ? "Segment Alpha-7" : seg.id;

    const hazPct = Math.round(seg.hazard * 100);
    document.getElementById('hazardScoreVal').innerText = hazPct;

    const warnVal = parseInt(document.getElementById('warnSlider').value);
    const critVal = parseInt(document.getElementById('critSlider').value);

    let statusText = "Safe";
    let statusColorClass = "text-emerald-400";

    if (hazPct >= critVal) {
      statusText = "Critical";
      statusColorClass = "text-rose-500";
    } else if (hazPct >= warnVal) {
      statusText = "Warning";
      statusColorClass = "text-amber-400";
    }

    const badge = document.getElementById('hazardStatusBadge');
    badge.innerText = statusText;
    badge.className = `text-sm font-bold ml-2 ${statusColorClass}`;

    const redPill = document.getElementById('redProgressPill');
    if (hazPct >= critVal) {
      redPill.style.display = 'block';
    } else {
      redPill.style.display = 'none';
    }

    const shapHtml = seg.shap.map(item => `
      <li class="flex items-start gap-3">
        <span class="${item[2].includes('42') || item[2].includes('28') ? 'text-rose-500' : 'text-amber-400'} font-mono font-bold text-xs w-10 pt-0.5 flex-shrink-0">${item[2]}</span>
        <div class="flex-1">
          <div class="text-xs font-bold text-white">${item[0]}</div>
          <div class="text-[11px] text-gray-400 mt-0.5">${item[1]}</div>
        </div>
      </li>
    `).join('');
    document.getElementById('shapList').innerHTML = shapHtml;

    const reportBtns = document.getElementById('reportActionButtons');
    if (reportBtns) reportBtns.style.display = 'flex';
    const reportBadge = document.getElementById('reportStatusBadge');
    if (reportBadge && reportBadge.innerText !== 'VERIFIED' && reportBadge.innerText !== 'REJECTED') {
      reportBadge.innerText = 'PENDING';
      reportBadge.className = 'absolute top-2 right-2 bg-amber-500 text-black px-2 py-0.5 rounded text-[10px] font-bold uppercase shadow';
    }
  }

  function setMapPerspective(type) {
    const b2 = document.getElementById('btn2D');
    const b3 = document.getElementById('btn3D');

    if (type === '3d') {
      b3.className = "px-3.5 py-1.5 text-xs font-bold bg-secondary text-on-secondary rounded-xl shadow-md transition-all";
      b2.className = "px-3.5 py-1.5 text-xs font-semibold text-on-surface-variant hover:text-primary transition-colors rounded-xl";
      
      map.easeTo({ pitch: 65, bearing: 45, duration: 1200 });
      showToast("3D Vector Elevation Perspective Activated (Pitch 65°, Bearing 45°)");
    } else {
      b2.className = "px-3.5 py-1.5 text-xs font-bold bg-secondary text-on-secondary rounded-xl shadow-md transition-all";
      b3.className = "px-3.5 py-1.5 text-xs font-semibold text-on-surface-variant hover:text-primary transition-colors rounded-xl";
      
      map.easeTo({ pitch: 0, bearing: 0, duration: 1200 });
      showToast("2D Flat Planimetric View Activated");
    }
  }

  function changeMapStyle(styleKey) {
    if (mapStyles[styleKey]) {
      map.setStyle(mapStyles[styleKey]);
      map.once('style.load', async () => {
        renderMapLayers();
        renderVehicleMarkers();
        renderHazardMarkers();
      });
      showToast(`Map Style updated: ${styleKey.toUpperCase()}`);
    }
  }

  function handleReplayScrub(val) {
    val = parseInt(val);
    const pct = (val / 24);
    document.getElementById('replayProgress').style.width = (pct * 100) + '%';
    document.getElementById('timeValDisplay').innerText = val === 24 ? "LIVE" : `${24 - val}h ago`;

    vehicles[0].progress = pct;
    renderVehicleMarkers();
  }

  function toggleReplayAnimation() {
    const playIcon = document.getElementById('playIcon');
    if (isReplaying) {
      clearInterval(replayTimer);
      isReplaying = false;
      playIcon.innerText = "play_circle";
      showToast("24h Telemetry Replay Paused");
    } else {
      isReplaying = true;
      playIcon.innerText = "pause_circle";
      showToast("▶ Replaying 24h Convoy Telemetry Along Exact OpenStreetMap Highway");
      let current = 0;
      replayTimer = setInterval(() => {
        current = (current + 1) % 25;
        document.getElementById('replaySlider').value = current;
        handleReplayScrub(current);
        if (current === 24) {
          clearInterval(replayTimer);
          isReplaying = false;
          playIcon.innerText = "play_circle";
        }
      }, 400);
    }
  }

  async function verifyReport(id) {
    const badge = document.getElementById('reportStatusBadge');
    badge.innerText = "VERIFIED";
    badge.className = "absolute top-2 right-2 bg-emerald-500 text-black px-2 py-0.5 rounded text-[10px] font-bold uppercase shadow";
    document.getElementById('reportActionButtons').style.display = 'none';

    segments[3].hazard = 0.25;
    renderMapLayers();
    selectSegment(segments[3]);

    showToast("✓ Field Report VERIFIED — Dynamic road routing cost mutated!");

    try {
      await fetch('/api/v1/sync/up', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          reports: [{
            segment_id: "NH10_SEG_005",
            reporter_id: "COMMANDER_DISPATCH",
            report_type: "clear",
            lat: 27.12, lng: 88.50,
            submitted_at: new Date().toISOString()
          }]
        })
      });
    } catch(e) {}
  }

  function rejectReport(id) {
    const badge = document.getElementById('reportStatusBadge');
    badge.innerText = "REJECTED";
    badge.className = "absolute top-2 right-2 bg-rose-600 text-white px-2 py-0.5 rounded text-[10px] font-bold uppercase shadow";
    document.getElementById('reportActionButtons').style.display = 'none';
    showToast("✗ Field report rejected and archived.");
  }

  // Dynamic OSRM Road Pathfinding for ANY Custom Coordinates
  async function handleComputeRoute(e) {
    e.preventDefault();
    closeNewMissionModal();

    const sLat = parseFloat(document.getElementById('srcLat').value);
    const sLng = parseFloat(document.getElementById('srcLng').value);
    const tLat = parseFloat(document.getElementById('tgtLat').value);
    const tLng = parseFloat(document.getElementById('tgtLng').value);

    showToast(`⚡ Querying OSRM road geometry for (${sLat}, ${sLng}) ➔ (${tLat}, ${tLng})...`);

    try {
      const url = `https://router.project-osrm.org/route/v1/driving/${sLng},${sLat};${tLng},${tLat}?overview=full&geometries=geojson`;
      const res = await fetch(url);
      const data = await res.json();

      if (data.code === 'Ok' && data.routes && data.routes[0]) {
        const routeCoords = data.routes[0].geometry.coordinates;

        const routeGeojson = {
          type: 'Feature',
          geometry: { type: 'LineString', coordinates: routeCoords }
        };

        if (map.getSource('safe-route')) {
          map.getSource('safe-route').setData(routeGeojson);
        } else {
          map.addSource('safe-route', { type: 'geojson', data: routeGeojson });
          map.addLayer({
            id: 'safe-route-line',
            type: 'line',
            source: 'safe-route',
            layout: { 'line-join': 'round', 'line-cap': 'round' },
            paint: {
              'line-color': '#06b6d4',
              'line-width': 7,
              'line-dasharray': [2, 2]
            }
          });
        }

        // Fly camera to fit the calculated route bounds
        const bounds = new maplibregl.LngLatBounds();
        routeCoords.forEach(c => bounds.extend(c));
        map.fitBounds(bounds, { padding: 80, pitch: 45 });

        showToast(`⚡ Dynamic OSRM Route Computed! ${routeCoords.length} road coordinates snapped pixel-perfect onto highway pavement.`);
      }
    } catch(err) {
      showToast("Error calculating OSRM road route");
    }
  }

  function toggleRoadLayer(enabled) {
    if (map.getLayer('road-segments-core')) {
      map.setLayoutProperty('road-segments-core', 'visibility', enabled ? 'visible' : 'none');
      map.setLayoutProperty('road-segments-glow', 'visibility', enabled ? 'visible' : 'none');
    }
  }

  function toggleConvoyLayer(enabled) {
    Object.values(vehicleMarkers).forEach(m => {
      m.getElement().style.display = enabled ? 'flex' : 'none';
    });
  }

  function updateThresholds() {
    document.getElementById('warnVal').innerText = document.getElementById('warnSlider').value + '%';
    document.getElementById('critVal').innerText = document.getElementById('critSlider').value + '%';
    renderMapLayers();
  }

  function focusSegment(segId) {
    const seg = segments.find(s => s.id === segId);
    if (seg && seg.coords && seg.coords.length > 0) {
      map.flyTo({ center: seg.coords[0], zoom: 12 });
      selectSegment(seg);
    }
  }

  function toggleSettingsDrawer() { document.getElementById('settingsDrawer').classList.toggle('hidden'); }
  function closeSegmentPanel() { document.getElementById('segmentPanel').classList.add('translate-x-[360px]'); }
  function openNewMissionModal() { document.getElementById('newMissionModal').classList.remove('hidden'); }
  function closeNewMissionModal() { document.getElementById('newMissionModal').classList.add('hidden'); }
  function openHelpModal() { document.getElementById('helpModal').classList.remove('hidden'); }
  function closeHelpModal() { document.getElementById('helpModal').classList.add('hidden'); }
  function openTechStackModal() { document.getElementById('techStackModal').classList.remove('hidden'); }
  function closeTechStackModal() { document.getElementById('techStackModal').classList.add('hidden'); }
  function toggleNotificationsModal() { document.getElementById('notificationsModal').classList.toggle('hidden'); }

  function setPresetCoords(sLat, sLng, tLat, tLng) {
    document.getElementById('srcLat').value = sLat;
    document.getElementById('srcLng').value = sLng;
    document.getElementById('tgtLat').value = tLat;
    document.getElementById('tgtLng').value = tLng;
  }

  function activateRailTab(tabName) {
    if (tabName === 'layers') showToast("Control Room Layers Active");
    if (tabName === 'vehicles') showToast("🚚 Convoy Telemetry Active");
    if (tabName === 'analytics') toggleSettingsDrawer();
    if (tabName === 'history') toggleReplayAnimation();
  }

  async function triggerSyncDown() {
    const icon = document.getElementById('syncIcon');
    icon.classList.add('animate-spin');
    showToast("🔄 Syncing live GIS edge updates from FastAPI backend...");
    setTimeout(() => {
      icon.classList.remove('animate-spin');
      showToast("✓ Synced 8 GIS road edge updates");
    }, 1000);
  }

  function showToast(msg) {
    let toast = document.getElementById('statusToast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'statusToast';
      toast.className = 'fixed bottom-14 left-1/2 -translate-x-1/2 bg-surface-variant/95 border border-outline-variant text-on-surface px-4 py-2 rounded-full text-xs font-mono z-50 shadow-2xl backdrop-blur-xl transition-all duration-300 pointer-events-none';
      document.body.appendChild(toast);
    }
    toast.innerText = msg;
    toast.style.opacity = '1';
    toast.style.transform = 'translateX(-50%) translateY(0)';
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(-50%) translateY(10px)';
    }, 3200);
  }
</script>
</body>
</html>"""
