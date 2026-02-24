<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '@/composables/useCart'

const router = useRouter()
const { items, totalPrice, meetsMinimum, MIN_ORDER, calcItemTotal, updateQuantity, removeItem } = useCart()

const expandedItem = ref(null)

function toggleExpand(cartId) {
  expandedItem.value = expandedItem.value === cartId ? null : cartId
}

function handleRemove(cartId) {
  removeItem(cartId)
  if (expandedItem.value === cartId) expandedItem.value = null
}

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

// Auto-redirect to home if cart becomes empty
watch(() => items.value.length, (len) => {
  if (len === 0) router.push('/')
})

// Redirect immediately if cart is already empty on mount
if (items.value.length === 0) {
  router.push('/')
}
</script>

<template>
  <div class="order-page">
    <!-- Header -->
    <div class="order-header">
      <button class="order-back" @click="router.push('/')">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M19 12H5"/><path d="M12 19l-7-7 7-7"/>
        </svg>
        Wróć
      </button>
    </div>

    <!-- Content -->
    <div class="order-scroll">
      <div class="order-content">

        <!-- Order heading -->
        <div class="order-heading">
          <h2>Twoje zamówienie</h2>
          <span class="order-heading-total">{{ totalPrice }} zł</span>
        </div>

        <!-- Items list -->
        <div class="order-items">
          <div class="order-item" v-for="item in items" :key="item.cartId">
            <div class="item-top">
              <div class="item-name-col">
                <span class="item-name">{{ item.name }}</span>
                <span v-if="item.quantity > 1" class="item-qty-badge">x{{ item.quantity }}</span>
              </div>
              <div class="item-right">
                <button class="item-delete" @click="handleRemove(item.cartId)" aria-label="Usuń">
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"/><path d="M19 6l-2 14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L5 6"/>
                    <path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/>
                  </svg>
                </button>
                <span class="item-price">{{ calcItemTotal(item) }} zł</span>
              </div>
            </div>

            <div class="item-details">
              <span v-if="summarize(item)" class="item-summary">{{ summarize(item) }}</span>
            </div>

            <div class="item-controls">
              <div class="item-qty-control">
                <button class="qty-btn" @click="updateQuantity(item.cartId, item.quantity - 1)">-</button>
                <span class="qty-val">{{ item.quantity }}</span>
                <button class="qty-btn" @click="updateQuantity(item.cartId, item.quantity + 1)">+</button>
              </div>
              <button class="item-modify" @click="toggleExpand(item.cartId)">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
                </svg>
                Zmień
              </button>
            </div>

            <!-- Inline edit accordion -->
            <Transition name="expand">
              <div v-if="expandedItem === item.cartId" class="item-edit">
                <div v-if="item.ingredients && item.ingredients.length" class="edit-group">
                  <h4 class="edit-group-title">Składniki</h4>
                  <label v-for="(ing, i) in item.ingredients" :key="'ing-' + i" class="edit-row">
                    <div class="edit-left">
                      <input type="checkbox" v-model="ing.included">
                      <span>{{ ing.name }}</span>
                    </div>
                    <span v-if="ing.price" class="edit-price">+{{ ing.price }} zł</span>
                  </label>
                </div>
                <div v-if="item.extras && item.extras.length" class="edit-group">
                  <h4 class="edit-group-title">Dodatki</h4>
                  <label v-for="(ext, i) in item.extras" :key="'ext-' + i" class="edit-row">
                    <div class="edit-left">
                      <input type="checkbox" v-model="ext.selected">
                      <span>{{ ext.name }}</span>
                    </div>
                    <span class="edit-price">+{{ ext.price }} zł</span>
                  </label>
                </div>
              </div>
            </Transition>
          </div>
        </div>

        <!-- Cost breakdown -->
        <div class="cost-section">
          <h3 class="cost-title">KOSZT ZAMÓWIENIA</h3>
          <div class="cost-row">
            <span>Produkty</span>
            <span>{{ totalPrice }} zł</span>
          </div>
          <div class="cost-row">
            <span>Dostawa</span>
            <span class="cost-tbd">do ustalenia</span>
          </div>
          <div class="cost-total">
            <span>Razem</span>
            <strong>{{ totalPrice }} zł</strong>
          </div>
        </div>

        <!-- Minimum order warning -->
        <div v-if="!meetsMinimum" class="min-warning">
          Minimalna wartość zamówienia: {{ MIN_ORDER }} zł
        </div>

        <!-- DALEJ button -->
        <button class="btn-proceed" :disabled="!meetsMinimum" @click="router.push('/order-summary')">
          DALEJ
        </button>

      </div>
    </div>
  </div>
</template>

<style scoped>
.order-page {
  min-height: 100vh;
  background: var(--white);
  display: flex;
  flex-direction: column;
  /* padding-top: 60px; */
}

/* Header */
.order-header {
  display: flex;
  align-items: center;
  padding: 0.9rem 2rem;
  background: var(--white);
  border-bottom: 1px solid #eee;
  flex-shrink: 0;
}

.order-back {
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

.order-back:hover {
  background: rgba(0, 146, 70, 0.08);
}

/* Scrollable body */
.order-scroll {
  flex: 1;
  overflow-y: auto;
}

.order-content {
  max-width: 680px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem;
}

/* Heading */
.order-heading {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1.5rem;
}

.order-heading h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--dark);
}

.order-heading-total {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--dark);
}

/* Items */
.order-items {
  margin-bottom: 2rem;
}

.order-item {
  padding: 1.25rem 0;
  border-bottom: 1px solid #eee;
}

.order-item:first-child {
  padding-top: 0;
}

.order-item:last-child {
  border-bottom: none;
}

.item-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}

.item-name-col {
  display: flex;
  align-items: baseline;
  gap: 0.5rem;
}

.item-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--dark);
}

.item-qty-badge {
  font-size: 0.85rem;
  font-weight: 600;
  color: #888;
}

.item-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.item-delete {
  background: none;
  border: none;
  color: #bbb;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.item-delete:hover {
  color: var(--red);
}

.item-price {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--dark);
}

.item-details {
  margin-top: 0.3rem;
}

.item-summary {
  font-size: 0.85rem;
  color: #888;
  line-height: 1.4;
}

.item-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.6rem;
}

.item-qty-control {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.qty-btn {
  width: 1.6rem;
  height: 1.6rem;
  border-radius: 50%;
  border: 1.5px solid var(--green);
  background: transparent;
  color: var(--green);
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
}

.qty-btn:hover {
  background: var(--green);
  color: var(--white);
}

.qty-val {
  font-weight: 700;
  font-size: 0.95rem;
  min-width: 1.4rem;
  text-align: center;
}

.item-modify {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  background: none;
  border: none;
  color: var(--green);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.item-modify:hover {
  background: rgba(0, 146, 70, 0.08);
}

/* Inline edit */
.item-edit {
  margin-top: 0.75rem;
  background: var(--light-gray);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  overflow: hidden;
}

.edit-group-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--dark);
  text-transform: uppercase;
  letter-spacing: 0.03em;
  margin-bottom: 0.3rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid #e0e0e0;
}

.edit-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.25rem 0;
  cursor: pointer;
  font-size: 0.9rem;
}

.edit-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.edit-left input[type="checkbox"] {
  accent-color: var(--green);
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.edit-price {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--green);
}

/* Cost breakdown */
.cost-section {
  border-top: 2px solid var(--dark);
  padding-top: 1.25rem;
  margin-bottom: 1.5rem;
}

.cost-title {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--dark);
  margin-bottom: 1rem;
}

.cost-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.4rem 0;
  font-size: 0.95rem;
  color: #555;
}

.cost-tbd {
  font-style: italic;
  color: #999;
}

.cost-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  margin-top: 0.5rem;
  border-top: 1px solid #eee;
  font-size: 1.3rem;
}

.cost-total strong {
  color: var(--green);
  font-size: 1.4rem;
}

/* Min warning */
.min-warning {
  text-align: center;
  color: var(--red);
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

/* Proceed button */
.btn-proceed {
  display: block;
  width: 100%;
  background: var(--green);
  color: var(--white);
  padding: 1rem;
  border: none;
  border-radius: 8px;
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-proceed:hover:not(:disabled) {
  background: #007a3a;
}

.btn-proceed:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Transitions */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.25s ease;
  max-height: 500px;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
  margin-top: 0;
  padding: 0 1rem;
}

/* Responsive */
@media (max-width: 600px) {
  .order-content {
    padding: 1.25rem 1rem 2rem;
  }

  .order-heading h2 {
    font-size: 1.25rem;
  }

  .order-heading-total {
    font-size: 1.25rem;
  }

  .order-header {
    padding: 0.75rem 1rem;
  }

  .item-edit {
    margin-left: 0;
  }
}
</style>
