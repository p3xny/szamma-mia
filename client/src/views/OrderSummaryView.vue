<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '@/composables/useCart'
import { useAuth } from '@/composables/useAuth'
import { createOrder, validateCoupon, getSlotOccupancy } from '@/composables/useApi'
import PhoneInput from '@/components/PhoneInput.vue'

const router = useRouter()
const { items, totalPrice, calcItemTotal, clearCart } = useCart()
const { isAuthenticated, user, getAddresses } = useAuth()

// Saved addresses
const savedAddresses = ref([])

// Delivery mode
const deliveryMode = ref('delivery') // 'delivery' | 'pickup'

// Delivery form
const city = ref('')
const street = ref('')
const houseNumber = ref('')
const apartment = ref('')
const phone = ref('')
const email = ref('')
const notes = ref('')

// Recipient
const firstName = ref('')
const lastName = ref('')

// Payment
const paymentMethod = ref('')

// Scheduling (optional — null means "as soon as possible")
const scheduledDate = ref(null)
const scheduledTime = ref('')
const slotOccupancy = ref({})

function localDateStr(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

function todayStr() {
  return localDateStr(new Date())
}

function addDays(dateStr, days) {
  const d = new Date(dateStr + 'T00:00:00')
  d.setDate(d.getDate() + days)
  return localDateStr(d)
}

const allTimeSlots = computed(() => {
  const isDelivery = deliveryMode.value === 'delivery'
  const startH = isDelivery ? 13 : 12
  const startM = isDelivery ? 0 : 30
  const endH = 22
  const endM = 0

  const all = []
  for (let h = startH; h <= endH; h++) {
    for (const m of [0, 30]) {
      if (h === startH && m < startM) continue
      if (h === endH && m > endM) continue
      all.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`)
    }
  }
  return all
})

const availableTimeSlots = computed(() => {
  if (!scheduledDate.value) return []
  return allTimeSlots.value.map(slot => ({
    time: slot,
    full: (slotOccupancy.value[slot] || 0) >= 2,
  }))
})

// Fetch slot occupancy when date changes
watch(scheduledDate, async (newDate) => {
  scheduledTime.value = ''
  slotOccupancy.value = {}
  if (!newDate) return
  try {
    const data = await getSlotOccupancy(newDate)
    slotOccupancy.value = data.slots || {}
  } catch {
    // silent
  }
})

// Reset time when delivery mode changes
watch(deliveryMode, () => {
  scheduledTime.value = ''
})

function formatDateLabel(dateStr) {
  const today = todayStr()
  const tomorrow = addDays(today, 1)
  if (dateStr === today) return 'Dzisiaj'
  if (dateStr === tomorrow) return 'Jutro'
  const d = new Date(dateStr + 'T00:00:00')
  return d.toLocaleDateString('pl-PL', { weekday: 'long', day: 'numeric', month: 'long' })
}

const dateOptions = computed(() => {
  const today = todayStr()
  const tomorrow = addDays(today, 1)
  return [
    { value: tomorrow, label: 'Jutro' },
    { value: addDays(today, 2), label: formatDateLabel(addDays(today, 2)) },
  ]
})

// Bonus code
const bonusCode = ref('')
const bonusApplied = ref(false)
const bonusDiscountType = ref('percent')
const bonusDiscountPercent = ref(0)
const bonusDiscountFixed = ref(0)
const bonusMessage = ref('')
const bonusError = ref('')

// Submit state
const submitting = ref(false)
const submitError = ref('')

async function applyBonus() {
  if (!bonusCode.value.trim()) return
  bonusError.value = ''
  bonusMessage.value = ''
  try {
    const res = await validateCoupon(bonusCode.value.trim())
    if (res.valid) {
      bonusApplied.value = true
      bonusDiscountType.value = res.discount_type || 'percent'
      bonusDiscountPercent.value = res.discount_percent || 0
      bonusDiscountFixed.value = res.discount_amount || 0
      bonusMessage.value = res.message
    } else {
      bonusError.value = res.message
    }
  } catch {
    bonusError.value = 'Nie udalo sie zweryfikowac kodu'
  }
}

// Computed totals
const discountAmount = computed(() => {
  if (!bonusApplied.value) return 0
  if (bonusDiscountType.value === 'fixed') {
    return Math.min(bonusDiscountFixed.value, totalPrice.value)
  }
  if (!bonusDiscountPercent.value) return 0
  return Math.round(totalPrice.value * bonusDiscountPercent.value / 100)
})

const discountLabel = computed(() => {
  if (bonusDiscountType.value === 'fixed') {
    return `Rabat (-${bonusDiscountFixed.value} zl)`
  }
  return `Rabat (${bonusDiscountPercent.value}%)`
})

const finalTotal = computed(() => totalPrice.value - discountAmount.value)

// Validation
const formValid = computed(() => {
  const hasRecipient = firstName.value.trim()
  const hasPhone = phone.value.trim()
  const hasPayment = paymentMethod.value

  if (deliveryMode.value === 'delivery') {
    return hasRecipient && hasPhone && city.value.trim() && street.value.trim() && houseNumber.value.trim() && hasPayment
  }
  return hasRecipient && hasPhone && hasPayment
})

function summarize(item) {
  const parts = []
  if (item.ingredients) {
    const removed = item.ingredients.filter(i => !i.included).map(i => i.name)
    if (removed.length) parts.push('bez ' + removed.join(', '))
    const added = item.ingredients.filter(i => i.included && i.price).map(i => '+ ' + i.name)
    if (added.length) parts.push(...added)
  }
  if (item.extras) {
    const selected = item.extras.filter(e => e.selected).map(e => '+ ' + e.name)
    if (selected.length) parts.push(...selected)
  }
  return parts.join(', ')
}

async function submitOrder() {
  if (!formValid.value || submitting.value) return
  submitting.value = true
  submitError.value = ''

  const orderData = {
    delivery_mode: deliveryMode.value,
    first_name: firstName.value.trim(),
    last_name: lastName.value.trim(),
    phone: phone.value.trim(),
    email: email.value.trim() || null,
    city: deliveryMode.value === 'delivery' ? city.value.trim() : null,
    street: deliveryMode.value === 'delivery' ? street.value.trim() : null,
    house_number: deliveryMode.value === 'delivery' ? houseNumber.value.trim() : null,
    apartment: deliveryMode.value === 'delivery' ? apartment.value.trim() || null : null,
    notes: notes.value.trim() || null,
    payment_method: paymentMethod.value,
    coupon_code: bonusApplied.value ? bonusCode.value.trim() : null,
    scheduled_date: scheduledTime.value ? scheduledDate.value : null,
    scheduled_time: scheduledTime.value || null,
    items: items.value.map(item => ({
      dish_id: item.dishId,
      quantity: item.quantity,
      ingredients: (item.ingredients || []).map(ing => ({
        name: ing.name,
        included: ing.included,
        price: ing.price || 0,
      })),
      extras: (item.extras || []).filter(e => e.selected).map(ext => ({
        name: ext.name,
        price: ext.price,
      })),
    })),
  }

  try {
    const order = await createOrder(orderData)
    clearCart()
    router.push('/order-confirmation/' + order.id)
  } catch (err) {
    submitError.value = err.response?.data?.detail || 'Nie udało się złożyć zamówienia'
  } finally {
    submitting.value = false
  }
}

function selectAddress(addr) {
  city.value = addr.city
  street.value = addr.street
  houseNumber.value = addr.house_number
  apartment.value = addr.apartment || ''
}

onMounted(async () => {
  if (isAuthenticated.value) {
    if (user.value) {
      phone.value = user.value.phone || ''
      firstName.value = user.value.first_name || ''
      email.value = user.value.email || ''
    }
    try {
      savedAddresses.value = await getAddresses()
    } catch {
      // silent
    }
  }
})

// Redirect if cart is empty
watch(() => items.value.length, (len) => {
  if (len === 0) router.push('/')
})

if (items.value.length === 0) {
  router.push('/')
}
</script>

<template>
  <div class="dv-page">
    <!-- Header -->
    <div class="dv-header">
      <button class="dv-back" @click="router.push('/cart-summary')">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5" />
          <path d="M12 19l-7-7 7-7" />
        </svg>
        Wróć
      </button>
    </div>

    <!-- Hero banner -->
    <div class="dv-hero">
      <div class="dv-hero-inner">
        <!-- Delivery / Pickup tabs -->
        <div class="dv-tabs">
          <button class="dv-tab" :class="{ active: deliveryMode === 'delivery' }" @click="deliveryMode = 'delivery'">
            DOSTAWA
          </button>
          <button class="dv-tab" :class="{ active: deliveryMode === 'pickup' }" @click="deliveryMode = 'pickup'">
            ODBIÓR OSOBISTY
          </button>
        </div>

        <div class="dv-mode-info">
          <div class="dv-mode-card" :class="{ active: deliveryMode === 'delivery' }">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <rect x="1" y="3" width="15" height="13" />
              <polygon points="16 8 20 8 23 11 23 16 16 16 16 8" />
              <circle cx="5.5" cy="18.5" r="2.5" />
              <circle cx="18.5" cy="18.5" r="2.5" />
            </svg>
            <!-- <span class="dv-mode-label">Przybliżony czas dostawy:</span> -->
            <!-- <span class="dv-mode-time">45–60 min</span> -->
          </div>
          <div class="dv-mode-card" :class="{ active: deliveryMode === 'pickup' }">
            <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
            <span class="dv-mode-address">ul. Sierakowskiego 2, Piaseczno</span>
            <!-- <span class="dv-mode-label">Przybliżony czas odbioru:</span> -->
            <!-- <span class="dv-mode-time">30–40 min</span> -->
          </div>
        </div>
      </div>
    </div>

    <!-- Main content -->
    <div class="dv-scroll">
      <div class="dv-layout">
        <!-- Left column: form -->
        <div class="dv-form-col">

          <!-- Delivery address (only for delivery mode) -->
          <div v-if="deliveryMode === 'delivery'" class="dv-section">
            <h3 class="dv-section-title">Dane do dostawy</h3>

            <div v-if="savedAddresses.length > 0" class="saved-addr-chips">
              <button v-for="addr in savedAddresses" :key="addr.id" class="addr-chip" @click="selectAddress(addr)">
                <span class="addr-chip-label" v-if="addr.label">{{ addr.label }}:</span>
                {{ addr.street }} {{ addr.house_number }}<template v-if="addr.apartment">/{{ addr.apartment
                }}</template>,
                {{ addr.city }}
              </button>
            </div>

            <div class="dv-field">
              <label class="dv-label">Miasto<span class="req">*</span></label>
              <input v-model="city" type="text" class="dv-input">
            </div>

            <div class="dv-field">
              <label class="dv-label">Ulica<span class="req">*</span></label>
              <input v-model="street" type="text" class="dv-input">
            </div>

            <div class="dv-row">
              <div class="dv-field">
                <label class="dv-label">Numer domu<span class="req">*</span></label>
                <input v-model="houseNumber" type="text" class="dv-input">
              </div>
              <div class="dv-field">
                <label class="dv-label">Mieszkanie</label>
                <input v-model="apartment" type="text" class="dv-input">
              </div>
            </div>

            <div class="dv-field">
              <label class="dv-label">Telefon<span class="req">*</span></label>
              <PhoneInput v-model="phone" :required="true" />
            </div>

            <div class="dv-field">
              <label class="dv-label">Email</label>
              <input v-model="email" type="email" class="dv-input">
            </div>

            <div class="dv-field">
              <label class="dv-label">Notatki dla dostawcy</label>
              <textarea v-model="notes" class="dv-textarea" placeholder="np. 3 piętro, kod do klatki"></textarea>
            </div>
          </div>

          <!-- Pickup info -->
          <div v-else class="dv-section">
            <h3 class="dv-section-title">Odbiór osobisty</h3>
            <p class="dv-pickup-info">
              Zamówienie będzie gotowe do odbioru pod adresem:<br>
              <strong>ul. Sierakowskiego 2, Piaseczno</strong>
            </p>

            <div class="dv-field">
              <label class="dv-label">Telefon<span class="req">*</span></label>
              <PhoneInput v-model="phone" :required="true" />
            </div>
          </div>

          <!-- Scheduling (optional) -->
          <div class="dv-section">
            <h3 class="dv-section-title">
              {{ deliveryMode === 'delivery' ? 'Zaplanuj dostawę' : 'Zaplanuj odbiór' }}
            </h3>
            <p class="schedule-hint">Opcjonalnie — domyślnie zamówienie realizowane jak najszybciej.</p>

            <div class="dv-field">
              <label class="dv-label">Dzień</label>
              <div class="schedule-date-chips">
                <button v-for="opt in dateOptions" :key="opt.value" class="schedule-chip"
                  :class="{ active: scheduledDate === opt.value }"
                  @click="scheduledDate = scheduledDate === opt.value ? null : opt.value">
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <template v-if="scheduledDate">
              <div class="dv-field">
                <label class="dv-label">Godzina</label>
                <div v-if="availableTimeSlots.length === 0" class="schedule-no-slots">
                  Brak dostępnych godzin na wybrany dzień. Wybierz inny termin.
                </div>
                <div v-else class="schedule-time-grid">
                  <button v-for="slot in availableTimeSlots" :key="slot.time" class="schedule-time-btn"
                    :class="{ active: scheduledTime === slot.time, full: slot.full }" :disabled="slot.full"
                    @click="scheduledTime = scheduledTime === slot.time ? '' : slot.time">
                    {{ slot.time }}
                  </button>
                </div>
              </div>
            </template>
          </div>

          <!-- Recipient -->
          <div class="dv-section">
            <h3 class="dv-section-title">Zamówienie odbierze</h3>

            <div class="dv-field">
              <label class="dv-label">Imię<span class="req">*</span></label>
              <input v-model="firstName" type="text" class="dv-input">
            </div>

            <div class="dv-field">
              <label class="dv-label">Nazwisko</label>
              <input v-model="lastName" type="text" class="dv-input">
            </div>
          </div>

          <!-- Payment method -->
          <div class="dv-section">
            <h3 class="dv-section-title">Metoda płatności</h3>

            <div class="pay-group">
              <div class="pay-group-header">ZAPŁAĆ ONLINE</div>
              <div class="pay-options">
                <label class="pay-option" :class="{ selected: paymentMethod === 'blik' }">
                  <input type="radio" v-model="paymentMethod" value="blik">
                  <div class="pay-option-inner">
                    <span class="pay-icon">BLIK</span>
                    <span class="pay-label">BLIK</span>
                  </div>
                </label>
                <label class="pay-option" :class="{ selected: paymentMethod === 'card-online' }">
                  <input type="radio" v-model="paymentMethod" value="card-online">
                  <div class="pay-option-inner">
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="1" y="4" width="22" height="16" rx="2" ry="2" />
                      <line x1="1" y1="10" x2="23" y2="10" />
                    </svg>
                    <span class="pay-label">Karta</span>
                  </div>
                </label>
                <label class="pay-option" :class="{ selected: paymentMethod === 'transfer' }">
                  <input type="radio" v-model="paymentMethod" value="transfer">
                  <div class="pay-option-inner">
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M17 1l4 4-4 4" />
                      <path d="M3 11V9a4 4 0 0 1 4-4h14" />
                      <path d="M7 23l-4-4 4-4" />
                      <path d="M21 13v2a4 4 0 0 1-4 4H3" />
                    </svg>
                    <span class="pay-label">Przelew</span>
                  </div>
                </label>
              </div>
            </div>

            <div class="pay-group">
              <div class="pay-group-header">ZAPŁAĆ PRZY ODBIORZE</div>
              <div class="pay-options">
                <label class="pay-option" :class="{ selected: paymentMethod === 'cash' }">
                  <input type="radio" v-model="paymentMethod" value="cash">
                  <div class="pay-option-inner">
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                      <line x1="12" y1="1" x2="12" y2="23" />
                      <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
                    </svg>
                    <span class="pay-label">Gotówka</span>
                  </div>
                </label>
                <label class="pay-option" :class="{ selected: paymentMethod === 'card-delivery' }">
                  <input type="radio" v-model="paymentMethod" value="card-delivery">
                  <div class="pay-option-inner">
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none"
                      stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="1" y="4" width="22" height="16" rx="2" ry="2" />
                      <line x1="1" y1="10" x2="23" y2="10" />
                    </svg>
                    <span class="pay-label">Karta</span>
                  </div>
                </label>
              </div>
            </div>
          </div>

          <!-- Bonus code -->
          <div class="dv-section">
            <h3 class="dv-section-title">Kod rabatowy</h3>
            <div class="bonus-row">
              <input v-model="bonusCode" type="text" class="dv-input bonus-input" placeholder="Wpisz kod"
                :disabled="bonusApplied">
              <button class="bonus-btn" @click="applyBonus" :disabled="bonusApplied || !bonusCode.trim()">
                Zastosuj
              </button>
            </div>
            <Transition name="toast">
              <span v-if="bonusApplied" class="bonus-success">{{ bonusMessage }}</span>
            </Transition>
            <Transition name="toast">
              <span v-if="bonusError" class="bonus-error">{{ bonusError }}</span>
            </Transition>
          </div>

          <!-- Submit error -->
          <div v-if="submitError" class="submit-error">{{ submitError }}</div>

          <!-- Submit (mobile: below form) -->
          <button class="dv-submit mobile-only" :disabled="!formValid || submitting" @click="submitOrder">
            {{ submitting ? 'Wysyłanie...' : 'Zamawiam' }}
          </button>
        </div>

        <!-- Right column: order summary sidebar -->
        <div class="dv-sidebar">
          <div class="sidebar-sticky">
            <h3 class="sidebar-title">Podsumowanie</h3>

            <div class="sidebar-item" v-for="item in items" :key="item.cartId">
              <div class="sidebar-item-top">
                <span class="sidebar-item-name">
                  {{ item.name }}
                  <span v-if="item.quantity > 1">x{{ item.quantity }}</span>
                </span>
                <span class="sidebar-item-price">{{ calcItemTotal(item) }} zł</span>
              </div>
              <span v-if="summarize(item)" class="sidebar-item-details">{{ summarize(item) }}</span>
            </div>

            <div class="sidebar-divider"></div>

            <div class="sidebar-row">
              <span>Dostawa</span>
              <span class="sidebar-tbd">do ustalenia</span>
            </div>

            <div v-if="scheduledTime" class="sidebar-row">
              <span>{{ deliveryMode === 'delivery' ? 'Dostawa' : 'Odbior' }}</span>
              <span>{{ formatDateLabel(scheduledDate) }}, {{ scheduledTime }}</span>
            </div>

            <div v-if="bonusApplied && discountAmount > 0" class="sidebar-row sidebar-discount">
              <span>{{ discountLabel }}</span>
              <span>-{{ discountAmount }} zl</span>
            </div>

            <div class="sidebar-divider"></div>

            <div class="sidebar-total">
              <span>SUMA</span>
              <strong>{{ finalTotal }} zł</strong>
            </div>

            <!-- Submit error in sidebar -->
            <div v-if="submitError" class="submit-error">{{ submitError }}</div>

            <!-- Submit (desktop: in sidebar) -->
            <button class="dv-submit desktop-only" :disabled="!formValid || submitting" @click="submitOrder">
              {{ submitting ? 'Wysyłanie...' : 'Zamawiam' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dv-page {
  min-height: 100vh;
  background: var(--white);
  display: flex;
  flex-direction: column;
  /* padding-top: 60px; */
}

/* Header */
.dv-header {
  display: flex;
  align-items: center;
  padding: 0.9rem 2rem;
  background: var(--white);
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}

.dv-back {
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

.dv-back:hover {
  background: rgba(0, 146, 70, 0.08);
}

/* Hero banner */
.dv-hero {
  background: linear-gradient(rgba(0, 0, 0, 0.55), rgba(0, 0, 0, 0.55)),
    url('https://images.unsplash.com/photo-1513104890138-7c749659a591?w=1600') center/cover;
  flex-shrink: 0;
  padding-top: 2rem;
  padding-bottom: 2rem;
}

.dv-hero-inner {
  max-width: 680px;
  margin: 0 auto;
  padding: 1.5rem;
}

/* Tabs */
.dv-tabs {
  display: flex;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 1.5rem;
}

.dv-tab {
  flex: 1;
  padding: 0.75rem 1rem;
  background: transparent;
  border: none;
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.2s;
}

.dv-tab.active {
  background: var(--white);
  color: var(--green);
}

/* Mode info */
.dv-mode-info {
  display: flex;
  gap: 1.5rem;
}

.dv-mode-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 0.4rem;
  color: rgba(255, 255, 255, 0.5);
  transition: color 0.2s;
}

.dv-mode-card.active {
  color: var(--white);
}

.dv-mode-card svg {
  margin-bottom: 0.3rem;
}

.dv-mode-address {
  font-size: 0.8rem;
  font-weight: 500;
}

.dv-mode-label {
  font-size: 0.8rem;
}

.dv-mode-time {
  font-size: 1.1rem;
  font-weight: 700;
}

/* Scroll area */
.dv-scroll {
  flex: 1;
  overflow-y: auto;
}

/* Two-column layout */
.dv-layout {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2.5rem;
  align-items: start;
}

/* Form column */
.dv-form-col {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.dv-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.dv-section-title {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--dark);
  margin-bottom: 0.25rem;
}

.dv-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.dv-label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
}

.req {
  color: var(--red);
  margin-left: 2px;
}

.dv-input {
  padding: 0.7rem 0.75rem;
  border: 1.5px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
  width: 100%;
  box-sizing: border-box;
}

.dv-input:focus {
  border-color: var(--green);
}

.dv-textarea {
  padding: 0.7rem 0.75rem;
  border: 1.5px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  outline: none;
  font-family: inherit;
  resize: vertical;
  min-height: 80px;
  transition: border-color 0.2s;
  width: 100%;
  box-sizing: border-box;
}

.dv-textarea:focus {
  border-color: var(--green);
}

.dv-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.dv-pickup-info {
  font-size: 0.95rem;
  color: #555;
  line-height: 1.6;
}

.dv-pickup-info strong {
  color: var(--dark);
}

/* Payment */
.pay-group {
  margin-bottom: 1rem;
}

.pay-group:last-child {
  margin-bottom: 0;
}

.pay-group-header {
  background: var(--green);
  color: var(--white);
  padding: 0.6rem 1rem;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  border-radius: 6px 6px 0 0;
}

.pay-options {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
  border: 1.5px solid #ddd;
  border-top: none;
  border-radius: 0 0 6px 6px;
  overflow: hidden;
}

.pay-option {
  flex: 1;
  min-width: 100px;
  cursor: pointer;
  border-right: 1px solid #eee;
  transition: background 0.2s;
}

.pay-option:last-child {
  border-right: none;
}

.pay-option input[type="radio"] {
  display: none;
}

.pay-option-inner {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 1rem 0.5rem;
  min-height: 80px;
}

.pay-icon {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--dark);
}

.pay-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #555;
}

.pay-option.selected {
  background: rgba(0, 146, 70, 0.06);
  box-shadow: inset 0 0 0 2px var(--green);
}

.pay-option.selected .pay-label {
  color: var(--red);
}

/* Scheduling */
.schedule-date-chips {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.schedule-chip {
  padding: 0.55rem 1rem;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  background: var(--white);
  font-size: 0.9rem;
  font-family: inherit;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  text-transform: capitalize;
}

.schedule-chip:hover {
  border-color: var(--green);
  color: var(--green);
}

.schedule-chip.active {
  background: var(--green);
  color: var(--white);
  border-color: var(--green);
}

.schedule-time-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.schedule-time-btn {
  padding: 0.45rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: var(--white);
  font-size: 0.85rem;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.15s;
}

.schedule-time-btn:hover {
  border-color: var(--green);
  color: var(--green);
}

.schedule-time-btn.active {
  background: var(--green);
  color: var(--white);
  border-color: var(--green);
}

.schedule-hint {
  font-size: 0.85rem;
  color: var(--red);
  font-weight: 500;
  margin: -0.25rem 0 0.25rem;
}

.schedule-no-slots {
  font-size: 0.9rem;
  color: #999;
  font-style: italic;
  padding: 0.5rem 0;
}

.schedule-time-btn.full {
  opacity: 0.35;
  cursor: not-allowed;
  text-decoration: line-through;
  border-color: #e0e0e0;
  background: #f5f5f5;
}

.schedule-time-btn.full:hover {
  border-color: #e0e0e0;
  color: inherit;
}

/* Bonus code */
.bonus-row {
  display: flex;
  gap: 0.5rem;
}

.bonus-input {
  flex: 1;
}

.bonus-btn {
  background: var(--green);
  color: var(--white);
  border: none;
  padding: 0.7rem 1.2rem;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
  white-space: nowrap;
}

.bonus-btn:hover:not(:disabled) {
  background: #007a3a;
}

.bonus-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.bonus-success {
  color: var(--green);
  font-size: 0.85rem;
  font-weight: 600;
}

.bonus-error {
  color: var(--red);
  font-size: 0.85rem;
  font-weight: 600;
}

/* Submit error */
.submit-error {
  color: var(--red);
  font-size: 0.9rem;
  font-weight: 600;
  text-align: center;
  padding: 0.5rem;
  background: rgba(206, 43, 55, 0.06);
  border-radius: 6px;
}

/* Sidebar */
.dv-sidebar {
  position: relative;
}

.sidebar-sticky {
  position: sticky;
  top: 0;
  background: var(--light-gray);
  border-radius: 10px;
  padding: 1.25rem;
}

.sidebar-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--dark);
  margin-bottom: 1rem;
}

.sidebar-item {
  margin-bottom: 0.75rem;
}

.sidebar-item-top {
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.sidebar-item-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--dark);
}

.sidebar-item-price {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--dark);
  white-space: nowrap;
}

.sidebar-item-details {
  font-size: 0.75rem;
  color: #888;
  display: block;
  margin-top: 0.15rem;
}

.sidebar-divider {
  height: 1px;
  background: #ddd;
  margin: 0.75rem 0;
}

.sidebar-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #555;
}

.sidebar-discount {
  color: var(--green);
  font-weight: 600;
}

.sidebar-tbd {
  font-style: italic;
  color: #999;
}

.sidebar-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.05rem;
  font-weight: 700;
}

.sidebar-total strong {
  color: var(--green);
  font-size: 1.15rem;
}

/* Submit button */
.dv-submit {
  width: 100%;
  background: var(--green);
  color: var(--white);
  padding: 1rem;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  cursor: pointer;
  transition: background 0.3s;
  margin-top: 1rem;
}

.dv-submit:hover:not(:disabled) {
  background: #007a3a;
}

.dv-submit:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.mobile-only {
  display: none;
}

.desktop-only {
  display: block;
}

/* Transitions */
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
}

/* Saved address chips */
.saved-addr-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.addr-chip {
  background: var(--light-gray);
  border: 1.5px solid #ddd;
  border-radius: 20px;
  padding: 0.45rem 0.9rem;
  font-size: 0.82rem;
  font-family: inherit;
  color: var(--dark);
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.addr-chip:hover {
  border-color: var(--green);
  background: rgba(0, 146, 70, 0.06);
}

.addr-chip-label {
  font-weight: 700;
  color: var(--green);
}

/* Responsive */
@media (max-width: 768px) {
  .dv-layout {
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1.25rem 1rem 2rem;
  }

  .dv-sidebar {
    order: -1;
  }

  .sidebar-sticky {
    position: static;
  }

  .mobile-only {
    display: block;
  }

  .desktop-only {
    display: none;
  }

  .dv-header {
    padding: 0.75rem 1rem;
  }

  .dv-hero-inner {
    padding: 1rem;
  }

  .dv-tab {
    font-size: 0.8rem;
    padding: 0.6rem 0.5rem;
  }

  .dv-mode-info {
    flex-direction: column;
    gap: 1rem;
  }

  .dv-mode-card svg {
    width: 28px;
    height: 28px;
  }

  .pay-option {
    min-width: 0;
  }

  .bonus-row {
    flex-wrap: wrap;
  }

  .bonus-input {
    min-width: 0;
  }
}
</style>
