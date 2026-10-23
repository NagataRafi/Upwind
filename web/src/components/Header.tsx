import React from 'react';
import { RegionId, SystemStatus } from '../types';
import { Flame, Info, AlertTriangle, ShieldAlert } from 'lucide-react';

interface HeaderProps {
  regionId: RegionId;
  onRegionChange: (reg: RegionId) => void;
  status: SystemStatus | null;
  onOpenAbout: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  regionId,
  onRegionChange,
  status,
  onOpenAbout
}) => {
  const isMock = status?.is_mock ?? true;

  return (
    <header className="bg-slate-900 text-white shadow-md z-30 flex-shrink-0 border-b border-slate-800">
      {/* FR-W10: Spanduk Permanen Data Tiruan */}
      {isMock && (
        <div 
          role="alert"
          className="bg-amber-600 text-amber-950 font-bold px-3 py-1 text-xs tracking-wider uppercase text-center flex items-center justify-center gap-1.5 shadow-inner"
        >
          <AlertTriangle className="w-4 h-4 text-amber-950 flex-shrink-0" />
          <span>DATA CONTOH, BUKAN DATA ASLI (FR-W10)</span>
          <span className="hidden sm:inline font-normal text-[11px] opacity-90">— Jangan dijadikan acuan operasional lapangan</span>
        </div>
      )}

      {/* Bar Navigasi Utama */}
      <div className="max-w-7xl mx-auto px-3 sm:px-4 py-2 flex items-center justify-between gap-2">
        {/* FR-W17: Identitas Aplikasi */}
        <div className="flex items-center gap-2.5 min-w-0">
          <div className="bg-red-600 p-1.5 rounded-lg text-white shadow-sm flex-shrink-0">
            <Flame className="w-5 h-5 fill-white" />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <h1 className="text-base sm:text-lg font-black tracking-tight text-white flex items-center gap-1">
                Upwind
              </h1>
              {/* FR-W13: Label Perkiraan, bukan jaminan */}
              <span className="hidden md:inline-flex items-center text-[10px] bg-slate-800 text-amber-400 border border-amber-500/30 px-1.5 py-0.5 rounded font-medium">
                Perkiraan, bukan jaminan
              </span>
            </div>
            <p className="text-[11px] sm:text-xs text-slate-300 truncate font-normal">
              Pemantau asap karhutla dan titik panas hulu asap
            </p>
          </div>
        </div>

        {/* Pilihan Wilayah (FR-W1) dan Tombol Tentang (FR-W13, FR-W14) */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {/* FR-W1: Pilihan Wilayah */}
          <div className="flex bg-slate-800 rounded-lg p-0.5 border border-slate-700 text-xs font-semibold">
            <button
              type="button"
              onClick={() => onRegionChange('riau')}
              className={`px-2.5 py-1.5 rounded-md transition-all ${
                regionId === 'riau'
                  ? 'bg-red-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700'
              }`}
            >
              Riau
            </button>
            <button
              type="button"
              onClick={() => onRegionChange('kalteng')}
              className={`px-2.5 py-1.5 rounded-md transition-all ${
                regionId === 'kalteng'
                  ? 'bg-red-600 text-white shadow-sm'
                  : 'text-slate-300 hover:text-white hover:bg-slate-700'
              }`}
            >
              Kalteng
            </button>
          </div>

          {/* Tombol Tentang & Keterbatasan */}
          <button
            type="button"
            onClick={onOpenAbout}
            className="flex items-center gap-1 bg-slate-800 hover:bg-slate-700 text-slate-200 hover:text-white text-xs px-2.5 py-1.5 rounded-lg border border-slate-700 transition"
            title="Tentang metodologi dan keterbatasan satelit"
          >
            <Info className="w-3.5 h-3.5 text-sky-400" />
            <span className="hidden sm:inline font-medium">Tentang</span>
          </button>
        </div>
      </div>
    </header>
  );
};
