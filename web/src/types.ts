/**
 * Definisi Tipe Kontrak Data Upwind
 * Sesuai ARSITEKTUR.md Bagian 3 dan docs/KONTRAK_DATA.md
 */

export type RegionId = 'riau' | 'kalteng';

export interface MotionData {
  direction_deg: number | null;
  speed_kmh: number | null;
  quality: 'good' | 'moderate' | 'poor' | 'unavailable';
  status_text: string;
}

export interface SmokeFrame {
  timestamp_utc: string;
  processed_utc: string;
  region_id: RegionId;
  bbox: [number, number, number, number]; // [min_lon, min_lat, max_lon, max_lat]
  mask_overlay: string;
  probability_overlay: string;
  uncertainty_overlay: string;
  area_km2: number;
  motion: MotionData;
  source_frames: string[];
  daylight: boolean;
  cloud_cover_fraction: number;
  model_version: string;
  code_version: string;
  is_mock: boolean;
}

export interface Hotspot {
  id: string;
  time_utc: string;
  lat: number;
  lon: number;
  source: string;
  confidence: number | string;
  frp: number;
  is_peat: boolean;
  is_mock: boolean;
}

export interface WindSample {
  time_utc: string;
  lat: number;
  lon: number;
  u: number;
  v: number;
  height_m: number;
  source: string;
  is_mock: boolean;
}

export interface RankedSourceFactors {
  distance_to_upwind_edge_km?: number | null;
  angle_difference_deg?: number | null;
  hotspot_confidence?: number | null;
  peat_factor?: number | null;
  [key: string]: any;
}

export interface RankedSource {
  frame_timestamp_utc: string;
  hotspot_id: string;
  rank: number;
  score: number;
  factors: RankedSourceFactors;
  explanation: string;
  method_version: string;
  is_mock: boolean;
}

export interface FrameBundle {
  frame: SmokeFrame;
  hotspots: Hotspot[];
  wind: WindSample[];
  ranked_sources: RankedSource[];
}

export interface FrameIndexItem {
  timestamp_utc: string;
  timestamp_safe: string;
  daylight: boolean;
  cloud_cover_fraction: number;
  area_km2: number;
  has_smoke: boolean;
  motion_quality: string;
  scenario_type: string;
}

export interface SystemStatus {
  last_processed_utc: string;
  latest_frame_utc: string;
  data_age_minutes: number;
  sources_status: {
    himawari: 'ok' | 'delayed' | 'failed';
    hotspot: 'ok' | 'delayed' | 'failed';
    wind: 'ok' | 'delayed' | 'failed';
  };
  night_no_smoke_update: boolean;
  cloud_cover_high: boolean;
  is_mock: boolean;
  note?: string;
}

export interface LayerVisibility {
  smokeMask: boolean;
  smokeMaskOpacity: number;
  smokeProb: boolean;
  smokeProbOpacity: number;
  smokeUnc: boolean;
  smokeUncOpacity: number;
  hotspots: boolean;
  wind: boolean;
  motionArrow: boolean;
}
