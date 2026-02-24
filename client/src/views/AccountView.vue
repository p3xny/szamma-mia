<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { api } from '@/composables/useApi'
import PhoneInput from '@/components/PhoneInput.vue'

const router = useRouter()
const {
  user, isAuthenticated, logout,
  updateProfile, getAddresses, createAddress, updateAddress, deleteAddress,
} = useAuth()

// Orders
const orders = ref([])
let orderPollTimer = null

const ACTIVE_ORDER_STATUSES = new Set(['pending', 'confirmed', 'preparing', 'delivering'])

const orderStatusLabels = {
  pending: 'Oczekuje na potwierdzenie',
  confirmed: 'Potwierdzone',
  preparing: 'W przygotowaniu',
  delivering: 'W dostawie',
  completed: 'Zrealizowane',
  cancelled: 'Anulowane',
}

const orderStatusColors = {
  pending: '#a16207',
  confirmed: '#009246',
  preparing: '#1d4ed8',
  delivering: '#1d4ed8',
  completed: '#666',
  cancelled: '#ce2b37',
}

async function loadOrders() {
  try {
    const res = await api.get('/my-orders')
    orders.value = res.data
    // Stop polling when no active orders remain
    const hasActive = res.data.some(o => ACTIVE_ORDER_STATUSES.has(o.status))
    if (!hasActive && orderPollTimer) {
      clearInterval(orderPollTimer)
      orderPollTimer = null
    }
  } catch {
    // silent
  }
}

// Reservations
const reservations = ref([])

async function loadReservations() {
  try {
    const res = await api.get('/my-reservations')
    reservations.value = res.data
  } catch {
    // silent
  }
}

function formatDate(dateStr) {
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('pl-PL', { weekday: 'long', day: 'numeric', month: 'long' })
}

function zoneLabel(zone) {
  return zone === 'indoor' ? 'Sala' : 'Ogrodek'
}

if (!isAuthenticated.value) {
  router.push('/login')
}

// Profile form
const profileFirstName = ref('')
const profileEmail = ref('')
const profilePhone = ref('')
const profileSaving = ref(false)
const profileMsg = ref('')

function initProfile() {
  if (user.value) {
    profileFirstName.value = user.value.first_name || ''
    profileEmail.value = user.value.email || ''
    profilePhone.value = user.value.phone || ''
  }
}

async function saveProfile() {
  profileSaving.value = true
  profileMsg.value = ''
  try {
    await updateProfile({
      first_name: profileFirstName.value,
      email: profileEmail.value,
      phone: profilePhone.value,
    })
    profileMsg.value = 'Zmiany zapisane'
  } catch (err) {
    profileMsg.value = err.response?.data?.detail || 'Nie udało się zapisać'
  } finally {
    profileSaving.value = false
  }
}

// Addresses
const addresses = ref([])
const showAddForm = ref(false)
const editingId = ref(null)

// New address form
const addrLabel = ref('')
const addrCity = ref('')
const addrStreet = ref('')
const addrHouse = ref('')
const addrApartment = ref('')

function resetAddrForm() {
  addrLabel.value = ''
  addrCity.value = ''
  addrStreet.value = ''
  addrHouse.value = ''
  addrApartment.value = ''
}

async function loadAddresses() {
  try {
    addresses.value = await getAddresses()
  } catch {
    // silent
  }
}

async function handleAddAddress() {
  try {
    await createAddress({
      label: addrLabel.value || null,
      city: addrCity.value,
      street: addrStreet.value,
      house_number: addrHouse.value,
      apartment: addrApartment.value || null,
    })
    resetAddrForm()
    showAddForm.value = false
    await loadAddresses()
  } catch {
    // silent
  }
}

function startEdit(addr) {
  editingId.value = addr.id
  addrLabel.value = addr.label || ''
  addrCity.value = addr.city
  addrStreet.value = addr.street
  addrHouse.value = addr.house_number
  addrApartment.value = addr.apartment || ''
}

function cancelEdit() {
  editingId.value = null
  resetAddrForm()
}

async function handleUpdateAddress(id) {
  try {
    await updateAddress(id, {
      label: addrLabel.value || null,
      city: addrCity.value,
      street: addrStreet.value,
      house_number: addrHouse.value,
      apartment: addrApartment.value || null,
    })
    editingId.value = null
    resetAddrForm()
    await loadAddresses()
  } catch {
    // silent
  }
}

async function handleDeleteAddress(id) {
  try {
    await deleteAddress(id)
    await loadAddresses()
  } catch {
    // silent
  }
}

function handleLogout() {
  logout()
  router.push('/')
}

function goHome() {
  router.push('/')
}

onMounted(async () => {
  initProfile()
  loadAddresses()
  loadReservations()
  await loadOrders()
  // Keep polling while there are active orders
  if (orders.value.some(o => ACTIVE_ORDER_STATUSES.has(o.status))) {
    orderPollTimer = setInterval(loadOrders, 25000)
  }
})

onUnmounted(() => {
  if (orderPollTimer) clearInterval(orderPollTimer)
})
</script>

<template>
  <div class="acc-page" v-if="isAuthenticated">
    <div class="acc-header" style="height:4rem;">  <!-- empty header to offset fixed nav -->
      <!-- <button class="acc-back" @click="goHome">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/>
        </svg>
        Strona główna
      </button> -->
    </div>

    <div class="acc-content">
      <h1 class="acc-title">Moje konto</h1>

      <!-- Profile section -->
      <section class="acc-section">
        <h2 class="acc-section-title">Dane osobowe</h2>

        <div class="acc-field">
          <label>Imię</label>
          <input v-model="profileFirstName" type="text">
        </div>

        <div class="acc-field">
          <label>Email</label>
          <input v-model="profileEmail" type="email">
        </div>

        <div class="acc-field">
          <label>Telefon</label>
          <PhoneInput v-model="profilePhone" />
        </div>

        <div class="acc-actions">
          <button class="btn-save" @click="saveProfile" :disabled="profileSaving">
            {{ profileSaving ? 'Zapisywanie...' : 'Zapisz zmiany' }}
          </button>
          <span v-if="profileMsg" class="acc-msg">{{ profileMsg }}</span>
        </div>
      </section>

      <!-- Addresses section -->
      <section class="acc-section">
        <h2 class="acc-section-title">Zapisane adresy</h2>

        <div v-if="addresses.length === 0 && !showAddForm" class="acc-empty">
          Brak zapisanych adresów
        </div>

        <div v-for="addr in addresses" :key="addr.id" class="addr-card">
          <template v-if="editingId === addr.id">
            <div class="addr-form">
              <input v-model="addrLabel" type="text" placeholder="Nazwa (np. Dom)">
              <input v-model="addrCity" type="text" placeholder="Miasto" required>
              <input v-model="addrStreet" type="text" placeholder="Ulica" required>
              <div class="addr-row">
                <input v-model="addrHouse" type="text" placeholder="Nr domu" required>
                <input v-model="addrApartment" type="text" placeholder="Mieszkanie">
              </div>
              <div class="addr-form-actions">
                <button class="btn-save btn-sm" @click="handleUpdateAddress(addr.id)">Zapisz</button>
                <button class="btn-cancel btn-sm" @click="cancelEdit">Anuluj</button>
              </div>
            </div>
          </template>
          <template v-else>
            <div class="addr-info">
              <strong v-if="addr.label">{{ addr.label }}</strong>
              <span>{{ addr.street }} {{ addr.house_number }}<template v-if="addr.apartment">/{{ addr.apartment }}</template>, {{ addr.city }}</span>
            </div>
            <div class="addr-actions">
              <button class="btn-icon" @click="startEdit(addr)" title="Edytuj">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button class="btn-icon btn-icon-danger" @click="handleDeleteAddress(addr.id)" title="Usuń">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </template>
        </div>

        <!-- Add address form -->
        <div v-if="showAddForm" class="addr-card">
          <div class="addr-form">
            <input v-model="addrLabel" type="text" placeholder="Nazwa (np. Dom)">
            <input v-model="addrCity" type="text" placeholder="Miasto" required>
            <input v-model="addrStreet" type="text" placeholder="Ulica" required>
            <div class="addr-row">
              <input v-model="addrHouse" type="text" placeholder="Nr domu" required>
              <input v-model="addrApartment" type="text" placeholder="Mieszkanie">
            </div>
            <div class="addr-form-actions">
              <button class="btn-save btn-sm" @click="handleAddAddress">Dodaj</button>
              <button class="btn-cancel btn-sm" @click="showAddForm = false; resetAddrForm()">Anuluj</button>
            </div>
          </div>
        </div>

        <button v-if="!showAddForm && editingId === null" class="btn-add-addr" @click="showAddForm = true">
          + Dodaj adres
        </button>
      </section>

      <!-- Orders section -->
      <section class="acc-section">
        <h2 class="acc-section-title">Moje zamówienia</h2>

        <div v-if="orders.length === 0" class="acc-empty">Brak zamówień z ostatnich 30 dni</div>

        <div v-for="o in orders" :key="o.id" class="order-card">
          <div class="order-card-head">
            <span class="order-card-id">#{{ o.id }}</span>
            <span
              class="order-card-badge"
              :style="{ background: orderStatusColors[o.status] + '18', color: orderStatusColors[o.status] }"
            >{{ orderStatusLabels[o.status] || o.status }}</span>
            <span class="order-card-total">{{ o.total }} zł</span>
          </div>

          <!-- ETA bar — only for active orders that have eta set -->
          <div v-if="o.eta_minutes && ACTIVE_ORDER_STATUSES.has(o.status)" class="order-card-eta">
            <span class="order-eta-icon">🕐</span>
            <span>Szacowany czas: <strong>{{ o.eta_minutes }} min</strong></span>
          </div>

          <div class="order-card-items">
            <span v-for="(item, i) in o.items" :key="item.id">
              {{ item.quantity > 1 ? `${item.quantity}× ` : '' }}{{ item.dish_name }}<template v-if="i < o.items.length - 1">, </template>
            </span>
          </div>

          <router-link :to="`/order-confirmation/${o.id}`" class="order-card-link">
            Szczegóły zamówienia →
          </router-link>
        </div>
      </section>

      <!-- Reservations section -->
      <section class="acc-section">
        <h2 class="acc-section-title">Moje rezerwacje</h2>

        <div v-if="reservations.length === 0" class="acc-empty">
          Brak nadchodzacych rezerwacji
        </div>

        <div v-for="res in reservations" :key="res.id" class="res-card">
          <div class="res-card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
          </div>
          <div class="res-card-info">
            <div class="res-card-date">{{ formatDate(res.reservation_date) }}</div>
            <div class="res-card-details">
              {{ res.start_time }} &middot; Stolik {{ res.table_label }} ({{ zoneLabel(res.zone) }}) &middot; {{ res.guests_count }} os.
            </div>
            <div v-if="res.notes" class="res-card-notes">{{ res.notes }}</div>
          </div>
        </div>

        <router-link to="/reservation" class="btn-add-addr" style="display: block; text-align: center; text-decoration: none;">
          Zarezerwuj stolik
        </router-link>
      </section>

      <!-- Logout -->
      <button class="btn-logout" @click="handleLogout">Wyloguj sie</button>
    </div>
  </div>
</template>

<style scoped>
.acc-page {
  min-height: 100vh;
  background: var(--light-gray);
}

.acc-header {
  display: flex;
  align-items: center;
  padding: 0.9rem 2rem;
  background: var(--white);
  border-bottom: 1px solid #eee;
}

.acc-back {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--green);
  cursor: pointer;
  padding: 0.4rem 0.6rem;
  border-radius: 6px;
  transition: background 0.2s;
}

.acc-back:hover {
  background: rgba(0, 146, 70, 0.08);
}

.acc-content {
  max-width: 560px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

.acc-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--dark);
  margin-bottom: 1.5rem;
}

.acc-section {
  background: var(--white);
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
}

.acc-section-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--dark);
  margin-bottom: 1rem;
}

.acc-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  margin-bottom: 0.75rem;
}

.acc-field label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
}

.acc-field input {
  padding: 0.7rem 0.75rem;
  border: 1.5px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
}

.acc-field input:focus {
  border-color: var(--green);
}

.acc-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.btn-save {
  background: var(--green);
  color: var(--white);
  border: none;
  padding: 0.65rem 1.5rem;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-save:hover:not(:disabled) {
  background: #007a3a;
}

.btn-save:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.85rem;
}

.btn-cancel {
  background: none;
  border: 1.5px solid #ccc;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  color: var(--dark);
  transition: border-color 0.3s;
}

.btn-cancel:hover {
  border-color: var(--dark);
}

.acc-msg {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--green);
}

.acc-empty {
  font-size: 0.9rem;
  color: #888;
  margin-bottom: 0.75rem;
}

/* Address cards */
.addr-card {
  border: 1.5px solid #eee;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
}

.addr-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.addr-info strong {
  font-size: 0.85rem;
  color: var(--green);
}

.addr-info span {
  font-size: 0.9rem;
  color: var(--dark);
}

.addr-actions {
  display: flex;
  gap: 0.5rem;
  flex-shrink: 0;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.4rem;
  border-radius: 6px;
  color: #666;
  transition: background 0.2s, color 0.2s;
}

.btn-icon:hover {
  background: rgba(0, 0, 0, 0.06);
  color: var(--dark);
}

.btn-icon-danger:hover {
  background: rgba(206, 43, 55, 0.08);
  color: var(--red);
}

/* Address form inside card */
.addr-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

.addr-form input {
  padding: 0.6rem 0.7rem;
  border: 1.5px solid #ddd;
  border-radius: 6px;
  font-size: 0.9rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
}

.addr-form input:focus {
  border-color: var(--green);
}

.addr-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.addr-form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.btn-add-addr {
  background: none;
  border: 1.5px dashed #ccc;
  padding: 0.7rem;
  border-radius: 8px;
  width: 100%;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--green);
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.btn-add-addr:hover {
  border-color: var(--green);
  background: rgba(0, 146, 70, 0.04);
}

/* Order cards */
.order-card {
  border: 1.5px solid #eee;
  border-radius: 8px;
  padding: 0.9rem 1rem;
  margin-bottom: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.order-card-head {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.order-card-id {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--dark);
}

.order-card-badge {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
}

.order-card-total {
  margin-left: auto;
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--dark);
}

.order-card-eta {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #555;
  background: rgba(0, 146, 70, 0.07);
  border-radius: 6px;
  padding: 0.35rem 0.65rem;
}

.order-eta-icon { font-size: 1rem; }

.order-card-eta strong { color: var(--green); }

.order-card-items {
  font-size: 0.85rem;
  color: #666;
  line-height: 1.5;
}

.order-card-link {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--green);
  text-decoration: none;
  align-self: flex-start;
  transition: opacity 0.2s;
}

.order-card-link:hover { opacity: 0.75; }

/* Reservation cards */
.res-card {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  border: 1.5px solid #eee;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
}

.res-card-icon {
  flex-shrink: 0;
  color: var(--green);
  margin-top: 2px;
}

.res-card-info {
  flex: 1;
}

.res-card-date {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--dark);
  text-transform: capitalize;
}

.res-card-details {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.15rem;
}

.res-card-notes {
  font-size: 0.8rem;
  color: #999;
  font-style: italic;
  margin-top: 0.25rem;
}

.btn-logout {
  background: none;
  border: 1.5px solid var(--red);
  color: var(--red);
  padding: 0.75rem;
  border-radius: 8px;
  width: 100%;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-logout:hover {
  background: rgba(206, 43, 55, 0.06);
}

@media (max-width: 768px) {
  .acc-header {
    padding: 0.75rem 1rem;
  }

  .acc-content {
    padding: 1.25rem 1rem 2rem;
  }
}
</style>
