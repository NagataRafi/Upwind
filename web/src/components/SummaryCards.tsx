import React from 'react';
import { SmokeFrame, Hotspot } from '../types';
import { Cloud, Flame, MapPin, Wind, Layers } from 'lucide-react';

interface SummaryCardsProps {
  frame: SmokeFrame;
  hotspots: Hotspot[];
}

export const SummaryCards: React.FC<SummaryCardsProps> = ({ frame, hotspots }) => {
  const peatHotspotsCount = hotspots.filter(h => h.is_peat).length;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 p-2 bg-slate-900 border-b border-slate-800 text-xs">
      {/* 1. Luas Asap */}
      <div className="bg-slate-800/80 p-2.5 rounded-lg border border-slate-700/60 flex items-center justify-between">
        <div>
          <span className="text-[11px] text-slate-400 font-medium block">Luas Asap</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base sm:text-lg font-bold text-white">
              {frame.daylight ? frame.area_km2.toLocaleString('id-ID') : '0'}
            </span>
            <span className="text-[10px] text-slate-400">km²</span>
          </div>
        </div>
        <div className="p-2 rounded-md bg-slate-700/50 text-slate-300">
          <Cloud className="w-4 h-4 text-slate-300" />
        </div>
      </div>

      {/* 2. Jumlah Titik Panas */}
      <div className="bg-slate-800/80 p-2.5 rounded-lg border border-slate-700/60 flex items-center justify-between">
        <div>
          <span className="text-[11px] text-slate-400 font-medium block">Titik Panas (Hotspot)</span>
          <div className="flex items-baseline gap-1 mt-0.5">
            <span className="text-base sm:text-lg font-bold text-amber-400">{hotspots.length}</span>
            <span className="text-[10px] text-red-400 font-medium">({peatHotspotsCount} di gambut)</span>
          </div>
        </div>
        <div className="p-2 rounded-md bg-amber-950/60 text-amber-400">
          <Flame className="w-4 h-4" />
        </div>
      </div>

      {/* 3. Arah Gerak Asap (FR-W7) */}
      <div className="bg-slate-800/80 p-2.5 rounded-lg border border-slate-700/60 flex items-center justify-between">
        <div className="min-w-0">
          <span className="text-[11px] text-slate-400 font-medium block">Arah Gerak Asap</span>
          <div className="mt-0.5 truncate">
            {frame.motion.quality === 'unavailable' ? (
              <span className="text-xs font-semibold text-amber-300">Tidak dapat dihitung</span>
            ) : (
              <span className="text-xs sm:text-sm font-bold text-emerald-400 truncate block">
                {frame.motion.status_text}
              </span>
            )}
          </div>
        </div>
        <div className="p-2 rounded-md bg-emerald-950/60 text-emerald-400 flex-shrink-0">
          <Wind className="w-4 h-4" />
        </div>
      </div>

      {/* 4. Batas Desa (FR-W8: Tidak diisi karangan) */}
      <div className="bg-slate-800/80 p-2.5 rounded-lg border border-slate-700/60 flex items-center justify-between">
        <div className="min-w-0">
          <span className="text-[11px] text-slate-400 font-medium block">Zona Desa Terdampak</span>
          <div className="mt-0.5">
            <span className="text-[11px] text-slate-400 italic block truncate">
              Data belum tersedia (FR-W8)
            </span>
          </div>
        </div>
        <div className="p-2 rounded-md bg-slate-700/50 text-slate-400 flex-shrink-0">
          <MapPin className="w-4 h-4" />
        </div>
      </div>
    </div>
  );
};
