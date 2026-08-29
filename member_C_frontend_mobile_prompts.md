# Prompts for Member C — Frontend / Mobile & Offline Engineer

Constraint baked into every prompt below: keep bundle size and dependencies light — **Leaflet over Mapbox GL** unless you already have a free API key, and the field app must work with **zero network connectivity**.

**Theme decision:** dark mode default, blue-teal accent, high-contrast control-room style (hazard colors pop harder on dark, reads as serious govt/infra tool). Light mode toggle kept as fallback. No gradients/glassmorphism — map is the hero, chrome stays flat.

---

### Prompt 1 — Admin GIS dashboard skeleton

```
Build a Next.js page using react-leaflet that:
1. Renders a map centered on [district name, NER coordinates].
2. Fetches GeoJSON road segments from GET /api/v1/road-edges and draws
   them as colored polylines: green if hazard_probability < 0.35,
   yellow if 0.35-0.70, red if >= 0.70.
3. On clicking a segment, opens a side panel showing hazard_probability,
   last_updated, and (if present) the top_shap_features explanation from
   the ML API, in plain English, e.g. "High risk mainly due to heavy
   rainfall in the last 7 days."
4. Has a "Find Safe Route" form (source/destination lat-lng or click-to-
   pick on map) that calls GET /route-safe and draws the returned route
   as a highlighted blue line on top of the hazard-colored segments.

Use Tailwind for styling, keep it a single page for the hackathon demo,
and add loading/error states for all API calls. Theme: dark mode default
(slate/near-black basemap, blue-teal UI accents, white text), with a
light-mode toggle in the top bar.
```

---

### Prompt 1b — Dashboard settings panel

```
Add a settings panel (collapsible sidebar or top-bar dropdown) to the
dashboard from Prompt 1 with:
1. Layer toggles: roads / vehicles / crowdsource reports / rainfall overlay
   (checkboxes, persisted in localStorage).
2. Time slider — scrub hazard_probability state across past 24h using
   cached hourly snapshots from the API, for demo replay.
3. Threshold sliders — let user adjust WARNING_SLOW (default 0.35) and
   CRITICAL_AVOID (default 0.70) cutoffs live; re-color the map
   immediately without a new API call (recompute color client-side from
   the already-fetched hazard_probability values).
4. Units toggle (km/miles) and language toggle (English/Hindi labels).
5. Dark/light mode toggle.
6. A small sync-status badge showing "Field app data last synced: [time]"
   pulled from the backend's most recent /sync/up timestamp.

Keep all settings in a single React context so any component can read
them without prop drilling.
```

---

### Prompt 2 — Live vehicle tracking overlay

```
Add a layer to the dashboard from Prompt 1 that polls GET /vehicles
every 10 seconds and shows truck icons at their current_lat/lng,
with a tooltip showing driver_name and time since last ping. If a
vehicle is heading toward a segment with hazard_probability >= 0.70,
show a pulsing red warning badge on its icon.
```

---

### Prompt 3 — Field app shell (Flutter)

```
Scaffold a Flutter app with three screens:
1. Map screen — shows the same hazard-colored road overlay (fetch once,
   cache locally as GeoJSON in a local file/sqlite for offline viewing).
2. Report screen — a form to submit a hazard report: photo (camera or
   gallery), report_type dropdown (crack/flood/blockage/clear), and
   auto-captured GPS lat/lng. On submit, always save to local SQLite
   first (never depend on network), and generate a client-side UUID for
   the report.
3. Sync status screen — shows how many reports are pending upload vs
   synced, with a manual "Sync Now" button.

Use the `connectivity_plus` and `sqflite` packages. Keep the UI simple
and legible for outdoor/low-light phone use (large touch targets, high
contrast).
```

---

### Prompt 4 — Offline queue & background sync logic

```
Write the Dart sync-manager class for the Flutter app above that:
1. Listens for connectivity changes via connectivity_plus.
2. When connectivity returns (2G/3G/4G/WiFi), automatically POSTs all
   unsynced local reports as a single batch to /api/v1/sync/up.
3. Marks each report as synced only after receiving a per-item success
   confirmation from the server (handle partial-batch failures — some
   items succeed, some don't).
4. Pulls new hazard data via GET /api/v1/sync/down?since=<last_sync_time>
   and updates the local cached GeoJSON.
5. Is idempotent — running sync twice in a row must not create
   duplicate reports (rely on the client-generated UUID).

Add comments explaining the retry/backoff strategy for flaky rural
connections (short bursts of signal, not sustained connectivity).
```

---

### Prompt 5 — "Why this route" explainer panel

```
Given the top_shap_features array returned by the routing API for each
flagged segment, write a small React component that translates SHAP
feature names into plain-English phrases, e.g.:
  ari_7d high -> "Heavy rainfall over the past week"
  slope_deg high -> "Very steep terrain"
  twi high -> "Water tends to collect here"
Render up to 3 as a bulleted "Why this route avoids this road" list next
to the map. Keep the mapping table easy to extend as Member A adds more
features.
```

---

### Prompt 6 — PWA fallback (if you skip native Flutter for time reasons)

```
Convert the field-report form from Prompt 3 into a installable PWA
(Progressive Web App) using a Next.js/React setup with a Service Worker
and IndexedDB (via the `idb` or `rxdb` library) instead of SQLite. Same
requirements: offline-first submission, background sync when online,
idempotent uploads via client-generated UUID. Explain briefly why RxDB's
built-in replication protocol could replace your custom sync-manager
code if you had more time — useful to mention to judges as a "future
work" line.
```

---

### Prompt 7 — 3D terrain + extruded hazard columns (deck.gl)

```
Add a 3D view mode to the dashboard using deck.gl (TerrainLayer +
ColumnLayer) layered on top of MapLibre/Leaflet:
1. TerrainLayer rendering the DEM for [district name] so valleys/slopes
   are visible as real terrain, not a flat map.
2. ColumnLayer: each road segment rendered as a vertical column at its
   midpoint, height scaled by hazard_probability (0 = flat, max height
   at prob=1.0), color still green/yellow/red. This is the main "wow"
   visual — hazard spikes should be instantly readable from a distance.
3. A 2D/3D toggle button that switches between this view and the flat
   Prompt-1 map — keep 3D for demo/pitch, 2D as the practical daily-use
   default.

Keep it a separate optional component so it doesn't bloat the default
page load — lazy-load deck.gl only when 3D mode is toggled on.
```

---

### Prompt 8 — Animated trucks + fly-through camera (stretch, for pitch video)

```
Extend the 3D view from Prompt 7 with:
1. deck.gl TripsLayer animating truck icons moving along their route
   polyline in real time (interpolate position between GPS pings).
2. A "fly-through" camera preset: on button click, animate the deck.gl
   viewState from a top-down overview down into the demo valley over
   ~4 seconds (ease-in-out), ending centered on the highest-hazard
   segment. Intended purely for the pitch/demo video, not daily use —
   gate it behind a "Cinematic Demo" button, not the default view.

Keep this isolated in its own component so it can be skipped entirely
if we run low on time before the deadline.
```
