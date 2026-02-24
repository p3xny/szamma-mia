<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api.js'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const banners = ref([])
const loading = ref(true)
const error = ref('')
const saving = ref(false)

const showForm = ref(false)
const editingId = ref(null)
const form = ref({ title: '', subtitle: '', image_url: '', link_url: '', is_active: false })

const deleteTarget = ref(null)

async function fetchBanners() {
  loading.value = true
  try {
    const { data } = await api.get('/admin/event-banners')
    banners.value = data
  } catch {
    error.value = 'Nie udalo sie zaladowac banerow'
  } finally {
    loading.value = false
  }
}

function openAdd() {
  editingId.value = null
  form.value = { title: '', subtitle: '', image_url: '', link_url: '', is_active: false }
  showForm.value = true
}

function openEdit(banner) {
  editingId.value = banner.id
  form.value = {
    title: banner.title,
    subtitle: banner.subtitle || '',
    image_url: banner.image_url,
    link_url: banner.link_url || '',
    is_active: banner.is_active,
  }
  showForm.value = true
}

async function saveForm() {
  if (!form.value.title || !form.value.image_url) return
  saving.value = true
  error.value = ''
  try {
    const payload = {
      title: form.value.title,
      subtitle: form.value.subtitle || null,
      image_url: form.value.image_url,
      link_url: form.value.link_url || null,
      is_active: form.value.is_active,
    }
    if (editingId.value) {
      await api.patch(`/admin/event-banners/${editingId.value}`, payload)
    } else {
      await api.post('/admin/event-banners', payload)
    }
    showForm.value = false
    await fetchBanners()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Blad zapisu banera'
  } finally {
    saving.value = false
  }
}

async function toggleActive(banner) {
  try {
    await api.patch(`/admin/event-banners/${banner.id}`, { is_active: !banner.is_active })
    banner.is_active = !banner.is_active
  } catch {
    error.value = 'Nie udalo sie zmienic statusu'
  }
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  try {
    await api.delete(`/admin/event-banners/${deleteTarget.value.id}`)
    deleteTarget.value = null
    await fetchBanners()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Nie udalo sie usunac banera'
    deleteTarget.value = null
  }
}

onMounted(fetchBanners)
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Banery wydarzen</h1>
      <button class="btn btn-primary" @click="openAdd">Dodaj baner</button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <!-- Add/Edit modal -->
    <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
      <div class="modal">
        <h3>{{ editingId ? 'Edytuj baner' : 'Nowy baner' }}</h3>
        <form @submit.prevent="saveForm">
          <div class="form-group">
            <label>Tytul</label>
            <input v-model="form.title" class="form-control" required />
          </div>
          <div class="form-group">
            <label>Podtytul (opcjonalny)</label>
            <input v-model="form.subtitle" class="form-control" />
          </div>
          <div class="form-group">
            <label>URL obrazka</label>
            <input v-model="form.image_url" class="form-control" required placeholder="https://..." />
          </div>
          <div v-if="form.image_url" class="form-group">
            <label>Podglad</label>
            <div class="banner-preview">
              <img :src="form.image_url" alt="Podglad banera" />
            </div>
          </div>
          <div class="form-group">
            <label>Link URL (opcjonalny)</label>
            <input v-model="form.link_url" class="form-control" placeholder="https://..." />
          </div>
          <div class="form-group">
            <label style="display: flex; align-items: center; gap: 0.3rem">
              <input type="checkbox" v-model="form.is_active" /> Aktywny (widoczny na stronie)
            </label>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn btn-secondary" @click="showForm = false">Anuluj</button>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Zapisywanie...' : 'Zapisz' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Banner list -->
    <div v-if="loading" class="card">Ladowanie...</div>
    <div v-else-if="banners.length === 0" class="card" style="text-align: center; color: #999">
      Brak banerow. Dodaj pierwszy baner wydarzenia.
    </div>
    <div v-else class="banners-grid">
      <div v-for="banner in banners" :key="banner.id" class="banner-card card">
        <div class="banner-image">
          <img :src="banner.image_url" :alt="banner.title" />
          <span
            class="badge banner-status toggle-active"
            :class="banner.is_active ? 'badge-green' : 'badge-red'"
            @click="toggleActive(banner)"
          >
            {{ banner.is_active ? 'Aktywny' : 'Nieaktywny' }}
          </span>
        </div>
        <div class="banner-info">
          <h3>{{ banner.title }}</h3>
          <p v-if="banner.subtitle" class="banner-subtitle">{{ banner.subtitle }}</p>
          <p v-if="banner.link_url" class="banner-link">{{ banner.link_url }}</p>
        </div>
        <div class="banner-actions">
          <button class="btn btn-secondary btn-sm" @click="openEdit(banner)">Edytuj</button>
          <button class="btn btn-danger btn-sm" @click="deleteTarget = banner">Usun</button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      v-if="deleteTarget"
      :message="`Czy na pewno chcesz usunac baner &quot;${deleteTarget.title}&quot;?`"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>

<style scoped>
.banners-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.banner-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.banner-image {
  position: relative;
  height: 180px;
  overflow: hidden;
  border-radius: 8px 8px 0 0;
}

.banner-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.banner-status {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
}

.banner-info {
  padding: 0.75rem 1rem 0;
}

.banner-info h3 {
  margin: 0 0 0.25rem;
  font-size: 1rem;
}

.banner-subtitle {
  margin: 0;
  color: #666;
  font-size: 0.85rem;
}

.banner-link {
  margin: 0.25rem 0 0;
  font-size: 0.8rem;
  color: #1565c0;
  word-break: break-all;
}

.banner-actions {
  display: flex;
  gap: 0.3rem;
  padding: 0.75rem 1rem;
}

.banner-preview {
  border-radius: 6px;
  overflow: hidden;
  max-height: 140px;
}

.banner-preview img {
  width: 100%;
  height: 140px;
  object-fit: cover;
}
</style>
