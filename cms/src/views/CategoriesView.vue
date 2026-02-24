<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api.js'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const categories = ref([])
const loading = ref(true)
const error = ref('')
const saving = ref(false)

// Add / edit
const showForm = ref(false)
const editingId = ref(null)
const form = ref({ key: '', label: '', display_order: 0, is_active: true })

// Delete
const deleteTarget = ref(null)

async function fetchCategories() {
  loading.value = true
  try {
    const { data } = await api.get('/admin/categories')
    categories.value = data
  } catch {
    error.value = 'Nie udało się załadować kategorii'
  } finally {
    loading.value = false
  }
}

function openAdd() {
  editingId.value = null
  form.value = { key: '', label: '', display_order: 0, is_active: true }
  showForm.value = true
}

function openEdit(cat) {
  editingId.value = cat.id
  form.value = {
    key: cat.key,
    label: cat.label,
    display_order: cat.display_order,
    is_active: cat.is_active,
  }
  showForm.value = true
}

async function saveForm() {
  if (!form.value.key.trim() || !form.value.label.trim()) return
  saving.value = true
  error.value = ''
  try {
    if (editingId.value) {
      await api.patch(`/admin/categories/${editingId.value}`, {
        key: form.value.key.trim(),
        label: form.value.label.trim(),
        display_order: Number(form.value.display_order),
        is_active: form.value.is_active,
      })
    } else {
      await api.post('/admin/categories', {
        key: form.value.key.trim(),
        label: form.value.label.trim(),
        display_order: Number(form.value.display_order),
        is_active: form.value.is_active,
      })
    }
    showForm.value = false
    await fetchCategories()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd zapisu kategorii'
  } finally {
    saving.value = false
  }
}

async function toggleActive(cat) {
  try {
    await api.patch(`/admin/categories/${cat.id}`, { is_active: !cat.is_active })
    cat.is_active = !cat.is_active
  } catch {
    error.value = 'Nie udało się zmienić statusu'
  }
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  try {
    await api.delete(`/admin/categories/${deleteTarget.value.id}`)
    deleteTarget.value = null
    await fetchCategories()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Nie udało się usunąć kategorii'
    deleteTarget.value = null
  }
}

onMounted(fetchCategories)
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Kategorie</h1>
      <button class="btn btn-primary" @click="openAdd">Dodaj kategorię</button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <!-- Add / Edit modal -->
    <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
      <div class="modal">
        <h3>{{ editingId ? 'Edytuj kategorię' : 'Nowa kategoria' }}</h3>
        <form @submit.prevent="saveForm">
          <div class="form-group">
            <label>Klucz (slug)</label>
            <input v-model="form.key" class="form-control" required placeholder="np. pizza, pasta" />
          </div>
          <div class="form-group">
            <label>Nazwa wyświetlana</label>
            <input v-model="form.label" class="form-control" required placeholder="np. Pizza, Makarony" />
          </div>
          <div class="form-group">
            <label>Kolejność wyświetlania</label>
            <input v-model.number="form.display_order" type="number" class="form-control" />
          </div>
          <div class="form-group">
            <label style="display: flex; align-items: center; gap: 0.3rem">
              <input type="checkbox" v-model="form.is_active" /> Aktywna
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

    <!-- Table -->
    <div v-if="loading" class="card">Ładowanie...</div>
    <div v-else class="card table-wrap" style="padding: 0">
      <table>
        <thead>
          <tr>
            <th>Kolejność</th>
            <th>Klucz</th>
            <th>Nazwa</th>
            <th>Aktywna</th>
            <th>Akcje</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cat in categories" :key="cat.id">
            <td>{{ cat.display_order }}</td>
            <td><code>{{ cat.key }}</code></td>
            <td><strong>{{ cat.label }}</strong></td>
            <td>
              <span
                class="badge toggle-active"
                :class="cat.is_active ? 'badge-green' : 'badge-red'"
                @click="toggleActive(cat)"
              >
                {{ cat.is_active ? 'Tak' : 'Nie' }}
              </span>
            </td>
            <td>
              <div style="display: flex; gap: 0.3rem">
                <button class="btn btn-secondary btn-sm" @click="openEdit(cat)">Edytuj</button>
                <button class="btn btn-danger btn-sm" @click="deleteTarget = cat">Usuń</button>
              </div>
            </td>
          </tr>
          <tr v-if="categories.length === 0">
            <td colspan="5" style="text-align: center; color: #999">Brak kategorii</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Delete confirmation -->
    <ConfirmDialog
      v-if="deleteTarget"
      :message="`Czy na pewno chcesz usunąć kategorię &quot;${deleteTarget.label}&quot;?`"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>
