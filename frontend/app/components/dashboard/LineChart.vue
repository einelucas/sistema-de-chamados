<script setup lang="ts">
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Filler,
} from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, LineElement, PointElement, CategoryScale, LinearScale, Filler)

const props = defineProps<{ labels: string[]; values: number[] }>()
const themeStore = useThemeStore()

const chartTheme = computed(() => themeStore.isDark
  ? {
      primary: '#00c596',
      fill: 'rgba(0, 197, 150, 0.10)',
      surface: '#121418',
      tooltip: '#252b33',
      tooltipTitle: '#fbfdfe',
      tooltipBody: '#d9dde1',
      border: '#39414b',
      muted: '#8c949d',
      grid: 'rgba(140, 148, 157, 0.10)',
    }
  : {
      primary: '#2563eb',
      fill: 'rgba(37, 99, 235, 0.10)',
      surface: '#ffffff',
      tooltip: '#0f172a',
      tooltipTitle: '#f8fafc',
      tooltipBody: '#cbd5e1',
      border: '#334155',
      muted: '#64748b',
      grid: 'rgba(100, 116, 139, 0.14)',
    })

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      label: 'Solicitações criadas',
      data: props.values,
      borderColor: chartTheme.value.primary,
      backgroundColor: chartTheme.value.fill,
      pointBackgroundColor: chartTheme.value.surface,
      pointBorderColor: chartTheme.value.primary,
      pointBorderWidth: 2,
      pointHoverRadius: 5,
      pointRadius: 3,
      tension: 0.38,
      fill: true,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: { intersect: false, mode: 'index' as const },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: chartTheme.value.tooltip,
      titleColor: chartTheme.value.tooltipTitle,
      bodyColor: chartTheme.value.tooltipBody,
      borderColor: chartTheme.value.border,
      borderWidth: 1,
      padding: 12,
      displayColors: false,
    },
  },
  scales: {
    x: {
      grid: { display: false },
      border: { display: false },
      ticks: { color: chartTheme.value.muted, font: { family: 'Montserrat', size: 10 } },
    },
    y: {
      beginAtZero: true,
      border: { display: false },
      grid: { color: chartTheme.value.grid },
      ticks: { precision: 0, color: chartTheme.value.muted, font: { family: 'Montserrat', size: 10 } },
    },
  },
}))
</script>

<template>
  <div class="chart-canvas"><Line :data="chartData" :options="chartOptions" /></div>
</template>

<style scoped>
.chart-canvas { height: 270px; }
</style>
