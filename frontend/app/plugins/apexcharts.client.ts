import { defineAsyncComponent, type Component } from 'vue'

export default defineNuxtPlugin(nuxtApp => {
  // ApexCharts reads its global defaults when a chart is instantiated.
  // Keep existing global chart options and set the platform font only.
  const host = window as Window & { Apex?: { chart?: Record<string, unknown> } & Record<string, unknown> }
  host.Apex = {
    ...host.Apex,
    chart: { ...host.Apex?.chart, fontFamily: 'Manrope, system-ui, sans-serif' },
  }
  nuxtApp.vueApp.component('apexchart', defineAsyncComponent(async () => (await import('vue3-apexcharts')).default as Component))
})
