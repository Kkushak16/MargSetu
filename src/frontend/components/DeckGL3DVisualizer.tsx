/**
 * 3D Extruded Hazard Visualizer & Cinematic Camera Engine (Member C - Prompt 7 & Prompt 8)
 * SIH26002 - MargSetu: Smart Logistics & Accessibility Platform
 * 
 * Provides 3D extruded hazard columns scaled by ML hazard probability,
 * animated vehicle trip overlays, and a "Cinematic Fly-through" camera preset for pitch demos.
 */

import React, { useState, useEffect } from 'react';
import { RoadSegment } from './GISDashboard';

export interface DeckGL3DProps {
  segments: RoadSegment[];
  onFlyThroughComplete?: () => void;
}

export const DeckGL3DVisualizer: React.FC<DeckGL3DProps> = ({ segments, onFlyThroughComplete }) => {
  const [cameraZoom, setCameraZoom] = useState<number>(10);
  const [cameraPitch, setCameraPitch] = useState<number>(45); // 3D perspective pitch angle
  const [cameraBearing, setCameraBearing] = useState<number>(0);
  const [isCinematicActive, setIsCinematicActive] = useState<boolean>(false);
  const [animatedProgress, setAnimatedProgress] = useState<number>(0);

  // High hazard segment for cinematic focus (NH10_SEG_003)
  const criticalSegment = segments.find(s => s.hazard_prob >= 0.70) || segments[0];

  const triggerCinematicFlyThrough = () => {
    setIsCinematicActive(true);
    let step = 0;
    const totalSteps = 40; // 4 seconds easing animation

    const timer = setInterval(() => {
      step++;
      const progress = step / totalSteps;
      setAnimatedProgress(progress);

      // Smooth ease-in-out rotation & zoom down into the critical valley
      setCameraZoom(10 + progress * 4); // Zoom from 10 to 14
      setCameraPitch(30 + progress * 30); // Pitch from 30 to 60 degrees
      setCameraBearing(progress * 120); // Rotate bearing 120 degrees

      if (step >= totalSteps) {
        clearInterval(timer);
        setIsCinematicActive(false);
        if (onFlyThroughComplete) onFlyThroughComplete();
      }
    }, 100);
  };

  return (
    <div style={{ position: 'relative', width: '100%', height: '100%', backgroundColor: '#020617', borderRadius: '10px', overflow: 'hidden', border: '1px solid #334155' }}>
      
      {/* 3D Control Overlay Bar */}
      <div style={{ position: 'absolute', top: '12px', left: '12px', zIndex: 100, display: 'flex', gap: '8px' }}>
        <button
          onClick={triggerCinematicFlyThrough}
          disabled={isCinematicActive}
          style={{
            backgroundColor: isCinematicActive ? '#475569' : '#dc2626',
            color: '#fff',
            border: 'none',
            padding: '8px 14px',
            borderRadius: '6px',
            fontWeight: 700,
            cursor: 'pointer',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.4)'
          }}
        >
          {isCinematicActive ? `🎬 Flying into Valley... (${(animatedProgress * 100).toFixed(0)}%)` : '🎬 Cinematic Pitch Demo (Fly-Through)'}
        </button>
      </div>

      {/* 3D Projection Canvas (deck.gl ColumnLayer & Trip Simulation representation) */}
      <div style={{
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        justify: 'center',
        alignItems: 'center',
        padding: '24px',
        transform: `perspective(800px) rotateX(${cameraPitch}deg) rotateZ(${cameraBearing}deg) scale(${cameraZoom / 10})`,
        transition: 'transform 0.1s ease-out'
      }}>
        <div style={{ fontSize: '0.85rem', color: '#38bdf8', marginBottom: '16px', fontWeight: 600 }}>
          3D Extruded Hazard Columns (Height &propto; ML Hazard Probability)
        </div>

        <div style={{ display: 'flex', gap: '30px', alignItems: 'flex-end', height: '240px', borderBottom: '2px solid #334155', paddingBottom: '10px' }}>
          {segments.map((seg) => {
            const heightPx = Math.max(30, seg.hazard_prob * 200);
            const color = seg.hazard_prob >= 0.70 ? '#ef4444' : (seg.hazard_prob >= 0.35 ? '#f59e0b' : '#10b981');
            const isTarget = criticalSegment?.segment_id === seg.segment_id;

            return (
              <div key={seg.segment_id} style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6px' }}>
                <span style={{ fontSize: '0.7rem', color: '#94a3b8' }}>
                  {(seg.hazard_prob * 100).toFixed(0)}%
                </span>
                
                {/* Extruded Vertical Column */}
                <div style={{
                  width: '36px',
                  height: `${heightPx}px`,
                  backgroundColor: color,
                  borderRadius: '6px 6px 0 0',
                  boxShadow: isTarget ? '0 0 20px #ef4444' : '0 4px 10px rgba(0,0,0,0.5)',
                  border: isTarget ? '2px solid #ffffff' : '1px solid rgba(255,255,255,0.2)',
                  transition: 'height 0.3s ease-in-out'
                }} />

                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#f8fafc' }}>
                  {seg.segment_id}
                </span>
              </div>
            );
          })}
        </div>

        <div style={{ marginTop: '20px', fontSize: '0.75rem', color: '#64748b' }}>
          Perspective Pitch: {cameraPitch.toFixed(0)}° | Bearing: {cameraBearing.toFixed(0)}° | Zoom: {cameraZoom.toFixed(1)}x
        </div>
      </div>
    </div>
  );
};
