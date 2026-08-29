/**
 * Dashboard Settings React Context (Member C - Prompt 1b)
 * SIH26002 - MargSetu: Smart Logistics & Accessibility Platform
 * 
 * Centralized state management for map layers, live threshold adjustment,
 * 24h time scrubbing, units/language toggles, and dark/light themes.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export interface LayerState {
  roads: boolean;
  vehicles: boolean;
  crowdsourceReports: boolean;
  rainfallOverlay: boolean;
}

export type UnitType = 'km' | 'mi';
export type LanguageType = 'en' | 'hi';
export type ThemeType = 'dark' | 'light';

export interface DashboardSettings {
  layers: LayerState;
  toggleLayer: (layer: keyof LayerState) => void;
  timeHour: number; // 0 to 24h scrub
  setTimeHour: (hour: number) => void;
  warningThreshold: number; // default 0.35
  setWarningThreshold: (val: number) => void;
  criticalThreshold: number; // default 0.70
  setCriticalThreshold: (val: number) => void;
  units: UnitType;
  setUnits: (u: UnitType) => void;
  language: LanguageType;
  setLanguage: (lang: LanguageType) => void;
  theme: ThemeType;
  setTheme: (t: ThemeType) => void;
  viewMode: '2D' | '3D';
  setViewMode: (v: '2D' | '3D') => void;
  lastSyncedTimestamp: string;
  setLastSyncedTimestamp: (ts: string) => void;
}

const defaultSettings: DashboardSettings = {
  layers: { roads: true, vehicles: true, crowdsourceReports: true, rainfallOverlay: true },
  toggleLayer: () => {},
  timeHour: 24,
  setTimeHour: () => {},
  warningThreshold: 0.35,
  setWarningThreshold: () => {},
  criticalThreshold: 0.70,
  setCriticalThreshold: () => {},
  units: 'km',
  setUnits: () => {},
  language: 'en',
  setLanguage: () => {},
  theme: 'dark',
  setTheme: () => {},
  viewMode: '2D',
  setViewMode: () => {},
  lastSyncedTimestamp: 'Just Now',
  setLastSyncedTimestamp: () => {}
};

const DashboardSettingsContext = createContext<DashboardSettings>(defaultSettings);

export const DashboardSettingsProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [layers, setLayers] = useState<LayerState>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('margsetu_layers');
      if (saved) return JSON.parse(saved);
    }
    return defaultSettings.layers;
  });

  const [timeHour, setTimeHour] = useState<number>(24);
  const [warningThreshold, setWarningThreshold] = useState<number>(0.35);
  const [criticalThreshold, setCriticalThreshold] = useState<number>(0.70);
  const [units, setUnits] = useState<UnitType>('km');
  const [language, setLanguage] = useState<LanguageType>('en');
  const [theme, setTheme] = useState<ThemeType>('dark');
  const [viewMode, setViewMode] = useState<'2D' | '3D'>('2D');
  const [lastSyncedTimestamp, setLastSyncedTimestamp] = useState<string>('Just Now');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('margsetu_layers', JSON.stringify(layers));
    }
  }, [layers]);

  const toggleLayer = (layerKey: keyof LayerState) => {
    setLayers(prev => ({ ...prev, [layerKey]: !prev[layerKey] }));
  };

  return (
    <DashboardSettingsContext.Provider
      value={{
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
        viewMode,
        setViewMode,
        lastSyncedTimestamp,
        setLastSyncedTimestamp
      }}
    >
      {children}
    </DashboardSettingsContext.Provider>
  );
};

export const useDashboardSettings = () => useContext(DashboardSettingsContext);
