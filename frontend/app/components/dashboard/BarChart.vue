<script setup lang="ts">
import type { ApexOptions } from 'apexcharts'
import { defineAsyncComponent } from 'vue'
const ApexChart=defineAsyncComponent(()=>import('vue3-apexcharts').then(m=>m.default))
const props=defineProps<{labels:string[];values:number[];color?:string}>()
const theme=useThemeStore()
const options=computed<ApexOptions>(()=>({
  chart:{type:'bar',toolbar:{show:false},fontFamily:'Manrope, system-ui, sans-serif',background:'transparent',foreColor:theme.isDark?'#cbd5e1':'#64748b',animations:{enabled:false}},
  theme:{mode:theme.isDark?'dark':'light'},
  colors:[props.color||(theme.isDark?'#93b5e5':'#304f7e')],
  dataLabels:{enabled:false},legend:{show:false,position:'bottom',fontSize:'12px'},
  xaxis:{categories:props.labels,axisBorder:{show:false},axisTicks:{show:false}},yaxis:{min:0,decimalsInFloat:0},grid:{borderColor:theme.isDark?'#334155':'#e2e8f0',strokeDashArray:3},plotOptions:{bar:{borderRadius:5,columnWidth:'50%'}},
  tooltip:{theme:theme.isDark?'dark':'light'}
}))
const series=computed(()=>[{name:'Total',data:props.values}])
</script>
<template><div class="central-chart"><ApexChart v-if="values.length" type="bar" :height="270" :options="options" :series="series"/><div v-else class="chart-empty">Sem dados</div></div></template>
<style scoped>.central-chart{min-width:0;min-height:270px}.chart-empty{display:grid;place-items:center;min-height:270px;color:var(--color-text-muted)}</style>
