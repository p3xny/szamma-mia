<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api.js'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

const coupons = ref([])
const loading = ref(true)
const error = ref('')
const saving = ref(false)

// Add/edit
const showForm = ref(false)
const editingId = ref(null)
const form = ref({ code: '', discount_type: 'percent', discount_percent: '', discount_amount: '', is_active: true })

// Delete
const deleteTarget = ref(null)

async function fetchCoupons() {
  loading.value = true
  try {
    const { data } = await api.get('/admin/coupons')
    coupons.value = data
  } catch {
    error.value = 'Nie udalo sie zaladowac kuponow'
  } finally {
    loading.value = false
  }
}

function openAdd() {
  editingId.value = null
  form.value = { code: '', discount_type: 'percent', discount_percent: '', discount_amount: '', is_active: true }
  showForm.value = true
}

function openEdit(coupon) {
  editingId.value = coupon.id
  form.value = {
    code: coupon.code,
    discount_type: coupon.discount_type || 'percent',
    discount_percent: coupon.discount_percent || '',
    discount_amount: coupon.discount_amount || '',
    is_active: coupon.is_active,
  }
  showForm.value = true
}

function buildPayload() {
  const payload = {
    code: form.value.code,
    discount_type: form.value.discount_type,
    is_active: form.value.is_active,
  }
  if (form.value.discount_type === 'percent') {
    payload.discount_percent = Number(form.value.discount_percent)
    payload.discount_amount = null
  } else {
    payload.discount_percent = 0
    payload.discount_amount = Number(form.value.discount_amount)
  }
  return payload
}

function isFormValid() {
  if (!form.value.code) return false
  if (form.value.discount_type === 'percent') {
    return form.value.discount_percent > 0
  }
  return form.value.discount_amount > 0
}

async function saveForm() {
  if (!isFormValid()) return
  saving.value = true
  error.value = ''
  try {
    const payload = buildPayload()
    if (editingId.value) {
      await api.patch(`/admin/coupons/${editingId.value}`, payload)
    } else {
      await api.post('/admin/coupons', payload)
    }
    showForm.value = false
    await fetchCoupons()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Blad zapisu kuponu'
  } finally {
    saving.value = false
  }
}

async function toggleActive(coupon) {
  try {
    await api.patch(`/admin/coupons/${coupon.id}`, { is_active: !coupon.is_active })
    coupon.is_active = !coupon.is_active
  } catch {
    error.value = 'Nie udalo sie zmienic statusu'
  }
}

async function confirmDelete() {
  if (!deleteTarget.value) return
  try {
    await api.delete(`/admin/coupons/${deleteTarget.value.id}`)
    deleteTarget.value = null
    await fetchCoupons()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Nie udalo sie usunac kuponu'
    deleteTarget.value = null
  }
}

function formatDiscount(coupon) {
  if (coupon.discount_type === 'fixed' && coupon.discount_amount) {
    return `-${coupon.discount_amount} zl`
  }
  return `-${coupon.discount_percent}%`
}

onMounted(fetchCoupons)
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Kupony</h1>
      <button class="btn btn-primary" @click="openAdd">Dodaj kupon</button>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <!-- Add/Edit modal -->
    <div v-if="showForm" class="modal-backdrop" @click.self="showForm = false">
      <div class="modal">
        <h3>{{ editingId ? 'Edytuj kupon' : 'Nowy kupon' }}</h3>
        <form @submit.prevent="saveForm">
          <div class="form-group">
            <label>Kod</label>
            <input v-model="form.code" class="form-control" required style="text-transform: uppercase" />
          </div>
          <div class="form-group">
            <label>Typ rabatu</label>
            <div class="discount-type-toggle">
              <button
                type="button"
                class="toggle-btn"
                :class="{ active: form.discount_type === 'percent' }"
                @click="form.discount_type = 'percent'"
              >
                Procentowy (%)
              </button>
              <button
                type="button"
                class="toggle-btn"
                :class="{ active: form.discount_type === 'fixed' }"
                @click="form.discount_type = 'fixed'"
              >
                Kwotowy (zl)
              </button>
            </div>
          </div>
          <div v-if="form.discount_type === 'percent'" class="form-group">
            <label>Rabat (%)</label>
            <input v-model="form.discount_percent" type="number" min="1" max="100" class="form-control" required />
          </div>
          <div v-else class="form-group">
            <label>Kwota rabatu (zl)</label>
            <input v-model="form.discount_amount" type="number" min="1" step="1" class="form-control" required />
          </div>
          <div class="form-group">
            <label style="display: flex; align-items: center; gap: 0.3rem">
              <input type="checkbox" v-model="form.is_active" /> Aktywny
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
    <div v-if="loading" class="card">Ladowanie...</div>
    <div v-else class="card table-wrap" style="padding: 0">
      <table>
        <thead>
          <tr>
            <th>Kod</th>
            <th>Typ</th>
            <th>Rabat</th>
            <th>Status</th>
            <th>Akcje</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="coupon in coupons" :key="coupon.id">
            <td><strong>{{ coupon.code }}</strong></td>
            <td>
              <span class="badge" :class="coupon.discount_type === 'fixed' ? 'badge-blue' : 'badge-gray'">
                {{ coupon.discount_type === 'fixed' ? 'Kwotowy' : 'Procentowy' }}
              </span>
            </td>
            <td>{{ formatDiscount(coupon) }}</td>
            <td>
              <span
                class="badge toggle-active"
                :class="coupon.is_active ? 'badge-green' : 'badge-red'"
                @click="toggleActive(coupon)"
              >
                {{ coupon.is_active ? 'Aktywny' : 'Nieaktywny' }}
              </span>
            </td>
            <td>
              <div style="display: flex; gap: 0.3rem">
                <button class="btn btn-secondary btn-sm" @click="openEdit(coupon)">Edytuj</button>
                <button class="btn btn-danger btn-sm" @click="deleteTarget = coupon">Usun</button>
              </div>
            </td>
          </tr>
          <tr v-if="coupons.length === 0">
            <td colspan="5" style="text-align: center; color: #999">Brak kuponow</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Delete confirmation -->
    <ConfirmDialog
      v-if="deleteTarget"
      :message="`Czy na pewno chcesz usunac kupon &quot;${deleteTarget.code}&quot;?`"
      @confirm="confirmDelete"
      @cancel="deleteTarget = null"
    />
  </div>
</template>

<style scoped>
.discount-type-toggle {
  display: flex;
  gap: 0;
  border: 1px solid #ddd;
  border-radius: 6px;
  overflow: hidden;
}

.toggle-btn {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: none;
  background: #f5f5f5;
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.toggle-btn.active {
  background: var(--green, #009246);
  color: white;
}

.toggle-btn:not(.active):hover {
  background: #e8e8e8;
}

.badge-blue {
  background: #e3f2fd;
  color: #1565c0;
}

.badge-gray {
  background: #f5f5f5;
  color: #666;
}
</style>
