import React, { useState, useEffect } from 'react';
import { RegionId, SystemStatus, FrameIndexItem, FrameBundle, LayerVisibility } from './types';
import { fetchSystemStatus, fetchFrameIndex, fetchFrameBundle } from './api';
import { Header } from './components/Header';
import { StatusBanner } from './components/StatusBanner';
import { SummaryCards } from './components/SummaryCards';
import { MapView } from './components/MapView';
import { LayerControl } from './components/LayerControl';
import { UpwindPanel } from './components/UpwindPanel';
import { TimeSlider } from './components/TimeSlider';
import { AboutModal } from './components/AboutModal';
import { FooterBar } from './components/FooterBar';

export const App: React.FC = () => {
  const [regionId, setRegionId] = useState<RegionId>('riau');
  const [status, setStatus] = useState<SystemStatus | null>(null);
  const [indexItems, setIndexItems] = useState<FrameIndexItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const [bundle, setBundle] = useState<FrameBundle | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Status Lapisan Peta
  const [layers, setLayers] = useState<LayerVisibility>({
    smokeMask: true,
    smokeMaskOpacity: 0.85,
    smokeProb: false,
    smokeProbOpacity: 0.8,
    smokeUnc: false,
    smokeUncOpacity: 0.8,
    hotspots: true,
    wind: true,
    motionArrow: true
  });

  const [selectedHotspotId, setSelectedHotspotId] = useState<string | null>(null);
  const [isAboutOpen, setIsAboutOpen] = useState<boolean>(false);
  const [isLayerControlCollapsed, setIsLayerControlCollapsed] = useState<boolean>(true);
  const [isMobilePanelOpen, setIsMobilePanelOpen] = useState<boolean>(false);

  // 1. Muat Status Sistem Global
  useEffect(() => {
    fetchSystemStatus()
      .then(setStatus)
      .catch((err) => console.warn('Peringatan status sistem:', err));
  }, []);

  // 2. Muat Indeks Bingkai saat Wilayah Berganti (FR-W1)
  useEffect(() => {
    setLoading(true);
    setError(null);
    setSelectedHotspotId(null);

    fetchFrameIndex(regionId)
      .then((items) => {
        setIndexItems(items);
        if (items.length > 0) {
          // Buka bingkai terbaru (elemen terakhir indeks) secara default
          const latestIdx = items.length - 1;
          setCurrentIndex(latestIdx);
        }
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [regionId]);

  // 3. Muat Data Bingkai Terpilih (FR-W9, FR-W16: Hemat Data on-demand)
  useEffect(() => {
    if (indexItems.length === 0 || currentIndex < 0 || currentIndex >= indexItems.length) return;

    const item = indexItems[currentIndex];
    setLoading(true);

    fetchFrameBundle(regionId, item.timestamp_safe)
      .then((data) => {
        setBundle(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [regionId, indexItems, currentIndex]);

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-slate-950 font-sans">
      {/* FR-W17 & FR-W10: Header Utama dan Spanduk Data Tiruan */}
      <Header
        regionId={regionId}
        onRegionChange={(reg) => setRegionId(reg)}
        status={status}
        onOpenAbout={() => setIsAboutOpen(true)}
      />

      {/* FR-W11, FR-W12: Bar Status Data, Usia Data & Indikator Malam/Awan */}
      <StatusBanner
        status={status}
        currentFrame={bundle?.frame ?? null}
      />

      {/* FR-W8: Kartu Ringkasan (Luas Asap, Hotspot, Penanganan Desa) */}
      {bundle && (
        <SummaryCards
          frame={bundle.frame}
          hotspots={bundle.hotspots}
        />
      )}

      {/* Area Tengah: Peta Utama (FR-W1 s.d. FR-W5, FR-W7) & Panel Hulu Asap (FR-W6) */}
      <div className="relative flex-1 flex flex-col md:flex-row min-h-0 overflow-hidden">
        {/* Peta Interaktif Leaflet */}
        <div className="relative flex-1 h-full w-full">
          {error ? (
            <div className="flex items-center justify-center h-full text-red-400 p-4 text-center">
              <div>
                <p className="font-bold">Gagal memuat data:</p>
                <p className="text-xs text-slate-400 mt-1">{error}</p>
              </div>
            </div>
          ) : (
            <MapView
              regionId={regionId}
              bundle={bundle}
              layers={layers}
              selectedHotspotId={selectedHotspotId}
              onSelectHotspot={(id) => setSelectedHotspotId(id)}
            />
          )}

          {/* Floating Kontrol Lapisan Peta di pojok kiri atas */}
          <div className="absolute top-3 left-3 z-[1000]">
            <LayerControl
              layers={layers}
              onChange={setLayers}
              isCollapsed={isLayerControlCollapsed}
              onToggleCollapse={() => setIsLayerControlCollapsed(!isLayerControlCollapsed)}
            />
          </div>

          {/* Loading Indicator */}
          {loading && (
            <div className="absolute top-3 right-3 z-[1000] bg-slate-900/90 text-slate-200 text-xs px-2.5 py-1.5 rounded-lg border border-slate-700 shadow flex items-center gap-2">
              <span className="w-2.5 h-2.5 border-2 border-red-500 border-t-transparent rounded-full animate-spin" />
              <span>Memuat bingkai...</span>
            </div>
          )}
        </div>

        {/* FR-W6 & FR-W15: Panel Titik Panas Hulu Asap (Desktop Sidebar / Mobile Bottom Sheet) */}
        {bundle && (
          <UpwindPanel
            rankedSources={bundle.ranked_sources}
            hotspots={bundle.hotspots}
            selectedHotspotId={selectedHotspotId}
            onSelectHotspot={(id) => setSelectedHotspotId(id)}
            isOpenMobile={isMobilePanelOpen}
            onToggleMobile={() => setIsMobilePanelOpen(!isMobilePanelOpen)}
          />
        )}
      </div>

      {/* FR-W9: Slider Linimasa Waktu 24 Jam Terakhir */}
      <TimeSlider
        indexItems={indexItems}
        currentIndex={currentIndex}
        onSelectIndex={(idx) => setCurrentIndex(idx)}
      />

      {/* FR-W14: Atribusi kaki halaman */}
      <FooterBar status={status} onOpenAbout={() => setIsAboutOpen(true)} />

      {/* FR-W13, FR-W14: Modal Tentang & Keterbatasan */}
      <AboutModal
        isOpen={isAboutOpen}
        onClose={() => setIsAboutOpen(false)}
      />
    </div>
  );
};
