/**
 * SHAP Feature Translation Dictionary (Member C - Prompt 5)
 * SIH26002 - MargSetu: Smart Logistics & Accessibility Platform
 * 
 * Translates raw XGBoost SHAP feature names and metrics into plain-English,
 * user-friendly hazard explanation tooltips for drivers, dispatchers, and GIS operators.
 */

export interface TranslatedFeature {
  feature: string;
  contribution: number;
  direction: string;
  plainEnglishExplanation: string;
}

export const SHAP_FEATURE_DICTIONARY: Record<string, { high: string; low: string }> = {
  ari_7d: {
    high: "Heavy rainfall accumulation over the past 7 days",
    low: "Low recent rainfall accumulation"
  },
  slope_deg: {
    high: "Extremely steep mountain incline (>30° slope)",
    low: "Relatively flat terrain"
  },
  twi: {
    high: "High water saturation zone (topographic water accumulation)",
    low: "Well-drained ridge terrain"
  },
  dist_to_fault_m: {
    high: "Far from known geological fault lines",
    low: "Proximity to high-shear geological fault line"
  },
  soil_saturation_pct: {
    high: "Saturated soil structure with high pore water pressure",
    low: "Dry soil matrix"
  },
  forecast_rain_3h: {
    high: "Severe cloudburst / heavy rain forecast in next 3 hours",
    low: "Clear weather forecast"
  },
  ndvi: {
    high: "Dense vegetation anchoring topsoil",
    low: "Sparse vegetation cover / degraded topsoil anchoring"
  },
  curvature: {
    high: "Concave slope surface collecting runoff water",
    low: "Convex slope surface"
  },
  aspect: {
    high: "South/South-West facing slope exposed to monsoon winds",
    low: "Sheltered slope aspect"
  }
};

export function translateSHAPFeatures(
  topFeatures: Array<{ feature: string; contribution: number; direction: string }>,
  maxCount: number = 3
): TranslatedFeature[] {
  if (!topFeatures || topFeatures.length === 0) {
    return [
      {
        feature: "baseline",
        contribution: 0.0,
        direction: "neutral",
        plainEnglishExplanation: "Road segment operating under normal baseline seasonal conditions."
      }
    ];
  }

  return topFeatures.slice(0, maxCount).map((item) => {
    const dict = SHAP_FEATURE_DICTIONARY[item.feature];
    let text = `${item.feature}: ${item.direction}`;
    
    if (dict) {
      const isHigh = item.direction.includes("increases") || item.direction.includes("high");
      text = isHigh ? dict.high : dict.low;
    }

    return {
      feature: item.feature,
      contribution: item.contribution,
      direction: item.direction,
      plainEnglishExplanation: text
    };
  });
}
