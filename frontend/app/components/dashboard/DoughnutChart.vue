<script setup lang="ts">
import type { ApexOptions } from 'apexcharts'
import { defineAsyncComponent } from 'vue'
const ApexChart=defineAsyncComponent(()=>import('vue3-apexcharts').then(m=>m.default))
const props=defineProps<{labels:string[];values:number[];color?:string}>()
const theme=useThemeStore()
const options=computed<ApexOptions>(()=>({
  chart:{type:'donut',toolbar:{show:false},fontFamily:'Manrope, system-ui, sans-serif',background:'transparent',foreColor:theme.isDark?'#cbd5e1':'#64748b',animations:{enabled:false}},
  theme:{mode:theme.isDark?'dark':'light'},
  colors:['#304f7e','#eaa239','#c0392b','#007cc5','#8b73bd','#609346'],
  dataLabels:{enabled:false},legend:{show:true,position:'bottom',fontSize:'12px'},
  labels:props.labels,plotOptions:{pie:{donut:{size:'68%'}}},stroke:{width:2,colors:[theme.isDark?'#1b1f24':'#ffffff']},
  tooltip:{theme:theme.isDark?'dark':'light'}
}))
const series=computed(()=>props.values)
</script>
<template><div class="central-chart"><ApexChart v-if="values.length" type="donut" :height="270" :options="options" :series="series"/><div v-else class="chart-empty">Sem dados</div></div></template>
<style scoped>.central-chart{min-width:0;min-height:270px}.chart-empty{display:grid;place-items:center;min-height:270px;color:var(--color-text-muted)}</style>
