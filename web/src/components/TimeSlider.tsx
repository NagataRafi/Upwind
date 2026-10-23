import React, { useState, useEffect } from 'react';
import { FrameIndexItem } from '../types';
import { formatTimeOnlyWIB, formatToWIB } from '../api';
import { Play, Pause, SkipBack, SkipForward, Clock, Moon, CloudRain, AlertTriangle } from 'lucide-react';

interface TimeSliderProps {
  indexItems: FrameIndexItem[];
  currentIndex: number;
  onSelectIndex: (idx: number) => void;
}

export const TimeSlider: React.FC<TimeSliderProps> = ({
  indexItems,
  currentIndex,
  onSelectIndex
}) => {
  const [isPlaying, setIsPlaying] = useState(false);

  // Otomatisasi Play/Pause putar linimasa waktu
  useEffect(() => {
    if (!isPlaying) return;
    const timer = setInterval(() => {
      onSelectIndex((currentIndex + 1) % indexItems.length);
    }, 2000);
    return () => clearInterval(timer);
  }, [isPlaying, currentIndex, indexItems.length, onSelectIndex]);

  if (indexItems.length === 0) return null;

  const currentItem = indexItems[currentIndex];

  return (
    <div className="bg-slate-900/95 text-white border-t border-slate-800 px-3 py-2 z-20 backdrop-blur-md flex flex-col gap-1.5 flex-shrink-0">
      <div className="flex items-center justify-between gap-2 max-w-7xl mx-auto w-full">
        {/* Tombol Kontrol Playback */}
        <div className="flex items-center gap-1.5 flex-shrink-0">
          <button
            type="button"
            onClick={() => onSelectIndex(Math.max(0, currentIndex - 1))}
            disabled={currentIndex === 0}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 transition"
            title="Bingkai sebelumnya"
          >
            <SkipBack className="w-4 h-4" />
          </button>

          <button
            type="button"
            onClick={() => setIsPlaying(!isPlaying)}
            className="px-2.5 py-1.5 rounded-lg bg-red-600 hover:bg-red-500 text-white font-semibold text-xs flex items-center gap-1 shadow-sm transition"
            title={isPlaying ? 'Jeda otomatis' : 'Putar otomatis 24 jam'}
          >
            {isPlaying ? (
              <>
                <Pause className="w-3.5 h-3.5 fill-white" />
                <span className="hidden sm:inline">Jeda</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-white" />
                <span className="hidden sm:inline">Putar</span>
              </>
            )}
          </button>

          <button
            type="button"
            onClick={() => onSelectIndex(Math.min(indexItems.length - 1, currentIndex + 1))}
            disabled={currentIndex === indexItems.length - 1}
            className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-200 transition"
            title="Bingkai berikutnya"
          >
            <SkipForward className="w-4 h-4" />
          </button>
        </div>

        {/* FR-W9: Slider Waktu 24 Jam */}
        <div className="flex-1 flex flex-col justify-center px-2">
          <input
            type="range"
            min="0"
            max={indexItems.length - 1}
            value={currentIndex}
            onChange={(e) => onSelectIndex(parseInt(e.target.value, 10))}
            className="w-full accent-red-500 h-2 bg-slate-700 rounded-lg cursor-pointer"
          />
          {/* Tanda-tanda titik waktu penting */}
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>{formatTimeOnlyWIB(indexItems[0].timestamp_utc)}</span>
            <span className="text-slate-300 font-medium">Linimasa 24 Jam Terakhir (FR-W9)</span>
            <span>{formatTimeOnlyWIB(indexItems[indexItems.length - 1].timestamp_utc)}</span>
          </div>
        </div>

        {/* Tampilan Waktu Terpilih (WIB) */}
        <div className="text-right flex-shrink-0 min-w-[120px] bg-slate-800/80 px-2 py-1 rounded-lg border border-slate-700">
          <div className="text-xs font-bold text-white flex items-center justify-end gap-1">
            <Clock className="w-3 h-3 text-red-400" />
            <span>{formatTimeOnlyWIB(currentItem.timestamp_utc)}</span>
          </div>
          <div className="text-[10px] text-slate-400 truncate" title={`UTC: ${currentItem.timestamp_utc}`}>
            {formatToWIB(currentItem.timestamp_utc).split(' ')[0]}
          </div>
        </div>
      </div>
    </div>
  );
};
