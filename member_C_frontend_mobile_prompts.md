# Prompts for Member C — Frontend / Mobile & Offline Engineer

Constraint baked into every prompt below: keep bundle size and dependencies light — **Leaflet over Mapbox GL** unless you already have a free API key, and the field app must work with **zero network connectivity**.

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
and add loading/error states for all API calls.
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
