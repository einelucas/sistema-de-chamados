<script setup lang="ts">
import { Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, ArcElement)

const props = defineProps<{ labels: string[]; values: number[] }>()
const themeStore = useThemeStore()

const chartTheme = computed(() => themeStore.isDark
  ? {
      palette: ['#00c596', '#d7c156', '#f06b78', '#66a8ff', '#b69cff', '#3ad08f'],
      surface: '#1b1f24',
      tooltip: '#252b33',
      tooltipTitle: '#fbfdfe',
      tooltipBody: '#d9dde1',
      border: '#39414b',
      muted: '#8c949d',
    }
  : {
      palette: ['#2563eb', '#c58a18', '#d93645', '#0284c7', '#7451c8', '#16864a'],
      surface: '#ffffff',
      tooltip: '#0f172a',
      tooltipTitle: '#f8fafc',
      tooltipBody: '#cbd5e1',
      border: '#334155',
      muted: '#64748b',
    })

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      data: props.values,
      backgroundColor: props.labels.map((_, index) => chartTheme.value.palette[index % chartTheme.value.palette.length]),
      hoverOffset: 7,
      borderColor: chartTheme.value.surface,
      borderWidth: 4,
    },
  ],
}))

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  cutout: '68%',
  plugins: {
    tooltip: {
      backgroundColor: chartTheme.value.tooltip,
      titleColor: chartTheme.value.tooltipTitle,
      bodyColor: chartTheme.value.tooltipBody,
      borderColor: chartTheme.value.border,
      borderWidth: 1,
      padding: 12,
    },
    legend: {
      position: 'bottom' as const,
      labels: {
        color: chartTheme.value.muted,
        boxWidth: 9,
        boxHeight: 9,
        padding: 16,
        usePointStyle: true,
        pointStyle: 'circle' as const,
        font: { family: 'Montserrat', size: 10 },
      },
    },
  },
}))
</script>

<template>
  <div class="chart-canvas"><Doughnut :data="chartData" :options="chartOptions" /></div>
</template>

<style scoped>
.chart-canvas { height: 270px; }
</style>
