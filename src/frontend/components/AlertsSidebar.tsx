/**
 * Timestamped Disaster & Hazard Alerts Log Sidebar Component
 * SIH26002 - MargSetu: Smart Logistics & Accessibility Platform
 * 
 * Displays real-time disaster alerts, blockage warnings, and high-risk events.
 */

import React from 'react';
import { useDashboardSettings } from '../context/DashboardSettingsContext';

export interface DisasterAlertItem {
  id: string;
  severity: 'CRITICAL' | 'WARNING' | 'INFO';
  title: string;
  location: string;
  timestamp: string;
  details: string;
}

export const AlertsSidebar: React.FC<{ alerts: DisasterAlertItem[] }> = ({ alerts }) => {
  const { language, theme } = useDashboardSettings();
  const isHindi = language === 'hi';

  const getSeverityBadge = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return <span style={{ backgroundColor: '#ef4444', color: '#fff', fontSize: '0.65rem', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>🚨 CRITICAL</span>;
      case 'WARNING':
        return <span style={{ backgroundColor: '#f59e0b', color: '#000', fontSize: '0.65rem', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>⚠️ WARNING</span>;
      default:
        return <span style={{ backgroundColor: '#0284c7', color: '#fff', fontSize: '0.65rem', padding: '2px 6px', borderRadius: '4px', fontWeight: 700 }}>ℹ️ INFO</span>;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <h3 style={{ margin: 0, fontSize: '0.95rem', color: '#f43f5e', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>📢 {isHindi ? 'आपदा एवं ब्लॉक अलर्ट' : 'Real-Time Disaster Alerts'}</span>
        <span style={{ fontSize: '0.75rem', backgroundColor: '#881337', color: '#fda4af', padding: '2px 8px', borderRadius: '10px' }}>
          {alerts.length} Active
        </span>
      </h3>

      {alerts.map(alert => (
        <div
          key={alert.id}
          style={{
            backgroundColor: alert.severity === 'CRITICAL' ? (theme === 'dark' ? '#450a0a' : '#fef2f2') : (theme === 'dark' ? '#0f172a' : '#f8fafc'),
            border: alert.severity === 'CRITICAL' ? '1px solid #ef4444' : '1px solid #334155',
            borderRadius: '8px',
            padding: '10px',
            fontSize: '0.8rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '4px'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <strong style={{ color: theme === 'dark' ? '#f8fafc' : '#0f172a' }}>{alert.title}</strong>
            {getSeverityBadge(alert.severity)}
          </div>
          
          <div style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
            📍 {alert.location} • <time>{alert.timestamp}</time>
          </div>

          <p style={{ margin: '4px 0 0 0', fontSize: '0.78rem', color: theme === 'dark' ? '#cbd5e1' : '#334155', lineHeight: '1.3' }}>
            {alert.details}
          </p>
        </div>
      ))}
    </div>
  );
};
