import React from 'react';
import { RankedSource, Hotspot } from '../types';
import { Compass, Flame, ArrowUpRight, CheckCircle2, ChevronRight, AlertCircle } from 'lucide-react';

interface UpwindPanelProps {
  rankedSources: RankedSource[];
  hotspots: Hotspot[];
  selectedHotspotId: string | null;
  onSelectHotspot: (id: string) => void;
  isOpenMobile: boolean;
  onToggleMobile: () => void;
}

export const UpwindPanel: React.FC<UpwindPanelProps> = ({
  rankedSources,
  hotspots,
  selectedHotspotId,
  onSelectHotspot,
  isOpenMobile,
  onToggleMobile
}) => {
  // Map hotspot ID ke objek hotspot untuk cepat mengambil FRP dan is_peat
  const hotspotMap = new Map(hotspots.map((h) => [h.id, h]));

  return (
    <aside
      className={`
        bg-slate-900/95 text-slate-100 border-l border-slate-800 flex flex-col z-20 backdrop-blur-md
        transition-all duration-300 ease-in-out
        ${/* Tampilan Mobile: Bottom Sheet yang bisa digeser/ditutup */ ''}
        fixed inset-x-0 bottom-0 md:static md:w-80 lg:w-96 md:h-auto md:max-h-full
        ${isOpenMobile ? 'h-[65vh] shadow-2xl rounded-t-2xl' : 'h-12 md:h-auto rounded-none'}
      `}
    >
      {/* Header Panel */}
      <div
        onClick={onToggleMobile}
        className="p-3 bg-slate-800/90 border-b border-slate-700/80 flex items-center justify-between cursor-pointer md:cursor-default flex-shrink-0"
      >
        <div className="flex items-center gap-2">
          <div className="p-1 rounded bg-red-950/70 text-red-400">
            <Compass className="w-4 h-4 text-red-400" />
          </div>
          <div>
            <h2 className="text-xs sm:text-sm font-bold text-white flex items-center gap-1.5">
              Titik Panas Hulu Asap (FR-W6)
            </h2>
            <span className="text-[10px] text-slate-400 block">
              Peringkat kandidat sumber penyulut asap
            </span>
          </div>
        </div>

        {/* Indikator Jumlah / Toggle Mobile */}
        <div className="flex items-center gap-2">
          <span className="bg-red-600/30 text-red-300 border border-red-500/40 text-[11px] font-bold px-2 py-0.5 rounded-full">
            {rankedSources.length} Kandidat
          </span>
          <span className="md:hidden text-xs text-slate-400 font-medium">
            {isOpenMobile ? 'Tutup ↓' : 'Buka ↑'}
          </span>
        </div>
      </div>

      {/* Konten Daftar Titik Panas Hulu Asap */}
      <div className={`p-2 space-y-2 overflow-y-auto flex-1 ${!isOpenMobile ? 'hidden md:block' : 'block'}`}>
        {rankedSources.length === 0 ? (
          <div className="p-4 text-center text-slate-400 text-xs">
            <AlertCircle className="w-6 h-6 mx-auto mb-1.5 text-slate-500" />
            <p>Tidak ada titik panas aktif di sektor hulu untuk bingkai ini.</p>
          </div>
        ) : (
          rankedSources.map((item) => {
            const hp = hotspotMap.get(item.hotspot_id);
            const isSelected = selectedHotspotId === item.hotspot_id;

            return (
              <div
                key={item.hotspot_id}
                onClick={() => onSelectHotspot(item.hotspot_id)}
                className={`
                  p-2.5 rounded-xl border text-xs cursor-pointer transition-all
                  ${
                    isSelected
                      ? 'bg-red-950/40 border-red-500/80 shadow-md ring-1 ring-red-500/50'
                      : 'bg-slate-800/70 border-slate-700/60 hover:bg-slate-800 hover:border-slate-600'
                  }
                `}
              >
                {/* Baris Atas: Peringkat, ID Hotspot, Skor */}
                <div className="flex items-center justify-between gap-1 mb-1.5">
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`
                        w-5 h-5 rounded-full flex items-center justify-center font-bold text-[11px]
                        ${
                          item.rank === 1
                            ? 'bg-red-600 text-white'
                            : item.rank === 2
                            ? 'bg-amber-600 text-white'
                            : 'bg-slate-700 text-slate-300'
                        }
                      `}
                    >
                      {item.rank}
                    </span>
                    <span className="font-mono text-[11px] font-semibold text-slate-200">
                      {item.hotspot_id.replace(/^hp_[a-z]+_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z_/, 'HP-')}
                    </span>
                    {hp?.is_peat && (
                      <span className="bg-amber-950/80 text-amber-300 border border-amber-600/40 text-[9px] px-1.5 py-0.2 rounded font-medium">
                        Gambut
                      </span>
                    )}
                  </div>

                  {/* Skor Heuristik */}
                  <div className="flex items-center gap-1">
                    <span className="text-[10px] text-slate-400">Skor:</span>
                    <span className="font-bold text-amber-400 font-mono text-xs">
                      {Math.round(item.score * 100)}%
                    </span>
                  </div>
                </div>

                {/* FR-W6: Penjelasan Satu Kalimat Bahasa Indonesia */}
                <p className="text-[11px] text-slate-300 leading-relaxed mb-2">
                  {item.explanation}
                </p>

                {/* Rincian Faktor Pendukung */}
                <div className="grid grid-cols-2 gap-1.5 text-[10px] text-slate-400 bg-slate-900/60 p-1.5 rounded-lg border border-slate-800">
                  <div>
                    Jarak Hulu:{' '}
                    <strong className="text-slate-200">
                      {item.factors.distance_to_upwind_edge_km != null
                        ? `${item.factors.distance_to_upwind_edge_km} km`
                        : '—'}
                    </strong>
                  </div>
                  <div>
                    Daya FRP:{' '}
                    <strong className="text-amber-300">
                      {hp ? `${hp.frp} MW` : '—'}
                    </strong>
                  </div>
                  <div>
                    Deviasi Sudut:{' '}
                    <strong className="text-slate-200">
                      {item.factors.angle_difference_deg != null
                        ? `${item.factors.angle_difference_deg}°`
                        : '—'}
                    </strong>
                  </div>
                  <div>
                    Kepercayaan:{' '}
                    <strong className="text-slate-200">
                      {hp ? (typeof hp.confidence === 'number' ? `${hp.confidence}%` : hp.confidence) : '—'}
                    </strong>
                  </div>
                </div>

                {/* Tombol Aksi Sorot di Peta */}
                <div className="mt-2 flex items-center justify-end text-[10px] text-sky-400 font-medium gap-0.5">
                  <span>Sorot di peta</span>
                  <ChevronRight className="w-3 h-3" />
                </div>
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
};
