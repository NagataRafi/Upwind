import React from 'react';
import { LayerVisibility } from '../types';
import { Eye, EyeOff, Sliders, Layers } from 'lucide-react';

interface LayerControlProps {
  layers: LayerVisibility;
  onChange: (layers: LayerVisibility) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export const LayerControl: React.FC<LayerControlProps> = ({
  layers,
  onChange,
  isCollapsed,
  onToggleCollapse
}) => {
  const update = (partial: Partial<LayerVisibility>) => {
    onChange({ ...layers, ...partial });
  };

  return (
    <div className="bg-slate-900/95 text-white border border-slate-700/80 rounded-xl shadow-xl overflow-hidden backdrop-blur-md max-w-xs w-full text-xs transition-all">
      {/* Header Panel */}
      <button
        type="button"
        onClick={onToggleCollapse}
        className="w-full flex items-center justify-between p-2.5 bg-slate-800/90 hover:bg-slate-800 font-semibold text-slate-200 transition"
      >
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          <span>Lapisan Peta & Kontrol</span>
        </div>
        <span className="text-[11px] text-slate-400">
          {isCollapsed ? 'Buka' : 'Tutup'}
        </span>
      </button>

      {!isCollapsed && (
        <div className="p-3 space-y-3.5 max-h-[70vh] overflow-y-auto">
          {/* FR-W2: Mask Asap & Slider */}
          <div className="space-y-1.5 border-b border-slate-800 pb-2.5">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer font-medium text-slate-200">
                <input
                  type="checkbox"
                  checked={layers.smokeMask}
                  onChange={(e) => update({ smokeMask: e.target.checked })}
                  className="rounded text-red-600 focus:ring-0 bg-slate-800 border-slate-700"
                />
                <span>Mask Asap Karhutla</span>
              </label>
              <span className="text-[10px] text-slate-400 font-mono">
                {Math.round(layers.smokeMaskOpacity * 100)}%
              </span>
            </div>
            {layers.smokeMask && (
              <div className="pl-6 pr-1 flex items-center gap-2">
                <span className="text-[10px] text-slate-500">Transparansi:</span>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={layers.smokeMaskOpacity}
                  onChange={(e) => update({ smokeMaskOpacity: parseFloat(e.target.value) })}
                  className="w-full accent-red-500 h-1.5 bg-slate-700 rounded-lg cursor-pointer"
                />
              </div>
            )}
          </div>

          {/* FR-W3: Probabilitas Asap */}
          <div className="space-y-1.5 border-b border-slate-800 pb-2.5">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer font-medium text-slate-200">
                <input
                  type="checkbox"
                  checked={layers.smokeProb}
                  onChange={(e) => update({ smokeProb: e.target.checked })}
                  className="rounded text-amber-500 focus:ring-0 bg-slate-800 border-slate-700"
                />
                <span>Probabilitas Model (FR-W3)</span>
              </label>
              <span className="text-[10px] text-slate-400 font-mono">
                {Math.round(layers.smokeProbOpacity * 100)}%
              </span>
            </div>
            {layers.smokeProb && (
              <div className="pl-6 space-y-1.5">
                <div className="flex items-center gap-2 pr-1">
                  <span className="text-[10px] text-slate-500">Opasitas:</span>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={layers.smokeProbOpacity}
                    onChange={(e) => update({ smokeProbOpacity: parseFloat(e.target.value) })}
                    className="w-full accent-amber-500 h-1.5 bg-slate-700 rounded-lg cursor-pointer"
                  />
                </div>
                {/* Legenda Probabilitas */}
                <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                  <div className="w-14 h-2 rounded bg-gradient-to-r from-yellow-300 via-orange-500 to-red-600" />
                  <span>Rendah (0.2) → Sangat Tinggi (1.0)</span>
                </div>
              </div>
            )}
          </div>

          {/* FR-W3: Ketidakpastian Per Piksel */}
          <div className="space-y-1.5 border-b border-slate-800 pb-2.5">
            <div className="flex items-center justify-between">
              <label className="flex items-center gap-2 cursor-pointer font-medium text-slate-200">
                <input
                  type="checkbox"
                  checked={layers.smokeUnc}
                  onChange={(e) => update({ smokeUnc: e.target.checked })}
                  className="rounded text-purple-500 focus:ring-0 bg-slate-800 border-slate-700"
                />
                <span>Ketidakpastian Model</span>
              </label>
              <span className="text-[10px] text-slate-400 font-mono">
                {Math.round(layers.smokeUncOpacity * 100)}%
              </span>
            </div>
            {layers.smokeUnc && (
              <div className="pl-6 space-y-1.5">
                <div className="flex items-center gap-2 pr-1">
                  <span className="text-[10px] text-slate-500">Opasitas:</span>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.05"
                    value={layers.smokeUncOpacity}
                    onChange={(e) => update({ smokeUncOpacity: parseFloat(e.target.value) })}
                    className="w-full accent-purple-500 h-1.5 bg-slate-700 rounded-lg cursor-pointer"
                  />
                </div>
                {/* Legenda Ketidakpastian */}
                <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                  <div className="w-14 h-2 rounded bg-gradient-to-r from-purple-300 via-purple-600 to-fuchsia-800" />
                  <span>Piksel batas/transisi yang meragukan</span>
                </div>
              </div>
            )}
          </div>

          {/* FR-W4: Titik Panas (Hotspots) */}
          <div className="border-b border-slate-800 pb-2.5">
            <label className="flex items-center justify-between cursor-pointer font-medium text-slate-200">
              <span className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={layers.hotspots}
                  onChange={(e) => update({ hotspots: e.target.checked })}
                  className="rounded text-amber-400 focus:ring-0 bg-slate-800 border-slate-700"
                />
                <span>Titik Panas (Hotspots)</span>
              </span>
              <div className="flex items-center gap-1.5 text-[10px] text-slate-400">
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-amber-500" /> Gambut
                <span className="inline-block w-2.5 h-2.5 rounded-full bg-orange-400 ml-1" /> Mineral
              </div>
            </label>
          </div>

          {/* FR-W5: Vektor Angin Panah */}
          <div className="border-b border-slate-800 pb-2.5">
            <label className="flex items-center justify-between cursor-pointer font-medium text-slate-200">
              <span className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={layers.wind}
                  onChange={(e) => update({ wind: e.target.checked })}
                  className="rounded text-sky-400 focus:ring-0 bg-slate-800 border-slate-700"
                />
                <span>Panah Angin (ERA5 10m)</span>
              </span>
              <span className="text-[10px] text-slate-400 font-mono">m/s</span>
            </label>
          </div>

          {/* FR-W7: Panah Arah Gerak Asap */}
          <div>
            <label className="flex items-center justify-between cursor-pointer font-medium text-slate-200">
              <span className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={layers.motionArrow}
                  onChange={(e) => update({ motionArrow: e.target.checked })}
                  className="rounded text-emerald-400 focus:ring-0 bg-slate-800 border-slate-700"
                />
                <span>Vektor Gerak Asap (FR-W7)</span>
              </span>
              <span className="text-[10px] text-emerald-400">Pusat Asap</span>
            </label>
          </div>
        </div>
      )}
    </div>
  );
};
