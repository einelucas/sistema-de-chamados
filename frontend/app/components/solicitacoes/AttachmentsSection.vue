<script setup lang="ts">
// Seção de anexos: upload, listagem, download e remoção de arquivos vinculados à solicitação.
import type { Attachment } from '~/types/attachment'

const props = defineProps<{ requestId: number }>()
const { listAttachments, uploadAttachment, deleteAttachment, downloadAttachment } = useAttachments()
const toast = useToast()
const { user, isAdmin } = useAuth()

const attachments = ref<Attachment[]>([])
const loading = ref(true)
const uploading = ref(false)
const deletingId = ref<number | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

async function load() {
  loading.value = true
  try {
    attachments.value = await listAttachments(props.requestId)
  } catch (error) {
    toast.error(extractErrorMessage(error, 'Não foi possível carregar os anexos.'))
  } finally {
    loading.value = false
  }
}

onMounted(load)

async function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploading.value = true
  try {
    const attachment = await uploadAttachment(props.requestId, file)
    attachments.value.unshift(attachment)
    toast.success('Anexo enviado com sucesso.')
  } catch (error) {
    toast.error(extractErrorMessage(error, 'Não foi possível enviar o arquivo.'))
  } finally {
    uploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

async function remove(attachment: Attachment) {
  deletingId.value = attachment.id
  try {
    await deleteAttachment(attachment.id)
    attachments.value = attachments.value.filter((a) => a.id !== attachment.id)
    toast.success('Anexo removido.')
  } catch (error) {
    toast.error(extractErrorMessage(error))
  } finally {
    deletingId.value = null
  }
}

function canManage(attachment: Attachment) {
  return isAdmin.value || attachment.uploaded_by.id === user.value?.id
}
</script>

<template>
  <div class="attachments-section">
    <div class="attachments-header">
      <div class="section-title"><span><UiIcon name="paperclip" :size="18" /></span><div><h3>Anexos</h3><p>Arquivos relacionados à solicitação</p></div></div>
      <label class="btn btn-secondary upload-btn">
        <UiIcon name="plus" :size="16" /> {{ uploading ? 'Enviando...' : 'Anexar arquivo' }}
        <input ref="fileInput" type="file" hidden :disabled="uploading" @change="handleFileChange" />
      </label>
    </div>

    <div v-if="loading" class="attachments-loading">
      <UiSkeleton v-for="i in 2" :key="i" height="44px" />
    </div>

    <UiEmptyState v-else-if="attachments.length === 0" icon="paperclip" title="Nenhum anexo" description="Anexe arquivos relevantes para esta solicitação." />

    <ul v-else class="attachment-list">
      <li v-for="attachment in attachments" :key="attachment.id" class="attachment-item">
        <div class="attachment-info">
          <span class="attachment-icon"><UiIcon name="paperclip" :size="19" /></span>
          <div>
            <button class="attachment-name" @click="downloadAttachment(attachment.id, attachment.original_filename)">
              {{ attachment.original_filename }}
            </button>
            <p class="attachment-meta">{{ formatFileSize(attachment.size_bytes) }} · {{ attachment.uploaded_by.name }} · {{ formatDate(attachment.created_at) }}</p>
          </div>
        </div>
        <button v-if="canManage(attachment)" class="btn btn-ghost" :disabled="deletingId === attachment.id" @click="remove(attachment)">
          <UiIcon name="trash" :size="15" /> {{ deletingId === attachment.id ? 'Removendo...' : 'Remover' }}
        </button>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.attachments-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}
.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
}
.section-title > span {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border-radius: 10px;
}
.section-title h3 { margin: 0; font-size: 0.9rem; }
.section-title p { margin: 3px 0 0; color: var(--color-text-muted); font-size: 0.64rem; }
.upload-btn { cursor: pointer; }
.attachment-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.attachment-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 11px 12px;
  background: var(--surface-translucent);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  transition: border-color var(--transition-fast), background-color var(--transition-fast);
}
.attachment-item:hover {
  background: var(--color-surface-soft);
  border-color: var(--color-primary-border);
}
.attachment-info {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 11px;
}
.attachment-icon {
  width: 36px;
  height: 36px;
  display: grid;
  place-items: center;
  flex-shrink: 0;
  color: var(--color-primary);
  background: var(--color-primary-light);
  border-radius: 10px;
}
.attachment-name {
  max-width: 100%;
  overflow: hidden;
  padding: 0;
  color: var(--color-text-soft);
  background: none;
  border: none;
  text-align: left;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.76rem;
  font-weight: 700;
  cursor: pointer;
}
.attachment-name:hover { color: var(--color-primary); }
.attachment-meta {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 0.61rem;
}
.attachments-loading { display: flex; flex-direction: column; gap: 8px; }
@media (max-width: 620px) {
  .attachments-header { align-items: stretch; flex-direction: column; }
  .upload-btn { width: 100%; }
  .attachment-item { align-items: flex-start; flex-direction: column; }
}
</style>
