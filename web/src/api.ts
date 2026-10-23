/**
 * Layanan API Pembaca Data Upwind
 * Mengambil file JSON statis dari /data/ yang disediakan oleh generator mock atau pipeline data asli.
 */

import { SystemStatus, FrameIndexItem, FrameBundle, RegionId } from './types';

// KEPUTUSAN 2026-10-23: Ambang usia data basi 60 menit (sama dengan
// STALE_THRESHOLD_MINUTES di mock/generate_mock_data.py; ubah serentak).
export const DATA_STALE_THRESHOLD_MINUTES = 60;

// Format waktu UTC string ke tampilan WIB (UTC+7)
export function formatToWIB(utcString: string): string {
  try {
    const d = new Date(utcString);
    if (isNaN(d.getTime())) return utcString;
    // Tambah 7 jam untuk WIB
    const wibDate = new Date(d.getTime() + 7 * 60 * 60 * 1000);
    const yyyy = wibDate.getUTCFullYear();
    const mm = String(wibDate.getUTCMonth() + 1).padStart(2, '0');
    const dd = String(wibDate.getUTCDate()).padStart(2, '0');
    const hh = String(wibDate.getUTCHours()).padStart(2, '0');
    const min = String(wibDate.getUTCMinutes()).padStart(2, '0');
    return `${dd}/${mm}/${yyyy} ${hh}:${min} WIB`;
  } catch {
    return utcString;
  }
}

export function formatTimeOnlyWIB(utcString: string): string {
  try {
    const d = new Date(utcString);
    if (isNaN(d.getTime())) return utcString;
    const wibDate = new Date(d.getTime() + 7 * 60 * 60 * 1000);
    const hh = String(wibDate.getUTCHours()).padStart(2, '0');
    const min = String(wibDate.getUTCMinutes()).padStart(2, '0');
    return `${hh}:${min} WIB`;
  } catch {
    return utcString;
  }
}

export async function fetchSystemStatus(): Promise<SystemStatus> {
  const res = await fetch('/data/status.json');
  if (!res.ok) {
    throw new Error(`Gagal memuat status sistem: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchFrameIndex(regionId: RegionId): Promise<FrameIndexItem[]> {
  const res = await fetch(`/data/${regionId}/index.json`);
  if (!res.ok) {
    throw new Error(`Gagal memuat indeks bingkai untuk wilayah ${regionId}: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchFrameBundle(regionId: RegionId, timestampSafe: string): Promise<FrameBundle> {
  const res = await fetch(`/data/${regionId}/${timestampSafe}.json`);
  if (!res.ok) {
    throw new Error(`Gagal memuat data bingkai ${timestampSafe}: ${res.statusText}`);
  }
  return res.json();
}
