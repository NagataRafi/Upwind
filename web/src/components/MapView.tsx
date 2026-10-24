import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { FrameBundle, LayerVisibility, RegionId, Hotspot } from '../types';
import { formatToWIB } from '../api';

interface MapViewProps {
  regionId: RegionId;
  bundle: FrameBundle | null;
  layers: LayerVisibility;
  selectedHotspotId: string | null;
  onSelectHotspot: (id: string | null) => void;
}

export const MapView: React.FC<MapViewProps> = ({
  regionId,
  bundle,
  layers,
  selectedHotspotId,
  onSelectHotspot
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);

  // Layer groups
  const maskLayerRef = useRef<L.ImageOverlay | null>(null);
  const probLayerRef = useRef<L.ImageOverlay | null>(null);
  const uncLayerRef = useRef<L.ImageOverlay | null>(null);
  const hotspotsLayerGroupRef = useRef<L.LayerGroup | null>(null);
  const windLayerGroupRef = useRef<L.LayerGroup | null>(null);
  const motionArrowGroupRef = useRef<L.LayerGroup | null>(null);

  // Markers map untuk pencarian cepat & penyorotan
  const markersRef = useRef<Map<string, L.CircleMarker>>(new Map());

  // Inisialisasi Peta Leaflet sekali
  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    // Koordinat awal (default Riau)
    const initialCenter: [number, number] = regionId === 'riau' ? [0.7, 102.0] : [-1.5, 113.5];
    const initialZoom = regionId === 'riau' ? 8 : 7;

    const map = L.map(mapContainerRef.current, {
      center: initialCenter,
      zoom: initialZoom,
      zoomControl: false,
      attributionControl: true
    });

    // Tile OpenStreetMap gratis, tanpa kunci API; atribusi wajib ditampilkan
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; Kontributor OpenStreetMap'
    }).addTo(map);

    // Zoom control di kanan bawah agar nyaman di mobile
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Inisialisasi layer groups
    hotspotsLayerGroupRef.current = L.layerGroup().addTo(map);
    windLayerGroupRef.current = L.layerGroup().addTo(map);
    motionArrowGroupRef.current = L.layerGroup().addTo(map);

    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Perubahan Wilayah (FR-W1): Pusatkan peta saat wilayah berganti
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map) return;

    if (regionId === 'riau') {
      map.flyTo([0.7, 102.0], 8, { duration: 1.0 });
    } else {
      map.flyTo([-1.5, 113.5], 7, { duration: 1.0 });
    }
  }, [regionId]);

  // Update Lapisan Asap, Titik Panas, Angin, dan Vektor Gerak saat data bingkai atau visibilitas berubah
  useEffect(() => {
    const map = mapInstanceRef.current;
    if (!map || !bundle) return;

    const frame = bundle.frame;
    // Bbox: [min_lon, min_lat, max_lon, max_lat] -> Leaflet LatLngBounds: [[min_lat, min_lon], [max_lat, max_lon]]
    const bounds = L.latLngBounds(
      [frame.bbox[1], frame.bbox[0]],
      [frame.bbox[3], frame.bbox[2]]
    );

    // 1. FR-W2: Mask Asap
    if (maskLayerRef.current) {
      map.removeLayer(maskLayerRef.current);
      maskLayerRef.current = null;
    }
    if (layers.smokeMask && frame.daylight && (frame.area_km2 ?? 0) > 0 && frame.mask_overlay) {
      maskLayerRef.current = L.imageOverlay(frame.mask_overlay, bounds, {
        opacity: layers.smokeMaskOpacity,
        interactive: false
      }).addTo(map);
    }

    // 2. FR-W3: Probabilitas Asap
    if (probLayerRef.current) {
      map.removeLayer(probLayerRef.current);
      probLayerRef.current = null;
    }
    if (layers.smokeProb && frame.daylight && (frame.area_km2 ?? 0) > 0 && frame.probability_overlay) {
      probLayerRef.current = L.imageOverlay(frame.probability_overlay, bounds, {
        opacity: layers.smokeProbOpacity,
        interactive: false
      }).addTo(map);
    }

    // 3. FR-W3: Ketidakpastian Asap
    if (uncLayerRef.current) {
      map.removeLayer(uncLayerRef.current);
      uncLayerRef.current = null;
    }
    if (layers.smokeUnc && frame.daylight && (frame.area_km2 ?? 0) > 0 && frame.uncertainty_overlay) {
      uncLayerRef.current = L.imageOverlay(frame.uncertainty_overlay, bounds, {
        opacity: layers.smokeUncOpacity,
        interactive: false
      }).addTo(map);
    }

    // 4. FR-W4: Titik Panas (Hotspots)
    if (hotspotsLayerGroupRef.current) {
      hotspotsLayerGroupRef.current.clearLayers();
      markersRef.current.clear();

      if (layers.hotspots) {
        bundle.hotspots.forEach((hp) => {
          const isSelected = selectedHotspotId === hp.id;
          const marker = L.circleMarker([hp.lat, hp.lon], {
            radius: hp.is_peat ? (isSelected ? 11 : 8) : (isSelected ? 9 : 6),
            color: hp.is_peat ? '#b91c1c' : '#d97706',
            weight: isSelected ? 3 : 2,
            fillColor: hp.is_peat ? '#ef4444' : '#f59e0b',
            fillOpacity: 0.9
          });

          // Popup detail sesuai FR-W4
          const popupHtml = `
            <div style="font-family: inherit; font-size: 12px; line-height: 1.4; min-width: 170px;">
              <div style="font-weight: 700; color: #1e293b; border-bottom: 1px solid #e2e8f0; padding-bottom: 3px; margin-bottom: 4px;">
                🔥 Titik Panas (${hp.id.replace(/^hp_[a-z]+_\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z_/, 'HP-')})
              </div>
              <div><strong>Waktu:</strong> ${formatToWIB(hp.time_utc)}</div>
              <div><strong>Sumber:</strong> ${hp.source}</div>
              <div><strong>Kepercayaan:</strong> ${typeof hp.confidence === 'number' ? hp.confidence + '%' : hp.confidence}</div>
              <div><strong>FRP (Daya):</strong> ${hp.frp} MW</div>
              <div><strong>Lahan Gambut:</strong> <span style="color: ${hp.is_peat ? '#b91c1c' : '#047857'}; font-weight: 600;">${hp.is_peat ? 'Ya (Kubah Gambut)' : 'Tidak (Mineral)'}</span></div>
            </div>
          `;
          marker.bindPopup(popupHtml);

          marker.on('click', () => {
            onSelectHotspot(hp.id);
          });

          marker.addTo(hotspotsLayerGroupRef.current!);
          markersRef.current.set(hp.id, marker);
        });
      }
    }

    // 5. FR-W5: Lapisan Panah Angin
    if (windLayerGroupRef.current) {
      windLayerGroupRef.current.clearLayers();

      if (layers.wind) {
        bundle.wind.forEach((w) => {
          // Hitung kecepatan dan sudut angin dari komponen u, v
          const speed = Math.sqrt(w.u * w.u + w.v * w.v);
          // Arah tiupan dari u dan v (arah ke mana angin bergerak dalam derajat matematika, lalu konversi ke rotasi ikon)
          const angleDeg = (Math.atan2(w.u, w.v) * 180) / Math.PI;

          const arrowHtml = `
            <div style="transform: rotate(${angleDeg}deg); transform-origin: center; display: flex; align-items: center; justify-content: center; width: 28px; height: 28px;">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L12 22M12 2L6 8M12 2L18 8" stroke="#0284c7" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          `;

          const icon = L.divIcon({
            html: arrowHtml,
            className: 'wind-arrow-icon',
            iconSize: [28, 28],
            iconAnchor: [14, 14]
          });

          const marker = L.marker([w.lat, w.lon], { icon, interactive: true });
          marker.bindTooltip(`Angin: ${speed.toFixed(1)} m/s (${(speed * 3.6).toFixed(1)} km/jam) pada ${w.height_m}m`, {
            direction: 'top',
            offset: [0, -10]
          });

          marker.addTo(windLayerGroupRef.current!);
        });
      }
    }

    // 6. FR-W7: Panah Arah Gerak Asap
    if (motionArrowGroupRef.current) {
      motionArrowGroupRef.current.clearLayers();

      if (layers.motionArrow && frame.daylight && (frame.area_km2 ?? 0) > 0 && frame.motion) {
        // Pusat perkiraan gumpalan asap
        const smokeCenterLat = regionId === 'riau' ? 1.35 : -2.2;
        const smokeCenterLon = regionId === 'riau' ? 101.8 : 113.9;

        if (frame.motion.quality !== 'unavailable' && frame.motion.direction_deg != null) {
          const dirDeg = frame.motion.direction_deg;
          const arrowHtml = `
            <div style="transform: rotate(${dirDeg}deg); transform-origin: center; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.4));">
              <div style="background: rgba(16, 185, 129, 0.95); color: white; padding: 4px 8px; border-radius: 9999px; font-weight: 800; font-size: 11px; display: flex; align-items: center; gap: 4px; border: 1.5px solid white;">
                <span>▲</span>
                <span style="white-space: nowrap;">${frame.motion.speed_kmh} km/jam (${dirDeg}°)</span>
              </div>
            </div>
          `;
          const icon = L.divIcon({
            html: arrowHtml,
            className: 'motion-arrow-icon',
            iconSize: [120, 30],
            iconAnchor: [60, 15]
          });

          const motionMarker = L.marker([smokeCenterLat, smokeCenterLon], { icon });
          motionMarker.bindTooltip(`Arah Gerak Asap: ${frame.motion.status_text}`, { permanent: false, direction: 'top' });
          motionMarker.addTo(motionArrowGroupRef.current);
        }
      }
    }
  }, [bundle, layers, regionId]);

  // Penyorotan Marker Titik Panas yang dipilih dari panel FR-W6
  useEffect(() => {
    if (!selectedHotspotId || !mapInstanceRef.current) return;
    const marker = markersRef.current.get(selectedHotspotId);
    if (marker) {
      const latLng = marker.getLatLng();
      mapInstanceRef.current.flyTo(latLng, Math.max(mapInstanceRef.current.getZoom(), 9), { duration: 0.8 });
      marker.openPopup();
    }
  }, [selectedHotspotId]);

  return (
    <div className="relative w-full h-full flex-1">
      {/* Container Leaflet */}
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
};
