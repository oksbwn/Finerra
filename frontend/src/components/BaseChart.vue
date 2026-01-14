<template>
  <div class="chart-container" :style="{ height: height + 'px' }">
    <component
      :is="chartComponent"
      :data="chartData"
      :options="chartOptions"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Filler
} from 'chart.js'
import { Bar, Line, Doughnut } from 'vue-chartjs'

ChartJS.register(
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Filler
)

const props = defineProps<{
  type: 'bar' | 'line' | 'doughnut'
  data: any
  options?: any
  height?: number
}>()

const chartComponent = computed(() => {
  if (props.type === 'bar') return Bar
  if (props.type === 'line') return Line
  if (props.type === 'doughnut') return Doughnut
  return Bar
})

const defaultOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: props.type === 'doughnut',
      position: 'bottom' as const,
      labels: {
        usePointStyle: true,
        padding: 20,
        font: { size: 12 }
      }
    },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 12,
      cornerRadius: 8,
      titleFont: { size: 14, weight: 'bold' }
    }
  },
  scales: props.type !== 'doughnut' ? {
    y: {
      beginAtZero: true,
      grid: {
        display: true,
        drawBorder: false,
        color: 'rgba(0, 0, 0, 0.05)'
      },
      ticks: {
        callback: (value: any) => '₹' + value.toLocaleString()
      }
    },
    x: {
      grid: {
        display: false
      }
    }
  } : {}
}

const chartData = computed(() => props.data)
const chartOptions = computed(() => ({ ...defaultOptions, ...props.options }))
const height = computed(() => props.height || 300)

</script>

<style scoped>
.chart-container {
  width: 100%;
  position: relative;
}
</style>
