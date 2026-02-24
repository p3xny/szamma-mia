<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/api.js'

const orders = ref([])
const notifications = ref([])
const loading = ref(true)
const error = ref('')
const filterStatus = ref('')

// ETA modal
const showEtaModal = ref(false)
const etaPendingOrder = ref(null)
const etaMinutes = ref(40)
const etaStep = ref(10)
const etaDefault = ref(40)

const filtered = computed(() => {
  if (!filterStatus.value) return orders.value
  return orders.value.filter(o => o.status === filterStatus.value)
})

const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)

async function fetchData() {
  loading.value = true
  try {
    const [res, notifs, settings] = await Promise.all([
      api.get('/admin/orders'),
      api.get('/admin/notifications?unread_only=false'),
      api.get('/admin/settings'),
    ])
    orders.value = res.data
    notifications.value = notifs.data.filter(n => n.type === 'order')
    etaStep.value = parseInt(settings.data.eta_step) || 10
    etaDefault.value = parseInt(settings.data.eta_default) || 40
  } catch {
    error.value = 'Nie udało się załadować danych'
  } finally {
    loading.value = false
  }
}

async function updateStatus(o, status, eta = null) {
  try {
    const payload = { status }
    if (eta !== null) payload.eta_minutes = eta
    const res = await api.patch(`/admin/orders/${o.id}`, payload)
    o.status = res.data.status
    if (res.data.eta_minutes !== undefined) o.eta_minutes = res.data.eta_minutes
  } catch {
    error.value = 'Nie udało się zaktualizować statusu'
  }
}

function openEtaModal(o) {
  etaPendingOrder.value = o
  etaMinutes.value = etaDefault.value
  showEtaModal.value = true
}

async function confirmEta() {
  const o = etaPendingOrder.value
  showEtaModal.value = false
  etaPendingOrder.value = null
  await updateStatus(o, 'confirmed', etaMinutes.value)
}

async function markNotifRead(n) {
  try {
    await api.patch(`/admin/notifications/${n.id}`)
    n.is_read = true
  } catch { /* silent */ }
}

async function markAllRead() {
  try {
    await api.post('/admin/notifications/read-all')
    notifications.value.forEach(n => { n.is_read = true })
  } catch { /* silent */ }
}

function formatDate(iso) {
  if (!iso) return '—'
  const [y, m, d] = iso.split('T')[0].split('-')
  return `${d}.${m}.${y}`
}

const statusLabels = {
  pending: 'Oczekujące',
  confirmed: 'Potwierdzone',
  preparing: 'W przygotowaniu',
  delivering: 'W dostawie',
  completed: 'Zrealizowane',
  cancelled: 'Anulowane',
}

const statusColors = {
  pending: 'badge-yellow',
  confirmed: 'badge-green',
  preparing: 'badge-blue',
  delivering: 'badge-blue',
  completed: 'badge-gray',
  cancelled: 'badge-red',
}

const deliveryLabels = {
  delivery: 'Dostawa',
  pickup: 'Odbiór',
}

const expandedId = ref(null)

function toggleDetails(id) {
  expandedId.value = expandedId.value === id ? null : id
}

function parseJson(str) {
  if (!str) return []
  try { return JSON.parse(str) } catch { return [] }
}

function itemDescription(item) {
  const ingredients = parseJson(item.ingredients_snapshot)
  const extras = parseJson(item.extras_snapshot)

  const removed = ingredients.filter(i => !i.included).map(i => i.name)
  const added = ingredients.filter(i => i.included && i.price > 0).map(i => i.name)
  const extraNames = extras.map(e => e.name)

  const parts = []
  if (removed.length) parts.push('bez ' + removed.join(', '))
  if (added.length) parts.push('+ ' + added.join(', '))
  if (extraNames.length) parts.push('+ ' + extraNames.join(', '))
  return parts.join('; ')
}

onMounted(fetchData)
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Zamówienia</h1>
    </div>

    <div v-if="error" class="alert alert-error">{{ error }}</div>

    <!-- Notifications banner -->
    <div v-if="unreadCount > 0" class="card" style="border-left: 4px solid var(--green); margin-bottom: 1rem">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem">
        <strong>Nowe powiadomienia ({{ unreadCount }})</strong>
        <button class="btn btn-sm btn-secondary" @click="markAllRead">Oznacz jako przeczytane</button>
      </div>
      <div
        v-for="n in notifications.filter(x => !x.is_read)"
        :key="n.id"
        style="padding: 0.4rem 0; border-bottom: 1px solid #eee; font-size: 0.9rem; display: flex; justify-content: space-between; align-items: center"
      >
        <span>{{ n.message }}</span>
        <button class="btn btn-sm btn-secondary" @click="markNotifRead(n)" style="white-space: nowrap">OK</button>
      </div>
    </div>

    <!-- Filter -->
    <div class="card" style="padding: 0.75rem 1rem; margin-bottom: 1rem">
      <div style="display: flex; align-items: center; gap: 0.75rem">
        <label style="font-size: 0.85rem; font-weight: 600; white-space: nowrap">Status:</label>
        <select v-model="filterStatus" class="form-control" style="max-width: 200px">
          <option value="">Wszystkie</option>
          <option value="pending">Oczekujące</option>
          <option value="confirmed">Potwierdzone</option>
          <option value="preparing">W przygotowaniu</option>
          <option value="delivering">W dostawie</option>
          <option value="completed">Zrealizowane</option>
          <option value="cancelled">Anulowane</option>
        </select>
      </div>
    </div>

    <!-- Table -->
    <div v-if="loading" class="card">Ładowanie...</div>
    <div v-else class="card table-wrap" style="padding: 0">
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Data</th>
            <th>Klient</th>
            <th>Tryb</th>
            <th>Kwota</th>
            <th>Płatność</th>
            <th>Status</th>
            <th>Akcje</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="o in filtered" :key="o.id">
            <tr class="order-row" :class="{ 'row-expanded': expandedId === o.id }" @click="toggleDetails(o.id)">
              <td>#{{ o.id }}</td>
              <td>{{ formatDate(o.created_at) }}</td>
              <td>{{ o.first_name }} {{ o.last_name || '' }}</td>
              <td>{{ deliveryLabels[o.delivery_mode] || o.delivery_mode }}</td>
              <td><strong>{{ o.total }} zł</strong></td>
              <td>{{ o.payment_method }}</td>
              <td>
                <span class="badge" :class="statusColors[o.status] || ''">
                  {{ statusLabels[o.status] || o.status }}
                </span>
              </td>
              <td @click.stop>
                <div style="display: flex; gap: 0.3rem">
                  <button
                    v-if="o.status === 'pending'"
                    class="btn btn-primary btn-sm"
                    @click="openEtaModal(o)"
                  >Potwierdź</button>
                  <button
                    v-if="o.status === 'confirmed'"
                    class="btn btn-primary btn-sm"
                    @click="updateStatus(o, 'preparing')"
                  >Przygotuj</button>
                  <button
                    v-if="o.status === 'preparing' && o.delivery_mode === 'delivery'"
                    class="btn btn-primary btn-sm"
                    @click="updateStatus(o, 'delivering')"
                  >Wyślij</button>
                  <button
                    v-if="o.status === 'preparing' && o.delivery_mode === 'pickup'"
                    class="btn btn-primary btn-sm"
                    @click="updateStatus(o, 'completed')"
                  >Gotowe</button>
                  <button
                    v-if="o.status === 'delivering'"
                    class="btn btn-primary btn-sm"
                    @click="updateStatus(o, 'completed')"
                  >Dostarczono</button>
                  <button
                    v-if="['pending', 'confirmed'].includes(o.status)"
                    class="btn btn-danger btn-sm"
                    @click="updateStatus(o, 'cancelled')"
                  >Anuluj</button>
                </div>
              </td>
            </tr>
            <!-- Expanded detail row -->
            <tr v-if="expandedId === o.id" class="detail-row">
              <td colspan="8">
                <div class="order-details">
                  <div class="details-grid">
                    <div class="details-items">
                      <strong>Pozycje zamówienia:</strong>
                      <ul class="items-list">
                        <li v-for="item in o.items" :key="item.id">
                          <span class="item-qty">{{ item.quantity }}x</span>
                          <span class="item-name">{{ item.dish_name }}</span>
                          <span class="item-price">{{ item.item_total }} zł</span>
                          <div v-if="itemDescription(item)" class="item-mods">{{ itemDescription(item) }}</div>
                        </li>
                      </ul>
                    </div>
                    <div class="details-info">
                      <div v-if="o.delivery_mode === 'delivery'">
                        <strong>Adres dostawy:</strong>
                        <div>{{ o.street }} {{ o.house_number }}<span v-if="o.apartment">/{{ o.apartment }}</span>, {{ o.city }}</div>
                      </div>
                      <div>
                        <strong>Kontakt:</strong>
                        <div>{{ o.phone }}<span v-if="o.email"> · {{ o.email }}</span></div>
                      </div>
                      <div v-if="o.scheduled_time">
                        <strong>Na godzinę:</strong>
                        <div>{{ o.scheduled_date ? formatDate(o.scheduled_date) + ' ' : '' }}{{ o.scheduled_time }}</div>
                      </div>
                      <div v-if="o.notes">
                        <strong>Uwagi:</strong>
                        <div>{{ o.notes }}</div>
                      </div>
                      <div class="details-totals">
                        <div>Pozycje: {{ o.items_total }} zł</div>
                        <div v-if="parseFloat(o.delivery_fee) > 0">Dostawa: {{ o.delivery_fee }} zł</div>
                        <div v-if="parseFloat(o.discount) > 0">Rabat: -{{ o.discount }} zł<span v-if="o.coupon_code"> ({{ o.coupon_code }})</span></div>
                        <div class="total-line">Razem: {{ o.total }} zł</div>
                      </div>
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </template>
          <tr v-if="filtered.length === 0">
            <td colspan="8" style="text-align: center; color: #999">Brak zamówień</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- ETA confirmation modal -->
    <Transition name="eta-fade">
      <div v-if="showEtaModal" class="eta-backdrop" @click.self="showEtaModal = false">
        <div class="eta-dialog">
          <button class="eta-close" @click="showEtaModal = false">&times;</button>
          <h3 class="eta-title">Potwierdź zamówienie</h3>
          <p class="eta-subtitle">
            Zamówienie <strong>#{{ etaPendingOrder?.id }}</strong> —
            {{ etaPendingOrder?.first_name }} {{ etaPendingOrder?.last_name || '' }}
          </p>
          <p class="eta-label">Szacowany czas realizacji</p>
          <div class="eta-controls">
            <button class="eta-btn-step" @click="etaMinutes = Math.max(etaStep, etaMinutes - etaStep)">−</button>
            <span class="eta-value">{{ etaMinutes }} min</span>
            <button class="eta-btn-step" @click="etaMinutes += etaStep">+</button>
          </div>
          <div class="eta-actions">
            <button class="btn btn-secondary" @click="showEtaModal = false">Anuluj</button>
            <button class="btn btn-primary" @click="confirmEta">Potwierdź zamówienie</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.order-row {
  cursor: pointer;
  transition: background 0.15s;
}

.order-row:hover {
  background: #f9f9f9;
}

.row-expanded {
  background: #f5f5f5;
}

.detail-row td {
  padding: 0 !important;
  background: #fafafa;
  border-bottom: 2px solid #e0e0e0;
}

.order-details {
  padding: 1rem 1.25rem;
}

.details-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.items-list {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0;
}

.items-list li {
  padding: 0.4rem 0;
  border-bottom: 1px solid #eee;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0.4rem;
}

.item-qty {
  font-weight: 700;
  color: #555;
  min-width: 2rem;
}

.item-name {
  font-weight: 600;
  flex: 1;
}

.item-price {
  color: #666;
  font-size: 0.85rem;
  white-space: nowrap;
}

.item-mods {
  width: 100%;
  font-size: 0.8rem;
  color: #888;
  padding-left: 2.4rem;
  font-style: italic;
}

.details-info {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  font-size: 0.9rem;
}

.details-info strong {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: #666;
}

.details-totals {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid #ddd;
  font-size: 0.85rem;
  color: #555;
}

.total-line {
  font-weight: 700;
  color: #1a1a1a;
  font-size: 0.95rem;
  margin-top: 0.2rem;
}

/* ETA modal */
.eta-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
}

.eta-dialog {
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  width: 360px;
  max-width: 90vw;
  text-align: center;
  position: relative;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
}

.eta-close {
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

.eta-close:hover {
  background: rgba(0, 0, 0, 0.07);
}

.eta-title {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 0.4rem;
}

.eta-subtitle {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1.5rem;
}

.eta-label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #888;
  margin-bottom: 0.75rem;
}

.eta-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1.25rem;
  margin-bottom: 1.75rem;
}

.eta-btn-step {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  border: 2px solid var(--primary, #2563eb);
  background: none;
  font-size: 1.3rem;
  font-weight: 700;
  cursor: pointer;
  color: var(--primary, #2563eb);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s;
  line-height: 1;
}

.eta-btn-step:hover {
  background: var(--primary, #2563eb);
  color: #fff;
}

.eta-value {
  font-size: 2rem;
  font-weight: 700;
  min-width: 5rem;
  color: #1a1a1a;
}

.eta-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: center;
}

.eta-fade-enter-active,
.eta-fade-leave-active {
  transition: opacity 0.2s ease;
}

.eta-fade-enter-from,
.eta-fade-leave-to {
  opacity: 0;
}
</style>
