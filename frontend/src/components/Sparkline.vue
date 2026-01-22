<template>
  <div class="sparkline-container" :style="{ height: height + 'px' }">
    <svg :width="width" :height="height" :viewBox="`0 0 ${width} ${height}`" preserveAspectRatio="none">
      <defs>
        <linearGradient :id="gradientId" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" :stop-color="color" stop-opacity="0.2" />
          <stop offset="100%" :stop-color="color" stop-opacity="0" />
        </linearGradient>
      </defs>
      
      <!-- Area Fill -->
      <path :d="areaPath" :fill="`url(#${gradientId})`" />
      
      <!-- Trend Line -->
      <path 
        :d="linePath" 
        fill="none" 
        :stroke="color" 
        stroke-width="2" 
        stroke-linecap="round" 
        stroke-linejoin="round" 
      />
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  data: number[]
  color?: string
  height?: number
}>()

const width = 100
const height = props.height || 40
const color = props.color || '#3b82f6'
const gradientId = `sparkline-gradient-${Math.random().toString(36).substr(2, 9)}`

const min = computed(() => Math.min(...props.data))
const max = computed(() => Math.max(...props.data))

const linePath = computed(() => {
  if (props.data.length < 2) return ''
  
  const range = max.value - min.value
  const step = width / (props.data.length - 1)
  
  return props.data.map((val, i) => {
    const x = i * step
    const y = range === 0 ? height / 2 : height - ((val - min.value) / range) * height
    return (i === 0 ? 'M' : 'L') + ` ${x},${y}`
  }).join(' ')
})

const areaPath = computed(() => {
  if (!linePath.value) return ''
  return linePath.value + ` L ${width},${height} L 0,${height} Z`
})
</script>

<style scoped>
.sparkline-container {
  width: 100%;
  overflow: hidden;
}
svg {
  width: 100%;
  height: 100%;
}
</style>
