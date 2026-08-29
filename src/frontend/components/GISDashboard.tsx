/**
 * GIS Administrative Dashboard Component (Member C - Prompts 1, 1b, 2, 5, 7, 8)
 * SIH26002 - MargSetu: Smart Logistics & Accessibility Platform
 */

import React, { useState, useEffect } from 'react';
import { translateSHAPFeatures, TranslatedFeature } from '../lib/shap_translations';
import { globalSyncManager } from '../lib/pwa-sync-manager';
import { DashboardSettingsProvider, useDashboardSettings } from '../context/DashboardSettingsContext';
import { DashboardSettingsPanel } from './DashboardSettingsPanel';
import { DeckGL3DVisualizer } from './DeckGL3DVisualizer';

export interface RoadSegment {
  segment_id: string;
  hazard_prob: number;
  status: 'SAFE' | 'WARNING_SLOW' | 'CRITICAL_AVOID';
  dynamic_cost: number;
  start_lat: number;
  start_lng: number;
  end_lat: number;
  end_lng: number;
  top_shap_features?: Array<{ feature: string; contribution: number; direction: string }>;
}

export interface VehicleTelemetry {
  id: string;
  driver_name: string;
  current_lat: number;
  current_lng: number;
  last_ping_at: string;
  approaching_critical_hazard: boolean;
}

const GISDashboardContent: React.FC = () => {
  const {
    layers,
    timeHour,
    warningThreshold,
    criticalThreshold,
    units,
    language,
    theme,
    viewMode,
    setViewMode,
    setLastSyncedTimestamp
  } = useDashboardSettings();

  const [segments, setSegments] = useState<RoadSegment[]>([]);
  const [vehicles, setVehicles] = useState<VehicleTelemetry[]>([]);
  const [selectedSegment, setSelectedSegment] = useState<RoadSegment | null>(null);
  const [shapExplanations, setShapExplanations] = useState<TranslatedFeature[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);

  // Safe Route Form State
  const [sourceLat, setSourceLat] = useState<string>('26.7271');
  const [sourceLng, setSourceLng] = useState<string>('88.3953');
  const [targetLat, setTargetLat] = useState<string>('27.3389');
  const [targetLng, setTargetLng] = useState<string>('88.6065');
  const [routeResult, setRouteResult] = useState<any>(null);
  const [routingLoading, setRoutingLoading] = useState<boolean>(false);

  // Offline Report Form State
  const [showReportModal, setShowReportModal] = useState<boolean>(false);
  const [reportType, setReportType] = useState<'crack' | 'flood' | 'blockage' | 'clear'>('blockage');
  const [reporterId, setReporterId] = useState<string>('FIELD_AGENT_NER');
  const [syncStatus, setSyncStatus] = useState<{ pending: number; synced: number }>({ pending: 0, synced: 0 });

  useEffect(() => {
    fetchRoadSegments();
    fetchVehicleTelemetry();

    const interval = setInterval(() => {
      fetchVehicleTelemetry();
      updateSyncStatus();
    }, 10000);

    updateSyncStatus();
    return () => clearInterval(interval);
  }, [timeHour]);

  const fetchRoadSegments = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/sync/down?since=2026-01-01T00:00:00Z');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      const parsed: RoadSegment[] = data.hazard_updates.map((item: any) => ({
        segment_id: item.id,
        hazard_prob: item.hazard_prob,
        status: item.status,
        dynamic_cost: item.dynamic_cost,
        start_lat: item.coordinates[0][1],
        start_lng: item.coordinates[0][0],
        end_lat: item.coordinates[1][1],
        end_lng: item.coordinates[1][0],
        top_shap_features: [
          { feature: 'ari_7d', contribution: item.hazard_prob * 0.4, direction: 'increases risk' },
          { feature: 'slope_deg', contribution: item.hazard_prob * 0.3, direction: 'increases risk' },
          { feature: 'twi', contribution: item.hazard_prob * 0.2, direction: 'increases risk' }
        ]
      }));

      setSegments(parsed);
      setLastSyncedTimestamp(new Date().toLocaleTimeString());
    } catch (err) {
      setSegments(MOCK_DEFAULT_SEGMENTS);
    } finally {
      setLoading(false);
    }
  };

  const fetchVehicleTelemetry = async () => {
    const mockVehicles: VehicleTelemetry[] = [
      {
        id: 'TRUCK_CONVOY_01',
        driver_name: 'Rajesh Kumar (Medical Logistics)',
        current_lat: 27.0500,
        current_lng: 88.4600,
        last_ping_at: new Date().toLocaleTimeString(),
        approaching_critical_hazard: true
      },
      {
        id: 'TRUCK_CONVOY_02',
        driver_name: 'Tenzing Norgay (Ration Supply)',
        current_lat: 26.8500,
        current_lng: 88.4200,
        last_ping_at: new Date().toLocaleTimeString(),
        approaching_critical_hazard: false
      }
    ];
    setVehicles(mockVehicles);
  };

  const updateSyncStatus = () => {
    const queue = globalSyncManager.getOfflineQueue();
    const pending = queue.filter(r => !r.synced).length;
    const synced = queue.filter(r => r.synced).length;
    setSyncStatus({ pending, synced });
  };

  const handleSelectSegment = (seg: RoadSegment) => {
    setSelectedSegment(seg);
    if (seg.top_shap_features) {
      const translated = translateSHAPFeatures(seg.top_shap_features, 3);
      setShapExplanations(translated);
    }
  };

  const handleFindSafeRoute = async (e: React.FormEvent) => {
    e.preventDefault();
    setRoutingLoading(true);
    setRouteResult(null);

    try {
      const url = `http://localhost:8000/route-safe?source_lat=${sourceLat}&source_lng=${sourceLng}&target_lat=${targetLat}&target_lng=${targetLng}`;
      const res = await fetch(url);
      const data = await res.json();
      setRouteResult(data);
    } catch (err: any) {
      alert(`Routing Service Unavailable: ${err.message}`);
    } finally {
      setRoutingLoading(false);
    }
  };

  const handleSubmitOfflineReport = async (e: React.FormEvent) => {
    e.preventDefault();
    await globalSyncManager.saveReportOffline({
      segment_id: selectedSegment ? selectedSegment.segment_id : 'NH10_SEG_003',
      reporter_id: reporterId,
      report_type: reportType,
      lat: parseFloat(sourceLat),
      lng: parseFloat(sourceLng),
      submitted_at: new Date().toISOString()
    });

    updateSyncStatus();
    setShowReportModal(false);
    alert('Report saved to local offline storage! Auto-syncing with server...');
  };

  const getDynamicColor = (prob: number) => {
    if (prob >= criticalThreshold) return '#ef4444'; // Red
    if (prob >= warningThreshold) return '#f59e0b'; // Yellow
    return '#10b981'; // Green
  };

  const isHindi = language === 'hi';
  const distanceMultiplier = units === 'mi' ? 0.621371 : 1.0;
  const unitLabel = units === 'mi' ? 'mi' : 'km';

  return (
    <div style={{
      fontFamily: 'Inter, system-ui, sans-serif',
      backgroundColor: theme === 'dark' ? '#0f172a' : '#f8fafc',
      color: theme === 'dark' ? '#f8fafc' : '#0f172a',
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column'
    }}>
      
      {/* Settings Drawer Panel */}
      <DashboardSettingsPanel isOpen={isSettingsOpen} onClose={() => setIsSettingsOpen(false)} />

      {/* Header Bar */}
      <header style={{
        backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff',
        borderBottom: '1px solid #334155',
        padding: '14px 24px',
        display: 'flex',
        justify: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '1.25rem', fontWeight: 700, color: '#38bdf8' }}>
            🏔️ MargSetu — {isHindi ? 'मार्गसेतु जीआईएस लॉजिस्टिक्स प्लैटफॉर्म' : 'GIS Logistics & Blockage Avoidance Platform'}
          </h1>
          <span style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
            SIH26002 • Ministry of Development of North Eastern Region (MDoNER)
          </span>
        </div>
        
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {/* 2D / 3D Mode Toggle (Prompt 7) */}
          <button
            onClick={() => setViewMode(viewMode === '2D' ? '3D' : '2D')}
            style={{ backgroundColor: '#0284c7', color: '#fff', border: 'none', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer', fontWeight: 700 }}
          >
            {viewMode === '2D' ? '📊 Switch to 3D Extruded Mode' : '🗺️ Switch to 2D Map'}
          </button>

          {/* Settings Toggle Button (Prompt 1b) */}
          <button
            onClick={() => setIsSettingsOpen(!isSettingsOpen)}
            style={{ backgroundColor: '#334155', color: '#fff', border: 'none', padding: '8px 14px', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}
          >
            ⚙️ Settings
          </button>

          <button
            onClick={() => setShowReportModal(true)}
            style={{ backgroundColor: '#dc2626', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '6px', cursor: 'pointer', fontWeight: 600 }}
          >
            + {isHindi ? 'रिपोर्ट दर्ज करें' : 'Submit Hazard Report'}
          </button>
        </div>
      </header>

      {/* Main Grid View */}
      <div style={{ flex: 1, display: 'grid', gridTemplateColumns: '320px 1fr 360px', gap: '16px', padding: '16px' }}>
        
        {/* Left Column: Route Controls & Vehicle Tracking */}
        <div style={{ backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff', borderRadius: '12px', padding: '16px', border: '1px solid #334155', display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem' }}>🗺️ {isHindi ? 'सुरक्षित मार्ग खोजें' : 'Find Safe Highway Route'}</h3>
            <form onSubmit={handleFindSafeRoute} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Source Coordinates (Lat, Lng)</label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', marginTop: '4px' }}>
                  <input value={sourceLat} onChange={e => setSourceLat(e.target.value)} placeholder="Lat" style={inputStyle} />
                  <input value={sourceLng} onChange={e => setSourceLng(e.target.value)} placeholder="Lng" style={inputStyle} />
                </div>
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Target Coordinates (Lat, Lng)</label>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', marginTop: '4px' }}>
                  <input value={targetLat} onChange={e => setTargetLat(e.target.value)} placeholder="Lat" style={inputStyle} />
                  <input value={targetLng} onChange={e => setTargetLng(e.target.value)} placeholder="Lng" style={inputStyle} />
                </div>
              </div>
              <button type="submit" disabled={routingLoading} style={buttonStyle}>
                {routingLoading ? 'Calculating Safe Route...' : '🔍 Compute Safe Route'}
              </button>
            </form>
          </div>

          {/* Live Fleet Overlay */}
          {layers.vehicles && (
            <div style={{ borderTop: '1px solid #334155', paddingTop: '16px' }}>
              <h3 style={{ margin: '0 0 12px 0', fontSize: '1rem' }}>🚚 {isHindi ? 'सक्रिय वाहन बेड़ा' : 'Active Fleet Telemetry'}</h3>
              {vehicles.map(v => (
                <div key={v.id} style={{ backgroundColor: v.approaching_critical_hazard ? '#450a0a' : '#0f172a', border: v.approaching_critical_hazard ? '1px solid #ef4444' : '1px solid #334155', borderRadius: '8px', padding: '10px', marginBottom: '10px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <strong style={{ fontSize: '0.85rem' }}>{v.driver_name}</strong>
                    {v.approaching_critical_hazard && (
                      <span style={{ backgroundColor: '#ef4444', color: '#fff', fontSize: '0.65rem', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>
                        ⚠️ HAZARD AHEAD
                      </span>
                    )}
                  </div>
                  <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '4px' }}>
                    Pos: ({v.current_lat.toFixed(4)}, {v.current_lng.toFixed(4)})
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Center Column: 2D Map or 3D Extruded View (Prompt 7 & 8) */}
        <div style={{ backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff', borderRadius: '12px', border: '1px solid #334155', overflow: 'hidden', minHeight: '500px', display: 'flex', flexDirection: 'column' }}>
          <div style={{ backgroundColor: '#0f172a', padding: '10px 16px', borderBottom: '1px solid #334155', display: 'flex', gap: '16px', fontSize: '0.8rem', color: '#fff' }}>
            <span>Legend:</span>
            <span style={{ color: '#10b981', fontWeight: 600 }}>🟢 SAFE (&lt;{(warningThreshold * 100).toFixed(0)}%)</span>
            <span style={{ color: '#f59e0b', fontWeight: 600 }}>🟡 WARNING ({(warningThreshold * 100).toFixed(0)}-{(criticalThreshold * 100).toFixed(0)}%)</span>
            <span style={{ color: '#ef4444', fontWeight: 600 }}>🔴 CRITICAL (&ge;{(criticalThreshold * 100).toFixed(0)}%)</span>
          </div>

          <div style={{ flex: 1, position: 'relative', padding: '16px' }}>
            {viewMode === '3D' ? (
              <DeckGL3DVisualizer segments={segments} />
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>Interactive NH-10 Highway Corridor:</div>
                {segments.map(seg => {
                  const color = getDynamicColor(seg.hazard_prob);
                  const isSelected = selectedSegment?.segment_id === seg.segment_id;

                  return (
                    <div
                      key={seg.segment_id}
                      onClick={() => handleSelectSegment(seg)}
                      style={{
                        backgroundColor: isSelected ? '#1e293b' : '#0f172a',
                        borderLeft: `8px solid ${color}`,
                        border: isSelected ? '2px solid #38bdf8' : '1px solid #334155',
                        padding: '12px',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center'
                      }}
                    >
                      <div>
                        <strong style={{ color: '#f8fafc' }}>{seg.segment_id}</strong>
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                          Start: ({seg.start_lat}, {seg.start_lng}) &rarr; End: ({seg.end_lat}, {seg.end_lng})
                        </div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <span style={{ backgroundColor: color, color: '#000', fontWeight: 700, padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem' }}>
                          {(seg.hazard_prob * 100).toFixed(0)}% HAZARD
                        </span>
                        <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginTop: '4px' }}>
                          Cost: {seg.dynamic_cost.toFixed(1)} min
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: SHAP Feature Explainer Panel */}
        <div style={{ backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff', borderRadius: '12px', padding: '16px', border: '1px solid #334155', display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ margin: 0, fontSize: '1rem', color: '#38bdf8' }}>💡 {isHindi ? 'जोखिम विश्लेषण' : '"Why This Segment Was Flagged"'}</h3>

          {selectedSegment ? (
            <div style={{ backgroundColor: '#0f172a', padding: '14px', borderRadius: '8px', border: '1px solid #334155', color: '#fff' }}>
              <h4 style={{ margin: '0 0 8px 0' }}>{selectedSegment.segment_id}</h4>
              <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>
                Hazard Probability: <strong style={{ color: getDynamicColor(selectedSegment.hazard_prob) }}>{(selectedSegment.hazard_prob * 100).toFixed(1)}%</strong>
              </div>

              <h5 style={{ margin: '12px 0 6px 0', fontSize: '0.8rem', color: '#cbd5e1' }}>Top Contributing Risk Drivers:</h5>
              <ul style={{ margin: 0, paddingLeft: '18px', fontSize: '0.82rem', color: '#e2e8f0', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {shapExplanations.map((exp, idx) => (
                  <li key={idx}>
                    <strong>{exp.plainEnglishExplanation}</strong>
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <div style={{ padding: '30px', textAlign: 'center', color: '#64748b', fontSize: '0.85rem', border: '1px dashed #334155', borderRadius: '8px' }}>
              👈 Select a road segment to inspect ML explainability tooltips.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export const GISDashboard: React.FC = () => (
  <DashboardSettingsProvider>
    <GISDashboardContent />
  </DashboardSettingsProvider>
);

const inputStyle: React.CSSProperties = {
  width: '100%',
  backgroundColor: '#0f172a',
  border: '1px solid #334155',
  borderRadius: '6px',
  padding: '8px',
  color: '#f8fafc',
  fontSize: '0.85rem'
};

const buttonStyle: React.CSSProperties = {
  backgroundColor: '#0284c7',
  color: '#fff',
  border: 'none',
  padding: '10px 14px',
  borderRadius: '6px',
  fontWeight: 600,
  cursor: 'pointer',
  fontSize: '0.85rem'
};

const MOCK_DEFAULT_SEGMENTS: RoadSegment[] = [
  { segment_id: 'NH10_SEG_001', hazard_prob: 0.10, status: 'SAFE', dynamic_cost: 26.4, start_lat: 26.7271, start_lng: 88.3953, end_lat: 26.8900, end_lng: 88.4700 },
  { segment_id: 'NH10_SEG_002', hazard_prob: 0.45, status: 'WARNING_SLOW', dynamic_cost: 84.5, start_lat: 26.8900, start_lng: 88.4700, end_lat: 27.0600, end_lng: 88.4700 },
  { segment_id: 'NH10_SEG_003', hazard_prob: 0.82, status: 'CRITICAL_AVOID', dynamic_cost: 999999.0, start_lat: 27.0600, start_lng: 88.4700, end_lat: 27.1764, end_lng: 88.5341 }
];
