<script setup lang="ts">
import { HISTORY_ACTION_LABELS } from '~/types/history'

const props = defineProps<{ requestId: number }>()
const { listHistory } = useHistory()
const toast = useToast()
const entries = ref<Awaited<ReturnType<typeof listHistory>>>([])
const loading = ref(true)

onMounted(async () => {
  try { entries.value = await listHistory(props.requestId) }
  catch (error) { toast.error(extractErrorMessage(error, 'Não foi possível carregar o histórico.')) }
  finally { loading.value = false }
})
</script>

<template>
  <div class="history-section">
    <div class="section-heading">
      <span><UiIcon name="clock" :size="18" /></span>
      <div><h3>Histórico</h3><p>Linha do tempo das alterações.</p></div>
    </div>
    <div v-if="loading" class="history-loading"><UiSkeleton v-for="item in 3" :key="item" height="48px" /></div>
    <UiEmptyState v-else-if="entries.length === 0" icon="clock" title="Sem histórico" description="Nenhuma alteração registrada ainda." />
    <ul v-else class="timeline">
      <li v-for="entry in entries" :key="entry.id" class="timeline-item">
        <div class="timeline-dot"><span /></div>
        <div class="timeline-content">
          <p class="timeline-action">
            {{ HISTORY_ACTION_LABELS[entry.action] }}
            <span v-if="entry.previous_value || entry.new_value" class="timeline-detail">
              {{ entry.previous_value ? `de “${entry.previous_value}” ` : '' }}{{ entry.new_value ? `para “${entry.new_value}”` : '' }}
            </span>
          </p>
          <p class="timeline-meta"><strong>{{ entry.user.name }}</strong><span>{{ formatDate(entry.created_at) }}</span></p>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.section-heading { display: flex; align-items: center; gap: 10px; margin-bottom: 17px; }
.section-heading > span {
  width: 36px; height: 36px; display: grid; place-items: center;
  color: var(--color-accent); background: var(--color-accent-light); border-radius: 10px;
}
.section-heading h3 { margin: 0; font-size: 0.9rem; }
.section-heading p { margin: 3px 0 0; color: var(--color-text-muted); font-size: 0.62rem; }
.timeline { list-style: none; padding: 0; margin: 0; }
.timeline-item { position: relative; display: flex; gap: 12px; padding-bottom: 17px; }
.timeline-item:not(:last-child)::before {
  content: ''; position: absolute; left: 7px; top: 16px; bottom: 0; width: 1px; background: var(--color-border-strong);
}
.timeline-dot { width: 15px; height: 15px; display: grid; place-items: center; flex-shrink: 0; margin-top: 2px; border: 1px solid var(--color-primary-border); border-radius: 50%; background: var(--color-surface); }
.timeline-dot span { width: 5px; height: 5px; border-radius: 50%; background: var(--color-primary); box-shadow: 0 0 8px var(--color-primary); }
.timeline-content { min-width: 0; flex: 1; }
.timeline-action { margin: 0; color: var(--color-text-soft); font-size: 0.7rem; line-height: 1.5; font-weight: 600; }
.timeline-detail { display: block; margin-top: 3px; color: var(--color-text-muted); font-size: 0.62rem; font-weight: 400; }
.timeline-meta { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 5px; margin: 6px 0 0; color: var(--color-text-muted); font-size: 0.58rem; }
.timeline-meta strong { color: var(--color-primary); }
.history-loading { display: flex; flex-direction: column; gap: 8px; }
</style>
