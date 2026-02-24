<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api.js'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const props = defineProps({ id: [String, Number] })
const router = useRouter()

const dish = ref(null)
const categories = ref([])
const allIngredients = ref([])
const allExtras = ref([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')

// Add ingredient/extra forms
const showAddIngredient = ref(false)
const newIngredient = ref({ ingredient_id: '', is_included_by_default: true, additional_price: 0 })
const showAddExtra = ref(false)
const newExtra = ref({ extra_id: '', price: '' })

// New ingredient/extra creation
const newIngredientName = ref('')
const newExtraName = ref('')
const creatingIngredient = ref(false)
const creatingExtra = ref(false)

// Delete confirmation
const deleteTarget = ref(null)
const deleteType = ref('')

async function fetchAll() {
  loading.value = true
  try {
    const [d, cats, ings, exts] = await Promise.all([
      api.get(`/admin/dishes`),
      api.get('/admin/categories'),
      api.get('/admin/ingredients'),
      api.get('/admin/extras'),
    ])
    dish.value = d.data.find((x) => x.id === Number(props.id))
    if (!dish.value) {
      error.value = 'Danie nie znalezione'
      return
    }
    categories.value = cats.data
    allIngredients.value = ings.data
    allExtras.value = exts.data
  } catch {
    error.value = 'Nie udało się załadować danych'
  } finally {
    loading.value = false
  }
}

async function saveDish() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.patch(`/admin/dishes/${dish.value.id}`, {
      name: dish.value.name,
      category_id: dish.value.category_id,
      base_price: Number(dish.value.base_price),
      original_price: dish.value.original_price ? Number(dish.value.original_price) : null,
      image_url: dish.value.image_url || null,
      is_daily_special: dish.value.is_daily_special,
      is_active: dish.value.is_active,
      display_order: dish.value.display_order,
    })
    dish.value = data
    success.value = 'Zapisano pomyślnie'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd zapisu'
  } finally {
    saving.value = false
  }
}

// --- Ingredients ---

async function addIngredient() {
  if (!newIngredient.value.ingredient_id) return
  try {
    await api.post(`/admin/dishes/${dish.value.id}/ingredients`, {
      ingredient_id: Number(newIngredient.value.ingredient_id),
      is_included_by_default: newIngredient.value.is_included_by_default,
      additional_price: Number(newIngredient.value.additional_price) || 0,
    })
    newIngredient.value = { ingredient_id: '', is_included_by_default: true, additional_price: 0 }
    showAddIngredient.value = false
    await fetchAll()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd dodawania składnika'
  }
}

async function updateIngredient(di) {
  try {
    await api.patch(`/admin/dishes/${dish.value.id}/ingredients/${di.id}`, {
      is_included_by_default: di.is_included_by_default,
      additional_price: Number(di.additional_price),
    })
  } catch {
    error.value = 'Błąd aktualizacji składnika'
  }
}

async function createNewIngredient() {
  if (!newIngredientName.value.trim()) return
  creatingIngredient.value = true
  try {
    const { data } = await api.post('/admin/ingredients', { name: newIngredientName.value.trim() })
    allIngredients.value.push(data)
    newIngredient.value.ingredient_id = data.id
    newIngredientName.value = ''
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd tworzenia składnika'
  } finally {
    creatingIngredient.value = false
  }
}

// --- Extras ---

async function addExtra() {
  if (!newExtra.value.extra_id || !newExtra.value.price) return
  try {
    await api.post(`/admin/dishes/${dish.value.id}/extras`, {
      extra_id: Number(newExtra.value.extra_id),
      price: Number(newExtra.value.price),
    })
    newExtra.value = { extra_id: '', price: '' }
    showAddExtra.value = false
    await fetchAll()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd dodawania dodatku'
  }
}

async function updateExtra(de) {
  try {
    await api.patch(`/admin/dishes/${dish.value.id}/extras/${de.id}`, {
      price: Number(de.price),
    })
  } catch {
    error.value = 'Błąd aktualizacji dodatku'
  }
}

async function createNewExtra() {
  if (!newExtraName.value.trim()) return
  creatingExtra.value = true
  try {
    const { data } = await api.post('/admin/extras', { name: newExtraName.value.trim() })
    allExtras.value.push(data)
    newExtra.value.extra_id = data.id
    newExtraName.value = ''
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd tworzenia dodatku'
  } finally {
    creatingExtra.value = false
  }
}

// --- Delete ---

function requestDelete(item, type) {
  deleteTarget.value = item
  deleteType.value = type
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  try {
    if (deleteType.value === 'ingredient') {
      await api.delete(`/admin/dishes/${dish.value.id}/ingredients/${deleteTarget.value.id}`)
    } else {
      await api.delete(`/admin/dishes/${dish.value.id}/extras/${deleteTarget.value.id}`)
    }
    deleteTarget.value = null
    await fetchAll()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd usuwania'
    deleteTarget.value = null
  }
}

onMounted(fetchAll)
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Edytuj danie</h1>
      <button class="btn btn-secondary" @click="router.push('/dishes')">Wróć do listy</button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div v-if="loading" class="card">Ładowanie...</div>

    <template v-else-if="dish">
      <!-- Dish info -->
      <div class="card">
        <h3 style="margin-bottom: 1rem">Informacje o daniu</h3>
        <form @submit.prevent="saveDish">
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem">
            <div class="form-group">
              <label>Nazwa</label>
              <input v-model="dish.name" class="form-control" required />
            </div>
            <div class="form-group">
              <label>Kategoria</label>
              <select v-model="dish.category_id" class="form-control" required>
                <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.label }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>Cena bazowa (zł)</label>
              <input v-model="dish.base_price" type="number" step="0.01" min="0" class="form-control" required />
            </div>
            <div class="form-group">
              <label>Cena oryginalna (zł) — opcjonalnie</label>
              <input v-model="dish.original_price" type="number" step="0.01" min="0" class="form-control" />
            </div>
            <div class="form-group" style="grid-column: 1 / -1">
              <label>URL obrazka</label>
              <input v-model="dish.image_url" class="form-control" />
            </div>
            <div class="form-group">
              <label>Kolejność wyświetlania</label>
              <input v-model.number="dish.display_order" type="number" class="form-control" />
            </div>
            <div class="form-group" style="display: flex; gap: 1.5rem; align-items: center; padding-top: 1.5rem">
              <label style="margin-bottom: 0; display: flex; align-items: center; gap: 0.3rem">
                <input type="checkbox" v-model="dish.is_daily_special" /> Danie dnia
              </label>
              <label style="margin-bottom: 0; display: flex; align-items: center; gap: 0.3rem">
                <input type="checkbox" v-model="dish.is_active" /> Aktywne
              </label>
            </div>
          </div>
          <button type="submit" class="btn btn-primary" :disabled="saving" style="margin-top: 0.75rem">
            {{ saving ? 'Zapisywanie...' : 'Zapisz zmiany' }}
          </button>
        </form>
      </div>

      <!-- Ingredients -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem">
          <h3>Składniki ({{ dish.ingredients.length }})</h3>
          <button class="btn btn-sm btn-primary" @click="showAddIngredient = !showAddIngredient">
            {{ showAddIngredient ? 'Anuluj' : 'Dodaj składnik' }}
          </button>
        </div>

        <!-- Add ingredient form -->
        <div v-if="showAddIngredient" style="background: var(--light-gray); padding: 0.75rem; border-radius: 6px; margin-bottom: 0.75rem">
          <div style="display: flex; gap: 0.5rem; align-items: flex-end; flex-wrap: wrap">
            <div class="form-group" style="flex: 1; min-width: 150px">
              <label>Składnik</label>
              <select v-model="newIngredient.ingredient_id" class="form-control">
                <option value="" disabled>Wybierz...</option>
                <option v-for="i in allIngredients" :key="i.id" :value="i.id">{{ i.name }}</option>
              </select>
            </div>
            <div class="form-group" style="width: 100px">
              <label>Cena dod.</label>
              <input v-model="newIngredient.additional_price" type="number" step="0.01" min="0" class="form-control" />
            </div>
            <div class="form-group" style="display: flex; align-items: center; gap: 0.3rem; padding-bottom: 0.1rem">
              <input type="checkbox" v-model="newIngredient.is_included_by_default" id="new-ing-default" />
              <label for="new-ing-default" style="margin-bottom: 0">Domyślnie</label>
            </div>
            <button class="btn btn-primary btn-sm" @click="addIngredient">Dodaj</button>
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: flex-end; margin-top: 0.5rem">
            <div class="form-group" style="flex: 1">
              <label>Lub utwórz nowy składnik</label>
              <input v-model="newIngredientName" class="form-control" placeholder="Nazwa składnika..." />
            </div>
            <button class="btn btn-secondary btn-sm" :disabled="creatingIngredient" @click="createNewIngredient">
              Utwórz
            </button>
          </div>
        </div>

        <div v-if="dish.ingredients.length === 0" style="color: #999; font-size: 0.9rem">
          Brak składników — dodaj powyżej.
        </div>
        <table v-else>
          <thead>
            <tr>
              <th>Nazwa</th>
              <th>Domyślnie</th>
              <th>Cena dodatkowa</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="di in dish.ingredients" :key="di.id">
              <td>{{ di.ingredient_name }}</td>
              <td>
                <input
                  type="checkbox"
                  :checked="di.is_included_by_default"
                  @change="di.is_included_by_default = $event.target.checked; updateIngredient(di)"
                />
              </td>
              <td>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  :value="di.additional_price"
                  class="form-control"
                  style="width: 90px; display: inline"
                  @change="di.additional_price = $event.target.value; updateIngredient(di)"
                />
                zł
              </td>
              <td>
                <button class="btn btn-danger btn-sm" @click="requestDelete(di, 'ingredient')">Usuń</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Extras -->
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem">
          <h3>Dodatki ({{ dish.extras.length }})</h3>
          <button class="btn btn-sm btn-primary" @click="showAddExtra = !showAddExtra">
            {{ showAddExtra ? 'Anuluj' : 'Dodaj dodatek' }}
          </button>
        </div>

        <!-- Add extra form -->
        <div v-if="showAddExtra" style="background: var(--light-gray); padding: 0.75rem; border-radius: 6px; margin-bottom: 0.75rem">
          <div style="display: flex; gap: 0.5rem; align-items: flex-end; flex-wrap: wrap">
            <div class="form-group" style="flex: 1; min-width: 150px">
              <label>Dodatek</label>
              <select v-model="newExtra.extra_id" class="form-control">
                <option value="" disabled>Wybierz...</option>
                <option v-for="e in allExtras" :key="e.id" :value="e.id">{{ e.name }}</option>
              </select>
            </div>
            <div class="form-group" style="width: 100px">
              <label>Cena</label>
              <input v-model="newExtra.price" type="number" step="0.01" min="0.01" class="form-control" required />
            </div>
            <button class="btn btn-primary btn-sm" @click="addExtra">Dodaj</button>
          </div>
          <div style="display: flex; gap: 0.5rem; align-items: flex-end; margin-top: 0.5rem">
            <div class="form-group" style="flex: 1">
              <label>Lub utwórz nowy dodatek</label>
              <input v-model="newExtraName" class="form-control" placeholder="Nazwa dodatku..." />
            </div>
            <button class="btn btn-secondary btn-sm" :disabled="creatingExtra" @click="createNewExtra">
              Utwórz
            </button>
          </div>
        </div>

        <div v-if="dish.extras.length === 0" style="color: #999; font-size: 0.9rem">
          Brak dodatków — dodaj powyżej.
        </div>
        <table v-else>
          <thead>
            <tr>
              <th>Nazwa</th>
              <th>Cena</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="de in dish.extras" :key="de.id">
              <td>{{ de.extra_name }}</td>
              <td>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  :value="de.price"
                  class="form-control"
                  style="width: 90px; display: inline"
                  @change="de.price = $event.target.value; updateExtra(de)"
                />
                zł
              </td>
              <td>
                <button class="btn btn-danger btn-sm" @click="requestDelete(de, 'extra')">Usuń</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>

    <!-- Delete confirmation -->
    <ConfirmDialog
      v-if="deleteTarget"
      :message="`Czy na pewno chcesz usunąć &quot;${deleteTarget.ingredient_name || deleteTarget.extra_name}&quot;?`"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>
