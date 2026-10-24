import React from 'react';
import { SystemStatus, SmokeFrame } from '../types';
import { formatToWIB, DATA_STALE_THRESHOLD_MINUTES } from '../api';
import { Clock, Moon, CloudRain, AlertCircle, CheckCircle2, AlertTriangle } from 'lucide-react';

interface StatusBannerProps {
  status: SystemStatus | null;
  currentFrame: SmokeFrame | null;
}

export const StatusBanner: React.FC<StatusBannerProps> = ({ status, currentFrame }) => {
  if (!currentFrame) return null;

  const isNight = !currentFrame.daylight;
  const isHighCloud = currentFrame.cloud_cover_fraction > 0.7;
  const isDataStale =
    (status?.data_age_minutes ?? 0) > (DATA_STALE_THRESHOLD_MINUTES ?? 60);
  // Sinkron dengan STALE_THRESHOLD_MINUTES di mock/generate_mock_data.py
  const motionUncomputable = currentFrame.motion?.quality === 'unavailable';

  return (
    <div className="flex flex-col gap-1 px-3 py-1.5 bg-slate-800/95 text-slate-200 border-b border-slate-700 text-xs">
      {/* Peringatan Khusus Kasus Sulit (FR-W12, FR-W7, FR-W11) */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Penanda Model Asap Belum Tersedia */}
        {currentFrame.area_km2 === null && (
          <div className="flex items-center gap-1.5 bg-amber-950/80 border border-amber-500/40 text-amber-200 px-2.5 py-1 rounded-md font-medium">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>Model asap belum tersedia (fase P2 pengolahan citra)</span>
          </div>
        )}

        {/* FR-W12: Penanda Malam Hari */}
        {isNight && (
          <div className="flex items-center gap-1.5 bg-indigo-950/80 border border-indigo-500/40 text-indigo-300 px-2.5 py-1 rounded-md font-medium">
            <Moon className="w-3.5 h-3.5 text-indigo-400" />
            <span>Malam: tidak ada pembaruan asap (citra tampak tidak tersedia)</span>
          </div>
        )}

        {/* FR-W12: Penanda Tutupan Awan Tinggi */}
        {isHighCloud && !isNight && (
          <div className="flex items-center gap-1.5 bg-sky-950/80 border border-sky-500/40 text-sky-200 px-2.5 py-1 rounded-md font-medium">
            <CloudRain className="w-3.5 h-3.5 text-sky-400" />
            <span>
              Awan tebal ({Math.round(currentFrame.cloud_cover_fraction * 100)}%): segmentasi optik mungkin terhalang
            </span>
          </div>
        )}

        {/* FR-W7: Gerak Asap Tidak Dapat Dihitung */}
        {motionUncomputable && (currentFrame.area_km2 ?? 0) > 0 && !isNight && (
          <div className="flex items-center gap-1.5 bg-amber-950/80 border border-amber-500/40 text-amber-200 px-2.5 py-1 rounded-md font-medium">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
            <span>Arah gerak asap: <strong>tidak dapat dihitung</strong> (frame urutan tidak mencukupi)</span>
          </div>
        )}

        {/* FR-W11: Peringatan Data Basi */}
        {isDataStale && (
          <div className="flex items-center gap-1.5 bg-rose-950/80 border border-rose-500/40 text-rose-200 px-2.5 py-1 rounded-md font-medium">
            <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
            <span>Peringatan: Usia data telah mencapai {status?.data_age_minutes} menit (melebihi ambang {DATA_STALE_THRESHOLD_MINUTES} mnt)</span>
          </div>
        )}
      </div>

      {/* FR-W11: Baris Status Data Terkini dan Usia Data */}
      <div className="flex flex-wrap items-center justify-between gap-x-4 gap-y-1 text-[11px] text-slate-300">
        <div className="flex items-center gap-2">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>
            Waktu Bingkai: <strong className="text-white">{formatToWIB(currentFrame.timestamp_utc)}</strong>
          </span>
          <span className="text-slate-500">|</span>
          <span>
            Usia data: <strong className={isDataStale ? 'text-rose-400' : 'text-emerald-400'}>{status?.data_age_minutes ?? 25} menit</strong>
          </span>
        </div>

        {/* Status Sumber Data */}
        <div className="flex items-center gap-3">
          <span className="text-slate-400 hidden sm:inline">Sumber:</span>
          <span className="flex items-center gap-1">
            <span className={`w-2 h-2 rounded-full ${status?.sources_status.himawari === 'ok' ? 'bg-emerald-400' : 'bg-rose-400'}`} />
            Himawari-9
          </span>
          <span className="flex items-center gap-1">
            <span className={`w-2 h-2 rounded-full ${status?.sources_status.hotspot === 'ok' ? 'bg-emerald-400' : 'bg-rose-400'}`} />
            FIRMS
          </span>
          <span className="flex items-center gap-1">
            <span className={`w-2 h-2 rounded-full ${status?.sources_status.wind === 'ok' ? 'bg-emerald-400' : 'bg-rose-400'}`} />
            ERA5
          </span>
        </div>
      </div>
    </div>
  );
};
