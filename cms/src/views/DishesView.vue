<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api.js'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const router = useRouter()
const dishes = ref([])
const categories = ref([])
const loading = ref(true)
const error = ref('')
const filterCategory = ref('')

// New dish form
const showAddForm = ref(false)
const newDish = ref({ name: '', category_id: '', base_price: '', image_url: '' })
const saving = ref(false)

// Delete confirm
const deleteTarget = ref(null)

const filteredDishes = computed(() => {
  if (!filterCategory.value) return dishes.value
  return dishes.value.filter((d) => d.category_id === Number(filterCategory.value))
})

async function fetchData() {
  loading.value = true
  try {
    const [d, c] = await Promise.all([
      api.get('/admin/dishes'),
      api.get('/admin/categories'),
    ])
    dishes.value = d.data
    categories.value = c.data
  } catch (e) {
    error.value = 'Nie udało się załadować danych'
  } finally {
    loading.value = false
  }
}

async function createDish() {
  if (!newDish.value.name || !newDish.value.category_id || !newDish.value.base_price) return
  saving.value = true
  try {
    await api.post('/admin/dishes', {
      name: newDish.value.name,
      category_id: Number(newDish.value.category_id),
      base_price: Number(newDish.value.base_price),
      image_url: newDish.value.image_url || null,
    })
    newDish.value = { name: '', category_id: '', base_price: '', image_url: '' }
    showAddForm.value = false
    await fetchData()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd tworzenia dania'
  } finally {
    saving.value = false
  }
}

async function toggleActive(dish) {
  try {
    await api.patch(`/admin/dishes/${dish.id}`, { is_active: !dish.is_active })
    dish.is_active = !dish.is_active
  } catch {
    error.value = 'Nie udało się zmienić statusu'
  }
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  try {
    await api.delete(`/admin/dishes/${deleteTarget.value.id}`)
    deleteTarget.value = null
    await fetchData()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Nie udało się usunąć dania'
    deleteTarget.value = null
  }
}

function getCategoryLabel(catId) {
  return categories.value.find((c) => c.id === catId)?.label || '—'
}

onMounted(fetchData)
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Dania</h1>
      <button class="btn btn-primary" @click="showAddForm = !showAddForm">
        {{ showAddForm ? 'Anuluj' : 'Dodaj danie' }}
      </button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <!-- Add dish form -->
    <div v-if="showAddForm" class="card" style="margin-bottom: 1rem">
      <h3 style="margin-bottom: 0.75rem">Nowe danie</h3>
      <form @submit.prevent="createDish" class="inline-form" style="flex-direction: column; align-items: stretch">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem">
          <div class="form-group">
            <label>Nazwa</label>
            <input v-model="newDish.name" class="form-control" required />
          </div>
          <div class="form-group">
            <label>Kategoria</label>
            <select v-model="newDish.category_id" class="form-control" required>
              <option value="" disabled>Wybierz...</option>
              <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.label }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Cena bazowa (zł)</label>
            <input v-model="newDish.base_price" type="number" step="0.01" min="0" class="form-control" required />
          </div>
          <div class="form-group">
            <label>URL obrazka</label>
            <input v-model="newDish.image_url" class="form-control" placeholder="https://..." />
          </div>
        </div>
        <div style="margin-top: 0.5rem">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? 'Zapisywanie...' : 'Dodaj' }}
          </button>
        </div>
      </form>
    </div>

    <!-- Filter -->
    <div class="card" style="padding: 0.75rem 1rem; margin-bottom: 1rem">
      <div style="display: flex; align-items: center; gap: 0.75rem">
        <label style="font-size: 0.85rem; font-weight: 600; white-space: nowrap">Filtruj kategorię:</label>
        <select v-model="filterCategory" class="form-control" style="max-width: 200px">
          <option value="">Wszystkie</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.label }}</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div v-if="loading" class="card">Ładowanie...</div>
    <div v-else class="card table-wrap" style="padding: 0">
      <table>
        <thead>
          <tr>
            <th>Nazwa</th>
            <th>Kategoria</th>
            <th>Cena</th>
            <th>Aktywne</th>
            <th>Akcje</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="dish in filteredDishes" :key="dish.id">
            <td>
              <strong @click="router.push(`/dishes/${dish.id}`)" style="cursor: pointer;">{{ dish.name }}</strong>
              <span v-if="dish.is_daily_special" class="badge badge-green" style="margin-left: 0.5rem">Specjalne</span>
            </td>
            <td>{{ getCategoryLabel(dish.category_id) }}</td>
            <td>{{ Number(dish.base_price).toFixed(2) }} zł</td>
            <td>
              <span
                class="badge toggle-active"
                :class="dish.is_active ? 'badge-green' : 'badge-red'"
                @click="toggleActive(dish)"
              >
                {{ dish.is_active ? 'Tak' : 'Nie' }}
              </span>
            </td>
            <td>
              <div style="display: flex; gap: 0.3rem">
                <button class="btn btn-secondary btn-sm" @click="router.push(`/dishes/${dish.id}`)">Edytuj</button>
                <button class="btn btn-danger btn-sm" @click="deleteTarget = dish">Usuń</button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredDishes.length === 0">
            <td colspan="5" style="text-align: center; color: #999">Brak dań</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Delete confirmation -->
    <ConfirmDialog
      v-if="deleteTarget"
      :message="`Czy na pewno chcesz usunąć &quot;${deleteTarget.name}&quot;?`"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>
