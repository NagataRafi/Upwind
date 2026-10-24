import React from 'react';
import { SystemStatus } from '../types';

interface FooterBarProps {
  status: SystemStatus | null;
  onOpenAbout: () => void;
}

/**
 * FR-W14: Baris atribusi kaki halaman.
 * Teks selalu menyatakan bahwa data yang tampil saat ini adalah data contoh;
 * Himawari-9, FIRMS, dan ERA5 disebut sebagai sumber yang direncanakan, bukan
 * sumber data yang sedang ditampilkan. Atribusi OpenStreetMap cukup tampil
 * di pojok peta (lihat MapView) dan tidak diulang di sini.
 */
export const FooterBar: React.FC<FooterBarProps> = ({ status, onOpenAbout }) => {
  const isMock = status?.is_mock ?? true;
  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-0.5 px-3 py-1 bg-slate-800/95 border-t border-slate-700 text-[10px] text-slate-400">
      <span>Sumber direncanakan (data asli): Himawari-9 JMA/NOAA - FIRMS NASA - Angin Prakiraan Model Open-Meteo (CC BY 4.0) / ERA5-Land ECMWF</span>
      {isMock && (
        <span className="text-orange-400 font-semibold">
          Saat ini: data contoh, bukan data asli
        </span>
      )}
      <button
        type="button"
        onClick={onOpenAbout}
        className="ml-auto underline hover:text-white transition"
      >
        Atribusi dan keterbatasan lengkap di Tentang
      </button>
    </div>
  );
};
