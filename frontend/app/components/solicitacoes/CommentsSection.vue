<script setup lang="ts">
import type { Comment } from '~/types/comment'

const props = defineProps<{ requestId: number; integrated?:boolean }>()
const { listComments, createComment, updateComment, deleteComment } = useComments()
const { user, isAdmin } = useAuth()
const toast = useToast()

const comments = ref<Comment[]>([])
const loading = ref(true)
const newContent = ref('')
const publicReply=ref(false)
let sequence=0,disposed=false
const submitting = ref(false)
const editingId = ref<number | null>(null)
const editingContent = ref('')
const deletingId = ref<number | null>(null)

async function load(quiet=false) {
  const current=++sequence
  if(!quiet)loading.value=true
  try { const next=await listComments(props.requestId);if(!disposed&&current===sequence)comments.value=next }
  catch (error) { if(!quiet)toast.error(extractErrorMessage(error, 'Não foi possível carregar os comentários.'));if([401,403,404].includes((error as any)?.statusCode))comments.value=[] }
  finally { if(current===sequence)loading.value=false }
}
onMounted(()=>load())
useSilentRefresh(async()=>{if(!submitting.value&&!editingId.value&&!deletingId.value)await load(true)})
onBeforeUnmount(()=>{disposed=true;sequence++})

async function submit() {
  if (submitting.value || !newContent.value.trim()) return
  submitting.value = true
  try {
    comments.value.push(await createComment(props.requestId, newContent.value.trim(), props.integrated && publicReply.value))
    newContent.value = '';publicReply.value=false
    toast.success('Comentário adicionado.')
  } catch (error) { toast.error(extractErrorMessage(error)) }
  finally { submitting.value = false }
}

function canManage(comment: Comment) { return !comment.author.email.endsWith("@integration.example.com") && (isAdmin.value || comment.author.id === user.value?.id) }
function startEdit(comment: Comment) { editingId.value = comment.id; editingContent.value = comment.content }

async function saveEdit(comment: Comment) {
  try {
    const updated = await updateComment(comment.id, editingContent.value.trim())
    const index = comments.value.findIndex((item) => item.id === comment.id)
    if (index !== -1) comments.value[index] = updated
    editingId.value = null
    toast.success('Comentário atualizado.')
  } catch (error) { toast.error(extractErrorMessage(error)) }
}

async function remove(comment: Comment) {
  deletingId.value = comment.id
  try {
    await deleteComment(comment.id)
    comments.value = comments.value.filter((item) => item.id !== comment.id)
    toast.success('Comentário removido.')
  } catch (error) { toast.error(extractErrorMessage(error)) }
  finally { deletingId.value = null }
}
</script>

<template>
  <div class="comments-section">
    <div class="section-heading">
      <span><UiIcon name="users" :size="18" /></span>
      <div><h3>Comentários</h3><p>Registre observações e mantenha o contexto do atendimento.</p></div>
    </div>

    <form class="new-comment" @submit.prevent="submit">
      <VSelect v-if="integrated" v-model="publicReply" label="Visibilidade" :items="[{title:'Nota interna (somente atendimento)',value:false},{title:'Resposta pública ao cliente',value:true}]" hide-details/><textarea v-model="newContent" rows="3" placeholder="Escreva um comentário..." />
      <VBtn class="hub-action-button" color="primary" variant="flat" type="submit" :disabled="submitting || !newContent.trim()">
        <UiIcon name="arrowRight" :size="16" /> {{ submitting ? 'Enviando...' : 'Comentar' }}
      </VBtn>
    </form>

    <div v-if="loading" class="comments-loading"><UiSkeleton v-for="item in 2" :key="item" height="70px" /></div>
    <UiEmptyState v-else-if="comments.length === 0" icon="users" title="Nenhum comentário ainda" description="Seja o primeiro a comentar nesta solicitação." />

    <ul v-else class="comment-list">
      <li v-for="comment in comments" :key="comment.id" class="comment-item">
        <span class="comment-avatar">{{ comment.author.name.charAt(0).toUpperCase() }}</span>
        <div class="comment-body">
          <div class="comment-header">
            <span class="comment-author">{{ comment.author.name }} <small v-if="integrated">· {{comment.public_reply?"Público":"Interno"}}</small></span>
            <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
          </div>
          <template v-if="editingId === comment.id">
            <textarea v-model="editingContent" rows="2" />
            <div class="comment-actions">
              <VBtn class="hub-action-button" color="secondary" variant="outlined" @click="editingId = null" type="button">Cancelar</VBtn>
              <VBtn class="hub-action-button" color="primary" variant="flat" @click="saveEdit(comment)" type="button">Salvar</VBtn>
            </div>
          </template>
          <template v-else>
            <p class="comment-content">{{ comment.content }}</p>
            <div v-if="canManage(comment)" class="comment-actions">
              <button class="text-action" @click="startEdit(comment)"><UiIcon name="edit" :size="14" /> Editar</button>
              <button class="text-action danger" :disabled="deletingId === comment.id" @click="remove(comment)">
                <UiIcon name="trash" :size="14" /> {{ deletingId === comment.id ? 'Removendo...' : 'Excluir' }}
              </button>
            </div>
          </template>
        </div>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.section-heading { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.section-heading > span {
  width: 36px; height: 36px; display: grid; place-items: center;
  color: var(--color-primary); background: var(--color-primary-light); border-radius: 10px;
}
.section-heading h3 { margin: 0; font-size: 0.9rem; }
.section-heading p { margin: 3px 0 0; color: var(--color-text-muted); font-size: 0.64rem; }
.new-comment { display: flex; flex-direction: column; gap: 9px; margin-bottom: 20px; }
.new-comment textarea,
.comment-item textarea {
  width: 100%; padding: 12px 14px; color: var(--color-text); background: var(--color-surface-soft);
  border: 1px solid var(--color-border-strong); border-radius: 11px; resize: vertical;
}
.new-comment textarea:focus,
.comment-item textarea:focus { outline: none; border-color: var(--color-primary); box-shadow: 0 0 0 3px var(--focus-ring); }
.new-comment .btn { align-self: flex-end; }
.comment-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
.comment-item {
  display: flex; gap: 11px; padding: 13px; background: var(--surface-translucent);
  border: 1px solid var(--color-border); border-radius: 13px;
}
.comment-avatar {
  width: 34px; height: 34px; display: grid; place-items: center; flex-shrink: 0;
  color: var(--button-primary-text); background: var(--color-primary); border-radius: 10px; font-size: 0.72rem; font-weight: 800;
}
.comment-body { min-width: 0; flex: 1; }
.comment-header { display: flex; justify-content: space-between; gap: 12px; margin-bottom: 7px; }
.comment-author { color: var(--color-text-soft); font-size: 0.72rem; font-weight: 700; }
.comment-date { color: var(--color-text-muted); font-size: 0.59rem; }
.comment-content { margin: 0; color: var(--color-text-soft); font-size: 0.75rem; line-height: 1.65; white-space: pre-wrap; }
.comment-actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; }
.text-action {
  display: inline-flex; align-items: center; gap: 5px; padding: 3px 0;
  color: var(--color-text-muted); background: transparent; border: none; font-size: 0.62rem; cursor: pointer;
}
.text-action:hover { color: var(--color-primary); }
.text-action.danger:hover { color: var(--color-danger); }
.comments-loading { display: flex; flex-direction: column; gap: 10px; }
</style>
