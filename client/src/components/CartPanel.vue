<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useCart } from '@/composables/useCart'

const props = defineProps({ isOpen: Boolean })
const emit = defineEmits(['close'])

const router = useRouter()
const { items, totalPrice, meetsMinimum, MIN_ORDER, calcItemTotal, updateQuantity, removeItem, clearCart, requestEdit } = useCart()

const showMinWarning = ref(false)

function handleOrder() {
  if (!meetsMinimum.value) {
    showMinWarning.value = true
  } else {
    showMinWarning.value = false
    emit('close')
    router.push('/cart-summary')
  }
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

function handleEdit(cartId) {
  requestEdit(cartId)
  emit('close')
}

watch(() => props.isOpen, (val) => {
  document.body.style.overflow = val ? 'hidden' : ''
})
</script>

<template>
  <Teleport to="body">
    <Transition name="cart-fade">
      <div v-if="isOpen" class="cart-backdrop" @click.self="$emit('close')">
        <Transition name="cart-slide">
          <div v-if="isOpen" class="cart-panel">
            <div class="cart-header">
              <h3>Twój koszyk</h3>
              <button class="cart-close" @click="$emit('close')">&times;</button>
            </div>

            <div v-if="items.length === 0" class="cart-empty">
              Koszyk jest pusty
            </div>

            <div v-else class="cart-items">
              <div class="cart-item" v-for="item in items" :key="item.cartId">
                <img :src="item.image" :alt="item.name" class="cart-item-img">
                <div class="cart-item-details">
                  <span class="cart-item-name">{{ item.name }}</span>
                  <span v-if="summarize(item)" class="cart-item-summary">{{ summarize(item) }}</span>
                  <span class="cart-item-price">{{ calcItemTotal(item) }} zł</span>
                  <div class="cart-item-actions">
                    <div class="cart-qty">
                      <button class="cart-qty-btn" @click="updateQuantity(item.cartId, item.quantity - 1)">-</button>
                      <span class="cart-qty-val">{{ item.quantity }}</span>
                      <button class="cart-qty-btn" @click="updateQuantity(item.cartId, item.quantity + 1)">+</button>
                    </div>
                    <button class="cart-btn-edit" @click="handleEdit(item.cartId)">Edytuj</button>
                    <button class="cart-btn-remove" @click="removeItem(item.cartId)">Usuń</button>
                  </div>
                </div>
              </div>
            </div>

            <div v-if="items.length" class="cart-footer">
              <button class="cart-btn-clear" @click="clearCart">Wyczyść koszyk</button>
              <div class="cart-total">
                <span>Razem:</span>
                <strong>{{ totalPrice }} zł</strong>
              </div>
              <span v-if="showMinWarning && !meetsMinimum" class="cart-min-warning">Minimalna wartość zamówienia: {{ MIN_ORDER }} zł</span>
              <button class="cart-btn-order" @click="handleOrder">Zamów</button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<style scoped>
.cart-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1100;
}

.cart-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 400px;
  max-width: 100%;
  height: 100%;
  background: var(--white);
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  z-index: 1101;
}

.cart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #eee;
}

.cart-header h3 {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--dark);
  margin: 0;
}

.cart-close {
  background: none;
  border: none;
  font-size: 1.75rem;
  cursor: pointer;
  color: var(--dark);
  line-height: 1;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.cart-close:hover {
  background: rgba(0, 0, 0, 0.08);
}

.cart-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 1.05rem;
}

.cart-items {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.5rem;
}

.cart-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.cart-item:last-child {
  border-bottom: none;
}

.cart-item-img {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
  flex-shrink: 0;
}

.cart-item-details {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  flex: 1;
  min-width: 0;
}

.cart-item-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--dark);
}

.cart-item-summary {
  font-size: 0.8rem;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cart-item-price {
  font-weight: 700;
  color: var(--green);
  font-size: 0.95rem;
}

.cart-item-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.cart-qty {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.cart-qty-btn {
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

.cart-qty-btn:hover {
  background: var(--green);
  color: var(--white);
}

.cart-qty-val {
  font-size: 0.9rem;
  font-weight: 700;
  min-width: 1.2rem;
  text-align: center;
}

.cart-btn-edit,
.cart-btn-remove {
  background: none;
  border: none;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.15rem 0.3rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.cart-btn-edit {
  color: var(--green);
}

.cart-btn-edit:hover {
  background: rgba(0, 146, 70, 0.08);
}

.cart-btn-remove {
  color: var(--red);
}

.cart-btn-remove:hover {
  background: rgba(206, 43, 55, 0.08);
}

.cart-footer {
  border-top: 1px solid #eee;
  padding: 1rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.cart-btn-clear {
  background: none;
  border: none;
  color: #999;
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  align-self: flex-start;
  padding: 0;
  transition: color 0.2s;
}

.cart-btn-clear:hover {
  color: var(--red);
}

.cart-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1.1rem;
}

.cart-total strong {
  color: var(--green);
  font-size: 1.25rem;
}

.cart-btn-order {
  width: 100%;
  background: var(--green);
  color: var(--white);
  padding: 0.85rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.3s;
}

.cart-btn-order:hover {
  background: #007a3a;
}

.cart-min-warning {
  color: var(--red);
  font-size: 0.85rem;
  font-weight: 600;
  text-align: center;
}

/* Transitions */
.cart-fade-enter-active,
.cart-fade-leave-active {
  transition: opacity 0.25s ease;
}

.cart-fade-enter-from,
.cart-fade-leave-to {
  opacity: 0;
}

.cart-slide-enter-active,
.cart-slide-leave-active {
  transition: transform 0.3s ease;
}

.cart-slide-enter-from,
.cart-slide-leave-to {
  transform: translateX(100%);
}

@media (max-width: 480px) {
  .cart-panel {
    width: 100%;
  }
}
</style>
