<script setup lang="ts">
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale)
ChartJS.defaults.font.family = 'Manrope, system-ui, sans-serif'

const props = defineProps<{ labels: string[]; values: number[]; color?: string }>()
const themeStore = useThemeStore()

const chartTheme = computed(() => themeStore.isDark
  ? {
      primary: '#00c596',
      primaryHover: '#19d8ad',
      tooltip: '#252b33',
      tooltipTitle: '#fbfdfe',
      tooltipBody: '#d9dde1',
      border: '#39414b',
      muted: '#8c949d',
      grid: 'rgba(140, 148, 157, 0.10)',
    }
  : {
      primary: '#2563eb',
      primaryHover: '#1d4ed8',
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
      label: 'Total',
      data: props.values,
      backgroundColor: props.color || chartTheme.value.primary,
      hoverBackgroundColor: props.color || chartTheme.value.primaryHover,
      borderRadius: 8,
      borderSkipped: false,
      maxBarThickness: 38,
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
      ticks: { color: chartTheme.value.muted, font: { family: 'Manrope', size: 10 } },
    },
    y: {
      beginAtZero: true,
      border: { display: false },
      grid: { color: chartTheme.value.grid },
      ticks: { precision: 0, color: chartTheme.value.muted, font: { family: 'Manrope', size: 10 } },
    },
  },
}))
</script>

<template>
  <div class="chart-canvas"><Bar :data="chartData" :options="chartOptions" /></div>
</template>

<style scoped>
.chart-canvas { height: 270px; }
</style>
