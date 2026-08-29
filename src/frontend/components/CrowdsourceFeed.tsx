/**
 * Crowdsource Field Report Moderation Feed Component
 * SIH26002 - MargSetu: Smart Logistics & Accessibility Platform
 * 
 * Displays incoming field photo reports with GPS coordinates, report types,
 * and Verify / Reject controls for control-room GIS operators.
 */

import React, { useState } from 'react';
import { useDashboardSettings } from '../context/DashboardSettingsContext';

export interface FieldReportItem {
  id: string;
  segment_id: string;
  reporter_id: string;
  report_type: 'blockage' | 'flood' | 'crack' | 'clear';
  lat: number;
  lng: number;
  submitted_at: string;
  status: 'PENDING' | 'VERIFIED' | 'REJECTED';
  photo_url?: string;
}

export const CrowdsourceFeed: React.FC<{
  reports: FieldReportItem[];
  onVerify: (id: string) => void;
  onReject: (id: string) => void;
}> = ({ reports, onVerify, onReject }) => {
  const { language, theme } = useDashboardSettings();
  const isHindi = language === 'hi';

  const getTypeLabel = (type: string) => {
    switch (type) {
      case 'blockage': return isHindi ? '🚧 पूर्ण अवरोध' : '🚧 Road Blockage';
      case 'flood': return isHindi ? '🌊 जलभराव / भूस्खलन' : '🌊 Flash Flood / Mudslide';
      case 'crack': return isHindi ? '⚡ दरार / चट्टान गिरना' : '⚡ Road Fissure / Rockfall';
      case 'clear': return isHindi ? '✅ मार्ग साफ़' : '✅ Road Clear';
      default: return type;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
      <h3 style={{ margin: 0, fontSize: '0.95rem', color: '#38bdf8', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span>📸 {isHindi ? 'फील्ड रिपोर्ट फ़ीड' : 'Crowdsource Verification Feed'}</span>
        <span style={{ fontSize: '0.75rem', backgroundColor: '#0284c7', color: '#fff', padding: '2px 8px', borderRadius: '10px' }}>
          {reports.filter(r => r.status === 'PENDING').length} Pending
        </span>
      </h3>

      {reports.length === 0 ? (
        <div style={{ fontSize: '0.8rem', color: '#94a3b8', textAlign: 'center', padding: '16px', border: '1px dashed #334155', borderRadius: '8px' }}>
          {isHindi ? 'कोई नई रिपोर्ट नहीं' : 'No incoming crowdsource reports.'}
        </div>
      ) : (
        reports.map(report => (
          <div
            key={report.id}
            style={{
              backgroundColor: theme === 'dark' ? '#0f172a' : '#f1f5f9',
              border: '1px solid #334155',
              borderRadius: '8px',
              padding: '10px',
              fontSize: '0.8rem',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
              <span style={{ color: '#38bdf8' }}>{report.segment_id}</span>
              <span style={{ fontSize: '0.7rem', color: report.status === 'VERIFIED' ? '#10b981' : (report.status === 'REJECTED' ? '#ef4444' : '#f59e0b') }}>
                ● {report.status}
              </span>
            </div>

            <div style={{ color: theme === 'dark' ? '#f8fafc' : '#0f172a', fontWeight: 700 }}>
              {getTypeLabel(report.report_type)}
            </div>

            <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
              By: <strong>{report.reporter_id}</strong> | Lat/Lng: ({report.lat.toFixed(4)}, {report.lng.toFixed(4)})
            </div>

            {report.status === 'PENDING' && (
              <div style={{ display: 'flex', gap: '6px', marginTop: '4px' }}>
                <button
                  onClick={() => onVerify(report.id)}
                  style={{ flex: 1, backgroundColor: '#10b981', color: '#000', border: 'none', padding: '6px', borderRadius: '4px', fontWeight: 700, cursor: 'pointer', fontSize: '0.75rem' }}
                >
                  ✓ {isHindi ? 'पुष्टि करें (Verify)' : 'Verify & Mutate Cost'}
                </button>
                <button
                  onClick={() => onReject(report.id)}
                  style={{ flex: 1, backgroundColor: '#ef4444', color: '#fff', border: 'none', padding: '6px', borderRadius: '4px', fontWeight: 700, cursor: 'pointer', fontSize: '0.75rem' }}
                >
                  ✗ {isHindi ? 'अस्वीकार करें (Reject)' : 'Reject'}
                </button>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
};
