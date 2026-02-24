<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api.js'

const phone = ref('')
const reservationDuration = ref('2')
const etaStep = ref('10')
const etaDefault = ref('40')
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const success = ref('')

async function fetchSettings() {
  loading.value = true
  try {
    const { data } = await api.get('/admin/settings')
    phone.value = data.phone
    reservationDuration.value = data.reservation_duration || '2'
    etaStep.value = data.eta_step || '10'
    etaDefault.value = data.eta_default || '40'
  } catch {
    error.value = 'Nie udało się załadować ustawień'
  } finally {
    loading.value = false
  }
}

async function saveSettings() {
  saving.value = true
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.patch('/admin/settings', {
      phone: phone.value,
      reservation_duration: reservationDuration.value,
      eta_step: String(etaStep.value),
      eta_default: String(etaDefault.value),
    })
    phone.value = data.phone
    reservationDuration.value = data.reservation_duration
    etaStep.value = data.eta_step
    etaDefault.value = data.eta_default
    success.value = 'Ustawienia zapisane'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd zapisu ustawień'
  } finally {
    saving.value = false
  }
}

onMounted(fetchSettings)
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Ustawienia</h1>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>

    <div v-if="loading" class="card">Ładowanie...</div>
    <div v-else class="card">
      <form @submit.prevent="saveSettings">
        <h3 style="margin-bottom: 1rem">Dane kontaktowe</h3>
        <div class="form-group" style="max-width: 400px">
          <label>Numer telefonu</label>
          <input v-model="phone" class="form-control" placeholder="+48 123 456 789" />
        </div>

        <h3 style="margin: 1.5rem 0 1rem">Rezerwacje</h3>
        <div class="form-group" style="max-width: 400px">
          <label>Czas trwania rezerwacji (godziny)</label>
          <select v-model="reservationDuration" class="form-control">
            <option value="1">1 godzina</option>
            <option value="2">2 godziny</option>
            <option value="3">3 godziny</option>
          </select>
          <small style="color: #999; font-size: 0.8rem; margin-top: 0.25rem; display: block">
            Stolik jest blokowany na tyle godzin od momentu rezerwacji
          </small>
        </div>

        <h3 style="margin: 1.5rem 0 1rem">Zamówienia</h3>
        <div class="form-group" style="max-width: 400px">
          <label>Domyślny czas realizacji (minuty)</label>
          <input v-model="etaDefault" type="number" min="5" step="5" class="form-control" />
          <small style="color: #999; font-size: 0.8rem; margin-top: 0.25rem; display: block">
            Domyślna wartość ETA przy potwierdzaniu zamówienia
          </small>
        </div>
        <div class="form-group" style="max-width: 400px">
          <label>Krok zmiany czasu (minuty)</label>
          <input v-model="etaStep" type="number" min="5" step="5" class="form-control" />
          <small style="color: #999; font-size: 0.8rem; margin-top: 0.25rem; display: block">
            O ile minut zwiększa/zmniejsza się ETA przy kliknięciu + / −
          </small>
        </div>

        <button type="submit" class="btn btn-primary" :disabled="saving" style="margin-top: 0.5rem">
          {{ saving ? 'Zapisywanie...' : 'Zapisz' }}
        </button>
      </form>
    </div>
  </div>
</template>
