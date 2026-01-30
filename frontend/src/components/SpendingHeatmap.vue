<template>
    <div class="heatmap-container glass-card">
        <div class="heatmap-header">
            <div class="header-info">
                <h3 class="heatmap-title">Spending Heatmap 🗺️</h3>
                <p class="heatmap-subtitle">Visualizing expenses by location</p>
            </div>
            <div class="header-actions">
                <div class="intensity-legend">
                    <span class="legend-label">Low</span>
                    <div class="gradient-bar"></div>
                    <span class="legend-label">High</span>
                </div>
            </div>
        </div>

        <div id="map" class="heatmap-canvas" ref="mapContainer"></div>

        <div v-if="!hasLocationData" class="no-data-overlay">
            <div class="empty-state">
                <div class="empty-icon">📍</div>
                <h3>No Geolocation Data</h3>
                <p>Transactions with location coordinates will appear here.</p>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import 'leaflet.heat'

interface HeatmapDataPoint {
    latitude: number
    longitude: number
    amount: number
    recipient?: string
}

const props = defineProps<{
    data: HeatmapDataPoint[]
}>()

const mapContainer = ref<HTMLElement | null>(null)
let map: L.Map | null = null
let heatLayer: any = null

const hasLocationData = computed(() => props.data && props.data.length > 0)

const initMap = () => {
    if (!mapContainer.value) return

    // Default center (can be tuned or detected from data)
    const center: L.LatLngExpression = hasLocationData.value
        ? [props.data[0].latitude, props.data[0].longitude]
        : [20.5937, 78.9629] // India center fallback

    map = L.map(mapContainer.value, {
        zoomControl: false,
        attributionControl: false
    }).setView(center, 13)

    // Premium Dark Mode Tiles
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
    }).addTo(map)

    // Add zoom control manually to bottom right
    L.control.zoom({
        position: 'bottomright'
    }).addTo(map)

    updateHeatmap()
}

const updateHeatmap = () => {
    if (!map) return

    if (heatLayer) {
        map.removeLayer(heatLayer)
    }

    if (!hasLocationData.value) return

    // Prepare heatmap data: [lat, lng, intensity]
    const heatPoints = props.data.map(p => {
        // Normalize intensity based on amount
        // Simple log scale or linear scale
        const intensity = Math.min(Math.abs(p.amount) / 1000, 1)
        return [p.latitude, p.longitude, intensity]
    })

    // @ts-ignore - leaflet.heat is not in types
    heatLayer = L.heatLayer(heatPoints as any, {
        radius: 25,
        blur: 15,
        maxZoom: 17,
        gradient: {
            0.4: '#3b82f6', // blue
            0.6: '#10b981', // green
            0.7: '#f59e0b', // amber
            0.8: '#ef4444'  // red
        }
    }).addTo(map)

    // Fit bounds if we have multiple points
    if (props.data.length > 1) {
        const bounds = L.latLngBounds(props.data.map(p => [p.latitude, p.longitude]))
        map.fitBounds(bounds, { padding: [50, 50] })
    }
}

watch(() => props.data, () => {
    updateHeatmap()
}, { deep: true })

onMounted(() => {
    // Small timeout to ensure container has dimensions
    setTimeout(initMap, 100)
})

onUnmounted(() => {
    if (map) {
        map.remove()
        map = null
    }
})
</script>

<style scoped>
.heatmap-container {
    display: flex;
    flex-direction: column;
    height: 600px;
    position: relative;
    overflow: hidden;
    background: #111827;
    border-color: rgba(255, 255, 255, 0.1);
}

.heatmap-header {
    padding: 1.25rem 1.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    z-index: 1000;
    background: rgba(17, 24, 39, 0.8);
    backdrop-filter: blur(8px);
}

.heatmap-title {
    font-size: 1.125rem;
    font-weight: 700;
    color: white;
    margin: 0;
}

.heatmap-subtitle {
    font-size: 0.8125rem;
    color: #94a3b8;
    margin: 0.25rem 0 0 0;
}

.heatmap-canvas {
    flex: 1;
    width: 100%;
    z-index: 1;
}

.intensity-legend {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: rgba(255, 255, 255, 0.05);
    padding: 0.5rem 1rem;
    border-radius: 2rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.legend-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #94a3b8;
    text-transform: uppercase;
}

.gradient-bar {
    width: 100px;
    height: 6px;
    border-radius: 3px;
    background: linear-gradient(to right, #3b82f6, #10b981, #f59e0b, #ef4444);
}

.no-data-overlay {
    position: absolute;
    inset: 0;
    top: 76px;
    /* Below header */
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(17, 24, 39, 0.6);
    backdrop-filter: blur(4px);
    z-index: 10;
}

.empty-state {
    text-align: center;
    color: white;
}

.empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 10px rgba(59, 130, 246, 0.5));
}

.empty-state h3 {
    margin: 0 0 0.5rem 0;
    font-size: 1.25rem;
}

.empty-state p {
    color: #94a3b8;
    max-width: 250px;
}

/* Leaflet Overrides */
:deep(.leaflet-popup-content-wrapper) {
    background: rgba(30, 41, 59, 0.9);
    color: white;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 0.75rem;
}

:deep(.leaflet-popup-tip) {
    background: rgba(30, 41, 59, 0.9);
}
</style>
