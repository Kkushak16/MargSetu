/**
 * Dashboard Settings Drawer/Panel Component (Member C - Prompt 1b)
 * SIH26002 - MargSetu: Smart Logistics & Accessibility Platform
 */

import React from 'react';
import { useDashboardSettings } from '../context/DashboardSettingsContext';

export const DashboardSettingsPanel: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose }) => {
  const {
    layers,
    toggleLayer,
    timeHour,
    setTimeHour,
    warningThreshold,
    setWarningThreshold,
    criticalThreshold,
    setCriticalThreshold,
    units,
    setUnits,
    language,
    setLanguage,
    theme,
    setTheme,
    lastSyncedTimestamp
  } = useDashboardSettings();

  if (!isOpen) return null;

  const isHindi = language === 'hi';

  return (
    <div style={{
      position: 'fixed',
      top: '65px',
      right: '16px',
      width: '320px',
      backgroundColor: theme === 'dark' ? '#1e293b' : '#ffffff',
      color: theme === 'dark' ? '#f8fafc' : '#0f172a',
      border: '1px solid #334155',
      borderRadius: '12px',
      padding: '18px',
      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)',
      zIndex: 2000,
      display: 'flex',
      flexDirection: 'column',
      gap: '16px',
      fontSize: '0.85rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #334155', paddingBottom: '10px' }}>
        <strong style={{ fontSize: '1rem', color: '#38bdf8' }}>
          ⚙️ {isHindi ? 'डैशबोर्ड सेटिंग्स' : 'Control Room Settings'}
        </strong>
        <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '1.2rem' }}>×</button>
      </div>

      {/* 1. Layer Visibility Toggles */}
      <div>
        <strong style={{ color: '#cbd5e1', display: 'block', marginBottom: '6px' }}>
          🗺️ {isHindi ? 'मानचित्र परतें' : 'Active Map Layers'}
        </strong>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '6px' }}>
          <label style={{ display: 'flex', gap: '8px', cursor: 'pointer' }}>
            <input type="checkbox" checked={layers.roads} onChange={() => toggleLayer('roads')} />
            {isHindi ? 'सड़क नेटवर्क (Roads)' : 'Road Graph & Hazard Costs'}
          </label>
          <label style={{ display: 'flex', gap: '8px', cursor: 'pointer' }}>
            <input type="checkbox" checked={layers.vehicles} onChange={() => toggleLayer('vehicles')} />
            {isHindi ? 'वाहन ट्रैकिंग (Vehicles)' : 'Live Vehicle Telemetry'}
          </label>
          <label style={{ display: 'flex', gap: '8px', cursor: 'pointer' }}>
            <input type="checkbox" checked={layers.crowdsourceReports} onChange={() => toggleLayer('crowdsourceReports')} />
            {isHindi ? 'फील्ड रिपोर्ट (Reports)' : 'Crowdsourced Field Alerts'}
          </label>
          <label style={{ display: 'flex', gap: '8px', cursor: 'pointer' }}>
            <input type="checkbox" checked={layers.rainfallOverlay} onChange={() => toggleLayer('rainfallOverlay')} />
            {isHindi ? 'वर्षा संचय (Rainfall ARI)' : 'Rainfall & Wetness Overlay'}
          </label>
        </div>
      </div>

      {/* 2. 24h Time Scrubbing Slider */}
      <div style={{ borderTop: '1px solid #334155', paddingTop: '10px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
          <strong>🕒 {isHindi ? 'समय रिप्ले (Past 24h)' : '24h Historical Demo Replay'}</strong>
          <span style={{ color: '#38bdf8', fontWeight: 700 }}>T - {24 - timeHour}h</span>
        </div>
        <input
          type="range"
          min="0"
          max="24"
          value={timeHour}
          onChange={e => setTimeHour(parseInt(e.target.value))}
          style={{ width: '100%' }}
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.7rem', color: '#94a3b8' }}>
          <span>-24 Hours</span>
          <span>Now (Live)</span>
        </div>
      </div>

      {/* 3. Dynamic Live Threshold Sliders */}
      <div style={{ borderTop: '1px solid #334155', paddingTop: '10px' }}>
        <strong style={{ display: 'block', marginBottom: '8px' }}>
          🎛️ {isHindi ? 'जोखिम सीमा (Cutoff Thresholds)' : 'Live Cutoff Thresholds'}
        </strong>
        <div style={{ marginBottom: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#f59e0b' }}>
            <span>{isHindi ? 'चेतावनी सीमा (Warning)' : 'WARNING Threshold:'}</span>
            <strong>{(warningThreshold * 100).toFixed(0)}%</strong>
          </div>
          <input
            type="range"
            min="0.10"
            max="0.50"
            step="0.05"
            value={warningThreshold}
            onChange={e => setWarningThreshold(parseFloat(e.target.value))}
            style={{ width: '100%' }}
          />
        </div>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#ef4444' }}>
            <span>{isHindi ? 'अवरोध सीमा (Critical Cutoff)' : 'CRITICAL Cutoff:'}</span>
            <strong>{(criticalThreshold * 100).toFixed(0)}%</strong>
          </div>
          <input
            type="range"
            min="0.50"
            max="0.90"
            step="0.05"
            value={criticalThreshold}
            onChange={e => setCriticalThreshold(parseFloat(e.target.value))}
            style={{ width: '100%' }}
          />
        </div>
      </div>

      {/* 4. Units & Language Toggle */}
      <div style={{ borderTop: '1px solid #334155', paddingTop: '10px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
        <div>
          <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Distance Unit</label>
          <select value={units} onChange={e => setUnits(e.target.value as any)} style={selectStyle}>
            <option value="km">Kilometers (km)</option>
            <option value="mi">Miles (mi)</option>
          </select>
        </div>
        <div>
          <label style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Language</label>
          <select value={language} onChange={e => setLanguage(e.target.value as any)} style={selectStyle}>
            <option value="en">English</option>
            <option value="hi">हिंदी (Hindi)</option>
          </select>
        </div>
      </div>

      {/* 5. Theme & Sync Badge */}
      <div style={{ borderTop: '1px solid #334155', paddingTop: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <button
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          style={{ backgroundColor: '#334155', color: '#fff', border: 'none', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer' }}
        >
          {theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
        <span style={{ fontSize: '0.7rem', color: '#10b981' }}>
          Sync: {lastSyncedTimestamp}
        </span>
      </div>
    </div>
  );
};

const selectStyle: React.CSSProperties = {
  width: '100%',
  backgroundColor: '#0f172a',
  border: '1px solid #334155',
  borderRadius: '6px',
  padding: '6px',
  color: '#fff',
  fontSize: '0.8rem',
  marginTop: '4px'
};
