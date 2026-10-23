import React from 'react';
import { X, ShieldAlert, BookOpen, ExternalLink, Award } from 'lucide-react';

interface AboutModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const AboutModal: React.FC<AboutModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 bg-black/70 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto shadow-2xl text-slate-200 text-xs">
        {/* Header Modal */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-between sticky top-0 bg-slate-900/95 backdrop-blur z-10">
          <div className="flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-red-500" />
            <h2 className="text-sm sm:text-base font-bold text-white">
              Tentang & Keterbatasan Sistem Upwind (FR-W13)
            </h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Konten Utama */}
        <div className="p-4 space-y-4 leading-relaxed">
          {/* FR-W13: Pernyataan Batas dan Validasi BRIN */}
          <div className="p-3 rounded-xl bg-amber-950/40 border border-amber-500/40 text-amber-200 space-y-1.5">
            <div className="flex items-center gap-1.5 font-bold text-amber-300">
              <ShieldAlert className="w-4 h-4 text-amber-400" />
              <span>Prinsip Kejujuran: Perkiraan, Bukan Jaminan</span>
            </div>
            <p>
              1. <strong>Asap bukan titik api.</strong> Asap dapat terbawa angin puluhan kilometer dari pusat kebakaran.
            </p>
            <p>
              2. <strong>Titik panas satelit meleset dari posisi sebenarnya:</strong> Menurut riset validasi BRIN di lahan gambut Kalimantan Tengah, akurasi deteksi hotspot satelit Himawari-8 berada di angka <strong>51,33% dalam radius 2 km</strong> untuk algoritma terbaik. Titik panas digunakan sebagai petunjuk arah penyelidikan tim lapangan, bukan bukti mutlak koordinat api.
            </p>
          </div>

          {/* Keterbatasan Teknis Siang/Malam & Awan */}
          <div className="space-y-2">
            <h3 className="font-bold text-white text-xs uppercase tracking-wider text-slate-400">
              Keterbatasan Sensor dan Citra
            </h3>
            <ul className="list-disc pl-4 space-y-1 text-slate-300">
              <li>
                <strong>Malam Hari:</strong> Satelit geostasioner Himawari-9 mengandalkan spektrum tampak (visible) untuk membedakan gumpalan asap. Pada malam hari (pukul 18.30 – 05.30 WIB), pembaruan segmentasi asap dihentikan secara jujur dan sistem menyatakan &quot;Malam: tidak ada pembaruan asap&quot;.
              </li>
              <li>
                <strong>Tutupan Awan Tebal:</strong> Awan kumulonimbus tebal menutupi pantulan permukaan dan asap gambut di bawahnya. Tutupan awan di atas 70% akan memicu peringatan keterbatasan deteksi optik.
              </li>
            </ul>
          </div>

          {/* Metodologi Titik Panas Hulu Asap (Smoke-to-source) */}
          <div className="space-y-2">
            <h3 className="font-bold text-white text-xs uppercase tracking-wider text-slate-400">
              Metode Titik Panas Hulu Asap (FR-S, FR-W6)
            </h3>
            <p className="text-slate-300">
              Upwind menganalisis arah vektor gerak gumpalan asap dari rangkaian frame satelit berkala (10 menit) yang dipadukan dengan arah dan kecepatan angin permukaan (ERA5 10m). Titik panas yang berada di sektor hulu (upwind) dan bertepatan di kubah gambut berdaya api (FRP) tinggi diprioritaskan agar satgas darat dapat memfokuskan sumber pemadaman.
            </p>
          </div>

          {/* FR-W14: Atribusi Sumber Data Resmi */}
          <div className="space-y-2 pt-2 border-t border-slate-800">
            <h3 className="font-bold text-white text-xs uppercase tracking-wider text-slate-400">
              Atribusi Sumber Data (FR-W14)
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
              <div className="bg-slate-800/60 p-2 rounded-lg border border-slate-700/50">
                <span className="font-semibold text-white block">Satelit Himawari-9</span>
                <span className="text-slate-400">JMA / NOAA Open Data AWS</span>
              </div>
              <div className="bg-slate-800/60 p-2 rounded-lg border border-slate-700/50">
                <span className="font-semibold text-white block">Titik Panas (Hotspot)</span>
                <span className="text-slate-400">NASA FIRMS (VIIRS NOAA-20 & Suomi-NPP)</span>
              </div>
              <div className="bg-slate-800/60 p-2 rounded-lg border border-slate-700/50">
                <span className="font-semibold text-white block">Vektor Angin Permukaan</span>
                <span className="text-slate-400">ECMWF ERA5-Land Reanalysis (10m)</span>
              </div>
              <div className="bg-slate-800/60 p-2 rounded-lg border border-slate-700/50">
                <span className="font-semibold text-white block">Peta Dasar</span>
                <span className="text-slate-400">CartoDB Positron / OpenStreetMap Contributors</span>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Modal */}
        <div className="p-3 border-t border-slate-800 flex justify-end bg-slate-900/90">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-medium text-xs transition"
          >
            Tutup
          </button>
        </div>
      </div>
    </div>
  );
};
