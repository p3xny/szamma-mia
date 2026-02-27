<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { api } from '@/composables/useApi'

const { isAuthenticated, user } = useAuth()

const tables = ref([])
const blocked = ref({})
const durationHours = ref(2)
const loading = ref(true)
const error = ref('')
const success = ref('')

// Date / time selection
const selectedDate = ref(todayStr())
const selectedTime = ref('')

// Reservation form
const selectedTable = ref(null)
const guestsCount = ref(2)
const notes = ref('')
const submitting = ref(false)

// Phone dialog for guests
const showPhoneDialog = ref(false)
const phoneNumber = ref('+48 123 456 789')
const phoneHref = ref('tel:+48123456789')

// User already has reservation for this date
const userHasReservation = ref(false)
const userReservation = ref(null)

function userResTableLabel() {
  if (!userReservation.value) return ''
  const t = tables.value.find(t => t.id === userReservation.value.table_id)
  return t ? t.label : ''
}

function todayStr() {
  const d = new Date()
  return d.toISOString().slice(0, 10)
}

function tomorrowStr() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().slice(0, 10)
}

const dateOptions = computed(() => [
  { value: todayStr(), label: 'Dzisiaj' },
  { value: tomorrowStr(), label: 'Jutro' },
])

const timeSlots = computed(() => {
  const slots = []
  for (let h = 12; h <= 22; h++) {
    slots.push(`${String(h).padStart(2, '0')}:00`)
    if (h < 22) slots.push(`${String(h).padStart(2, '0')}:30`)
  }
  return slots
})

const availableTimeSlots = computed(() => {
  if (selectedDate.value !== todayStr()) return timeSlots.value
  const now = new Date()
  const minTime = new Date(now.getTime() + 60 * 60 * 1000)
  const minH = minTime.getHours()
  const minM = minTime.getMinutes()
  return timeSlots.value.filter(slot => {
    const [h, m] = slot.split(':').map(Number)
    return h > minH || (h === minH && m >= minM)
  })
})

const indoorTables = computed(() => tables.value.filter(t => t.zone === 'indoor'))
const outdoorTables = computed(() => tables.value.filter(t => t.zone === 'outdoor'))

function isTableBlocked(tableId) {
  if (!selectedTime.value) return false
  const tableBlocked = blocked.value[String(tableId)]
  if (!tableBlocked) return false
  return tableBlocked.includes(selectedTime.value)
}

function tableStatus(tableId) {
  if (!selectedTime.value) return 'no-time'
  if (isTableBlocked(tableId)) return 'reserved'
  if (userHasReservation.value) return 'user-blocked'
  return 'free'
}

function selectTable(table) {
  if (!selectedTime.value) return
  if (isTableBlocked(table.id)) return
  if (!isAuthenticated.value) {
    showPhoneDialog.value = true
    return
  }
  if (userHasReservation.value) return
  selectedTable.value = table
  guestsCount.value = 2
  notes.value = ''
}

async function fetchTables() {
  try {
    const { data } = await api.get('/tables')
    tables.value = data
  } catch {
    error.value = 'Nie udało się załadować stolików'
  }
}

async function fetchAvailability() {
  if (!selectedDate.value) return
  try {
    const { data } = await api.get(`/reservations/availability?date_str=${selectedDate.value}`)
    blocked.value = data.blocked || {}
    durationHours.value = data.duration_hours || 2
    userHasReservation.value = data.user_has_reservation || false
    userReservation.value = data.user_reservation || null
  } catch {
    // silent - tables will show as free
    blocked.value = {}
    userHasReservation.value = false
    userReservation.value = null
  }
  loading.value = false
}

async function fetchPhone() {
  try {
    const res = await api.get('/site-config')
    if (res.data.phone) {
      phoneNumber.value = res.data.phone
      phoneHref.value = 'tel:' + res.data.phone.replace(/\s/g, '')
    }
  } catch { /* keep fallback */ }
}

async function submitReservation() {
  if (!selectedTable.value || !selectedTime.value || submitting.value) return
  submitting.value = true
  error.value = ''
  success.value = ''
  try {
    const { data } = await api.post('/reservations', {
      table_id: selectedTable.value.id,
      date: selectedDate.value,
      start_time: selectedTime.value,
      guests_count: guestsCount.value,
      notes: notes.value || null,
    })
    success.value = `Zarezerwowano stolik ${data.table_label} na ${data.date} o ${data.start_time}`
    selectedTable.value = null
    await fetchAvailability()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Nie udało się zarezerwować stolika'
  } finally {
    submitting.value = false
  }
}

watch(selectedDate, () => {
  selectedTime.value = ''
  selectedTable.value = null
  userHasReservation.value = false
  fetchAvailability()
})

watch(selectedTime, () => {
  selectedTable.value = null
})

onMounted(async () => {
  await Promise.all([fetchTables(), fetchAvailability(), fetchPhone()])
})
</script>

<template>
  <div class="res-page">
    <div class="res-hero">
      <h1>Rezerwacja stolika</h1>
      <p>Wybierz datę, godzinę i stolik, który Ci odpowiada</p>
    </div>

    <div class="res-content">
      <!-- Controls bar -->
      <div class="res-controls">
        <div class="res-control-group">
          <label>Data</label>
          <div class="time-slots">
            <button
              v-for="opt in dateOptions"
              :key="opt.value"
              class="time-slot"
              :class="{ active: selectedDate === opt.value }"
              @click="selectedDate = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
        </div>
        <div class="res-control-group">
          <label>Godzina</label>
          <div v-if="availableTimeSlots.length === 0" class="res-no-slots">
            Brak dostępnych godzin na dziś — wybierz jutro.
          </div>
          <div v-else class="time-slots">
            <button
              v-for="slot in availableTimeSlots"
              :key="slot"
              class="time-slot"
              :class="{ active: selectedTime === slot }"
              @click="selectedTime = slot"
            >
              {{ slot }}
            </button>
          </div>
        </div>
      </div>

      <!-- Larger group info -->
      <div class="res-info-box">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        <p>
          Rezerwacja online dotyczy stolików do 4 osób. W przypadku wiekszej grupy prosimy o kontakt telefoniczny:
          <a :href="phoneHref" class="res-phone-link">{{ phoneNumber }}</a>
        </p>
      </div>

      <!-- Private events callout -->
      <div class="res-events-callout">
        <div class="res-events-callout-icon">🎉</div>
        <div class="res-events-callout-text">
          <strong>Organizujesz urodziny, spotkanie firmowe lub inne wydarzenie?</strong>
          <span>Zarezerwuj salę dla swojej grupy — skontaktuj się z nami telefonicznie:
            <a :href="phoneHref" class="res-phone-link">{{ phoneNumber }}</a>
          </span>
        </div>
      </div>

      <div v-if="userHasReservation" class="res-existing">
        <div class="res-existing-header">Twoja rezerwacja na ten dzien</div>
        <div v-if="userReservation" class="res-existing-details">
          <span>Stolik <strong>{{ userResTableLabel() }}</strong></span>
          <span>&middot;</span>
          <span>{{ userReservation.start_time }}</span>
          <span>&middot;</span>
          <span>{{ userReservation.guests_count }} os.</span>
        </div>
        <div class="res-existing-note">
          Mozesz miec tylko jedna rezerwacje dziennie. W razie zmian skontaktuj sie telefonicznie:
          <a :href="phoneHref" class="res-phone-link">{{ phoneNumber }}</a>
        </div>
      </div>

      <div v-if="error" class="res-alert res-alert-error">{{ error }}</div>
      <div v-if="success" class="res-alert res-alert-success">{{ success }}</div>

      <div v-if="!selectedTime" class="res-hint">
        Wybierz godzinę, aby zobaczyć dostępność stolików
      </div>

      <!-- Table maps -->
      <div v-if="selectedTime" class="res-maps">
        <!-- Indoor -->
        <div class="res-zone">
          <h2 class="res-zone-title">Sala</h2>
          <div class="res-map res-map-indoor">
            <div class="map-bg-label">SALA GŁÓWNA</div>
            <div
              v-for="table in indoorTables"
              :key="table.id"
              class="map-table"
              :class="[tableStatus(table.id), { clickable: tableStatus(table.id) === 'free' && !userHasReservation }]"
              :style="{ left: table.position_x + '%', top: table.position_y + '%' }"
              @click="selectTable(table)"
            >
              <span class="map-table-label">{{ table.label }}</span>
              <span class="map-table-seats">{{ table.seats }} os.</span>
            </div>
          </div>
        </div>

        <!-- Outdoor -->
        <div class="res-zone">
          <h2 class="res-zone-title">Ogródek</h2>
          <div class="res-map res-map-outdoor">
            <div class="map-bg-label">TARAS</div>
            <div
              v-for="table in outdoorTables"
              :key="table.id"
              class="map-table"
              :class="[tableStatus(table.id), { clickable: tableStatus(table.id) === 'free' && !userHasReservation }]"
              :style="{ left: table.position_x + '%', top: table.position_y + '%' }"
              @click="selectTable(table)"
            >
              <span class="map-table-label">{{ table.label }}</span>
              <span class="map-table-seats">{{ table.seats }} os.</span>
            </div>
          </div>
        </div>

        <!-- Legend -->
        <div class="res-legend">
          <span class="res-legend-item"><span class="res-legend-dot free"></span> Wolny</span>
          <span class="res-legend-item"><span class="res-legend-dot reserved"></span> Zarezerwowany</span>
        </div>
      </div>

      <!-- Reservation modal -->
      <Teleport to="body">
        <Transition name="modal-fade">
          <div v-if="selectedTable" class="res-backdrop" @click.self="selectedTable = null">
            <div class="res-modal">
              <button class="res-modal-close" @click="selectedTable = null">&times;</button>
              <h3>Rezerwacja stolika {{ selectedTable.label }}</h3>
              <p class="res-modal-info">
                {{ selectedDate }} o {{ selectedTime }} &middot; {{ selectedTable.seats }} miejsc &middot;
                {{ selectedTable.zone === 'indoor' ? 'Wewnątrz' : 'Ogródek' }}
              </p>

              <div class="res-form-group">
                <label>Liczba gości</label>
                <select v-model.number="guestsCount" class="res-input">
                  <option v-for="n in selectedTable.seats" :key="n" :value="n">{{ n }}</option>
                </select>
              </div>

              <div class="res-form-group">
                <label>Uwagi (opcjonalnie)</label>
                <textarea v-model="notes" class="res-input res-textarea" rows="2" placeholder="np. krzesełko dziecięce..."></textarea>
              </div>

              <div class="res-modal-actions">
                <button class="res-btn res-btn-secondary" @click="selectedTable = null">Anuluj</button>
                <button class="res-btn res-btn-primary" :disabled="submitting" @click="submitReservation">
                  {{ submitting ? 'Rezerwuję...' : 'Zarezerwuj' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>

      <!-- Phone dialog for non-logged-in users -->
      <Teleport to="body">
        <Transition name="modal-fade">
          <div v-if="showPhoneDialog" class="res-backdrop" @click.self="showPhoneDialog = false">
            <div class="res-modal">
              <button class="res-modal-close" @click="showPhoneDialog = false">&times;</button>
              <h3>Rezerwacja wymaga zalogowania</h3>
              <p style="margin-bottom: 1rem; color: #666;">
                Zaloguj się, aby zarezerwować stolik online, lub zadzwoń do nas:
              </p>
              <p class="res-phone-number">{{ phoneNumber }}</p>
              <div class="res-modal-actions">
                <a :href="phoneHref" class="res-btn res-btn-primary">Zadzwoń</a>
                <router-link to="/login" class="res-btn res-btn-secondary">Zaloguj się</router-link>
              </div>
            </div>
          </div>
        </Transition>
      </Teleport>
    </div>
  </div>
</template>

<style scoped>
.res-page {
  padding-top: 70px;
  min-height: 100vh;
  background: var(--light-gray);
}

.res-hero {
  background: var(--dark);
  color: var(--white);
  text-align: center;
  padding: 3rem 1rem 2.5rem;
}

.res-hero h1 {
  font-size: 2rem;
  margin-bottom: 0.5rem;
}

.res-hero p {
  color: #bbb;
  font-size: 1rem;
}

.res-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}

/* Controls */
.res-controls {
  background: var(--white);
  border-radius: 10px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.res-control-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
  color: #444;
}

.res-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  font-family: inherit;
}

.res-input:focus {
  outline: none;
  border-color: var(--green);
  box-shadow: 0 0 0 2px rgba(0, 146, 70, 0.15);
}

.time-slots {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.time-slot {
  padding: 0.4rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: var(--white);
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}

.time-slot:hover {
  border-color: var(--green);
  color: var(--green);
}

.time-slot.active {
  background: var(--green);
  color: var(--white);
  border-color: var(--green);
}

.res-hint {
  text-align: center;
  padding: 3rem 1rem;
  color: #999;
  font-size: 1rem;
}

.res-no-slots {
  font-size: 0.9rem;
  color: #999;
  font-style: italic;
  padding: 0.4rem 0;
}

/* Alerts */
.res-alert {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  font-weight: 500;
}

.res-alert-error { background: #fce8ea; color: #c0392b; }
.res-alert-success { background: #e6f4ea; color: #1a7f37; }
.res-alert-warning { background: #fff8e1; color: #e65100; }

/* Info box */
.res-info-box {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  background: var(--white);
  border: 1px solid #e0e0e0;
  border-left: 4px solid var(--green);
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.res-info-box svg {
  flex-shrink: 0;
  color: var(--green);
  margin-top: 1px;
}

.res-info-box p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.5;
  color: #444;
}

.res-phone-link {
  color: var(--green);
  font-weight: 700;
  text-decoration: none;
  white-space: nowrap;
}

.res-phone-link:hover {
  text-decoration: underline;
}

/* Existing reservation */
.res-existing {
  background: var(--white);
  border: 2px solid var(--green);
  border-radius: 10px;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
}

.res-existing-header {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--green);
  margin-bottom: 0.4rem;
}

.res-existing-details {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: var(--dark);
  margin-bottom: 0.5rem;
}

.res-existing-note {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.5;
}

/* Maps */
.res-maps {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.res-zone-title {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: var(--dark);
}

.res-map {
  position: relative;
  background: var(--white);
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  height: 320px;
  overflow: hidden;
  border: 2px solid #e8e8e8;
}

.res-map-indoor {
  background:
    repeating-linear-gradient(0deg, transparent, transparent 39px, #f0f0f0 39px, #f0f0f0 40px),
    repeating-linear-gradient(90deg, transparent, transparent 39px, #f0f0f0 39px, #f0f0f0 40px),
    var(--white);
}

.res-map-outdoor {
  background:
    radial-gradient(circle at 20% 80%, rgba(0, 146, 70, 0.04) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(0, 146, 70, 0.04) 0%, transparent 50%),
    var(--white);
  border-color: var(--green);
  border-style: dashed;
}

.map-bg-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 2rem;
  font-weight: 800;
  color: rgba(0, 0, 0, 0.04);
  letter-spacing: 0.2em;
  pointer-events: none;
  white-space: nowrap;
}

/* Table markers */
.map-table {
  position: absolute;
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s, box-shadow 0.2s;
  transform: translate(-50%, -50%);
  user-select: none;
}

.map-table.free {
  background: #e8f5e9;
  border: 2px solid #81c784;
  color: #2e7d32;
}

.map-table.reserved {
  background: #ffebee;
  border: 2px solid #e57373;
  color: #c62828;
  cursor: not-allowed;
}

.map-table.no-time,
.map-table.user-blocked {
  background: #f5f5f5;
  border: 2px solid #ccc;
  color: #999;
  cursor: not-allowed;
}

.map-table.clickable {
  cursor: pointer;
}

.map-table.clickable:hover {
  transform: translate(-50%, -50%) scale(1.12);
  box-shadow: 0 4px 16px rgba(0, 146, 70, 0.25);
}

.map-table-label {
  font-weight: 700;
  font-size: 0.95rem;
  line-height: 1;
}

.map-table-seats {
  font-size: 0.7rem;
  margin-top: 2px;
  opacity: 0.8;
}

/* Legend */
.res-legend {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  padding: 0.5rem 0;
}

.res-legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #666;
}

.res-legend-dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
}

.res-legend-dot.free {
  background: #e8f5e9;
  border: 2px solid #81c784;
}

.res-legend-dot.reserved {
  background: #ffebee;
  border: 2px solid #e57373;
}

/* Modal */
.res-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
}

.res-modal {
  background: var(--white);
  border-radius: 12px;
  padding: 2rem;
  max-width: 420px;
  width: 90%;
  position: relative;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.res-modal h3 {
  font-size: 1.2rem;
  margin-bottom: 0.25rem;
}

.res-modal-info {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1.25rem;
}

.res-modal-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.res-modal-close:hover {
  background: rgba(0, 0, 0, 0.06);
}

.res-form-group {
  margin-bottom: 1rem;
}

.res-form-group label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 0.3rem;
  color: #444;
}

.res-form-group .res-input {
  width: 100%;
}

.res-textarea {
  resize: vertical;
}

.res-modal-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  margin-top: 1rem;
}

.res-btn {
  padding: 0.6rem 1.25rem;
  border: none;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  font-family: inherit;
  text-decoration: none;
  text-align: center;
  transition: background 0.2s;
}

.res-btn-primary {
  background: var(--green);
  color: var(--white);
}

.res-btn-primary:hover { background: #007a3a; }

.res-btn-secondary {
  background: none;
  border: 1.5px solid #ccc;
  color: var(--dark);
}

.res-btn-secondary:hover { border-color: var(--dark); }

.res-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.res-phone-number {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--green);
  text-align: center;
  margin-bottom: 1.25rem;
}

/* Modal transition */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

/* Private events callout */
.res-events-callout {
  display: flex;
  gap: 0.85rem;
  align-items: flex-start;
  background: #fffbf0;
  border: 1px solid #f0dfa0;
  border-left: 4px solid #d4a017;
  border-radius: 8px;
  padding: 1rem 1.25rem;
  margin-bottom: 1rem;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
}

.res-events-callout-icon {
  font-size: 1.4rem;
  flex-shrink: 0;
  line-height: 1.4;
}

.res-events-callout-text {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  font-size: 0.9rem;
  line-height: 1.5;
  color: #444;
}

.res-events-callout-text strong {
  color: #333;
  font-weight: 700;
}

@media (max-width: 600px) {
  .res-hero h1 { font-size: 1.5rem; }
  .res-map { height: 260px; }
  .map-table {
    width: 60px;
    height: 60px;
  }
  .map-table-label { font-size: 0.85rem; }
  .map-table-seats { font-size: 0.65rem; }
  .time-slot { padding: 0.35rem 0.55rem; font-size: 0.8rem; }

  .res-events-inner {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
