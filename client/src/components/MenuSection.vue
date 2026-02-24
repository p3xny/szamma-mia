<template>
  <section id="menu" class="menu">
    <h2 class="section-title">Nasze Menu</h2>
    <p class="section-subtitle">Świeże składniki, tradycyjne włoskie dania</p>

    <div class="category-tabs">
      <button
        v-for="cat in categories"
        :key="cat.key"
        class="category-tab"
        :class="{ active: activeCategory === cat.key }"
        @click="activeCategory = cat.key"
      >
        <span v-if="cat.key === 'daily'" class="tab-star">&#9733;</span>
        {{ cat.label }}
      </button>
    </div>

    <div v-if="loading" class="menu-status">Ładowanie menu...</div>
    <div v-else-if="error" class="menu-status menu-error">
      {{ error }}
      <button class="btn-retry" @click="fetchMenu">Spróbuj ponownie</button>
    </div>

    <div v-else class="dishes-grid">
      <div class="dish-card" v-for="dish in filteredDishes" :key="dish.id" @click="openModal(dish)">
        <div class="dish-image-wrapper">
          <img :src="dish.image" :alt="dish.name">
          <span v-if="dish.dailySpecial" class="badge-daily">Danie Dnia</span>
        </div>
        <div class="dish-info">
          <span class="dish-name">{{ dish.name }}</span>
          <span class="dish-price">
            <span v-if="dish.originalPrice" class="price-original">{{ dish.originalPrice }} zł</span>
            {{ dish.price }} zł
          </span>
        </div>
        <button class="btn-add-cart">Dodaj do koszyka</button>
      </div>
    </div>

    <!-- Customization Modal -->
    <Teleport to="body">
      <div v-if="selectedDish" class="modal-backdrop" @click.self="closeModal">
        <div class="modal" @keydown.escape="closeModal">
          <button class="modal-close" @click="closeModal">&times;</button>

          <div class="modal-header">
            <img :src="selectedDish.image" :alt="selectedDish.name" class="modal-image">
            <div class="modal-header-info">
              <h3 class="modal-dish-name">{{ selectedDish.name }}</h3>
              <span class="modal-base-price">Cena bazowa: {{ selectedDish.price }} zł</span>
            </div>
          </div>

          <div class="modal-body">
            <!-- Ingredients -->
            <div v-if="selectedDish.ingredients && selectedDish.ingredients.length" class="modal-section">
              <h4 class="modal-section-title">Składniki</h4>
              <label
                v-for="(ing, i) in selectedDish.ingredients"
                :key="'ing-' + i"
                class="checkbox-row"
              >
                <div class="checkbox-left">
                  <input type="checkbox" v-model="ing.included">
                  <span>{{ ing.name }}</span>
                </div>
                <span v-if="ing.price" class="price-badge">+{{ ing.price }} zł</span>
              </label>
            </div>

            <!-- Extras -->
            <div v-if="selectedDish.extras && selectedDish.extras.length" class="modal-section">
              <h4 class="modal-section-title">Dodatki</h4>
              <label
                v-for="(ext, i) in selectedDish.extras"
                :key="'ext-' + i"
                class="checkbox-row"
              >
                <div class="checkbox-left">
                  <input type="checkbox" v-model="ext.selected">
                  <span>{{ ext.name }}</span>
                </div>
                <span class="price-badge">+{{ ext.price }} zł</span>
              </label>
            </div>

            <!-- Quantity -->
            <div class="modal-section">
              <h4 class="modal-section-title">Ilość</h4>
              <div class="quantity-control">
                <button class="qty-btn" @click="decrementQty">-</button>
                <span class="qty-value">{{ quantity }}</span>
                <button class="qty-btn" @click="quantity++">+</button>
              </div>
            </div>
          </div>

          <button class="modal-cta" @click="handleModalCta">
            {{ editingCartId ? 'Zapisz zmiany' : 'Dodaj do koszyka' }} — {{ modalTotal }} zł
          </button>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useCart } from '@/composables/useCart'

const { addItem, updateItem, editRequest, clearEditRequest, calcItemTotal } = useCart()
const emit = defineEmits(['open-cart'])

const editingCartId = ref(null)

const categories = ref([{ key: 'daily', label: 'Dania Dnia' }])
const activeCategory = ref('daily')
const dishes = ref([])
const loading = ref(true)
const error = ref(null)

async function fetchMenu() {
  loading.value = true
  error.value = null
  try {
    const [menuRes, catRes] = await Promise.all([
      fetch('/api/menu'),
      fetch('/api/categories'),
    ])
    if (!menuRes.ok || !catRes.ok) throw new Error('Nie udało się załadować menu')
    dishes.value = await menuRes.json()
    const dbCategories = await catRes.json()
    categories.value = [{ key: 'daily', label: 'Dania Dnia' }, ...dbCategories]
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}

onMounted(fetchMenu)

const filteredDishes = computed(() => {
  if (activeCategory.value === 'daily') {
    return dishes.value.filter(d => d.dailySpecial)
  }
  return dishes.value.filter(d => d.category === activeCategory.value)
})

// Modal state
const selectedDish = ref(null)
const quantity = ref(1)

function openModal(dish) {
  editingCartId.value = null
  selectedDish.value = JSON.parse(JSON.stringify(dish))
  if (selectedDish.value.extras) {
    selectedDish.value.extras.forEach(ext => { ext.selected = false })
  }
  quantity.value = 1
}

function closeModal() {
  selectedDish.value = null
  editingCartId.value = null
}

// Edit-from-cart flow
watch(editRequest, (req) => {
  if (!req) return
  editingCartId.value = req.cartId
  selectedDish.value = {
    id: req.dishId,
    name: req.name,
    image: req.image,
    price: req.price,
    ingredients: JSON.parse(JSON.stringify(req.ingredients || [])),
    extras: JSON.parse(JSON.stringify(req.extras || [])),
  }
  quantity.value = req.quantity
  clearEditRequest()
})

function handleModalCta() {
  if (!selectedDish.value) return
  if (editingCartId.value) {
    updateItem(
      editingCartId.value,
      selectedDish.value.ingredients,
      selectedDish.value.extras,
      quantity.value
    )
  } else {
    addItem(selectedDish.value, selectedDish.value.ingredients, selectedDish.value.extras, quantity.value)
    // emit('open-cart')
  }
  closeModal()
}

function decrementQty() {
  if (quantity.value > 1) quantity.value--
}

const modalTotal = computed(() => {
  if (!selectedDish.value) return 0
  return calcItemTotal({
    price: selectedDish.value.price,
    ingredients: selectedDish.value.ingredients,
    extras: selectedDish.value.extras,
    quantity: quantity.value,
  })
})

// Lock body scroll when modal is open
watch(selectedDish, (val) => {
  document.body.style.overflow = val ? 'hidden' : ''
})

// Handle Escape key
function onKeydown(e) {
  if (e.key === 'Escape' && selectedDish.value) closeModal()
}

if (typeof window !== 'undefined') {
  window.addEventListener('keydown', onKeydown)
}

onBeforeUnmount(() => {
  document.body.style.overflow = ''
  if (typeof window !== 'undefined') {
    window.removeEventListener('keydown', onKeydown)
  }
})
</script>

<style scoped>
.menu {
  background: var(--light-gray);
  padding: 4rem 5%;

  font-family: 'Nocturne', serif;
}

.section-title {
  text-align: center;
  font-size: 2rem;
  margin-bottom: 0.5rem;
  color: var(--dark);
}

.section-subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
}

.category-tabs {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 2.5rem;
}

.category-tab {
  padding: 0.5rem 1.25rem;
  border: 2px solid var(--green);
  border-radius: 999px;
  background: transparent;
  color: var(--green);
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.25s, color 0.25s;
}

.category-tab:hover {
  background: rgba(0, 128, 0, 0.08);
}

.category-tab.active {
  background: var(--green);
  color: var(--white);
}

.tab-star {
  margin-right: 0.25rem;
  font-size: 0.85em;
}

.menu-status {
  text-align: center;
  padding: 3rem 1rem;
  color: #666;
  font-size: 1.1rem;
}

.menu-error {
  color: var(--red);
}

.btn-retry {
  display: inline-block;
  margin-top: 1rem;
  padding: 0.5rem 1.25rem;
  border: 2px solid var(--green);
  border-radius: 999px;
  background: transparent;
  color: var(--green);
  font-weight: 600;
  cursor: pointer;
  transition: background 0.25s, color 0.25s;
}

.btn-retry:hover {
  background: var(--green);
  color: var(--white);
}

.dishes-grid {
  display: grid;
  grid-template-columns: repeat(3, 360px);
  justify-content: center;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.dish-card {
  background: var(--white);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s;
}

.dish-card:hover {
  transform: translateY(-5px);
  cursor: pointer;
}

.dish-image-wrapper {
  position: relative;
}

.dish-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  display: block;
}

.badge-daily {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  background: var(--red, #d32f2f);
  color: var(--white);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.dish-info {
  padding: 1.25rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dish-name {
  font-weight: 600;
  font-size: 1.1rem;
}

.dish-price {
  color: var(--green);
  font-weight: 700;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.price-original {
  color: #999;
  font-size: 0.85rem;
  font-weight: 400;
  text-decoration: line-through;
}

.btn-add-cart {
  width: 100%;
  background: var(--green);
  color: var(--white);
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0 0 8px 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s;
}

.btn-add-cart:hover {
  background: #007a3a;
}

/* Modal styles */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: var(--white, #fff);
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-close {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  background: none;
  border: none;
  font-size: 1.75rem;
  cursor: pointer;
  color: var(--dark, #333);
  line-height: 1;
  z-index: 1;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.08);
}

.modal-header {
  display: flex;
  gap: 1rem;
  padding: 1.5rem 1.5rem 0;
  align-items: center;
}

.modal-image {
  width: 120px;
  height: 120px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.modal-header-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.modal-dish-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--dark, #333);
  margin: 0;
}

.modal-base-price {
  font-size: 1rem;
  color: var(--green);
  font-weight: 600;
}

.modal-body {
  padding: 1rem 1.5rem;
}

.modal-section {
  margin-bottom: 1.25rem;
}

.modal-section-title {
  font-size: 0.9rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #888;
  margin: 0 0 0.5rem;
  padding-bottom: 0.35rem;
  border-bottom: 1px solid #eee;
}

.checkbox-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.4rem 0;
  cursor: pointer;
}

.checkbox-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.checkbox-row input[type="checkbox"] {
  width: 1.1rem;
  height: 1.1rem;
  accent-color: var(--green);
  cursor: pointer;
}

.price-badge {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--green);
  background: rgba(0, 128, 0, 0.08);
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.quantity-control {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.qty-btn {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 50%;
  border: 2px solid var(--green);
  background: transparent;
  color: var(--green);
  font-size: 1.25rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
}

.qty-btn:hover {
  background: var(--green);
  color: var(--white, #fff);
}

.qty-value {
  font-size: 1.2rem;
  font-weight: 700;
  min-width: 1.5rem;
  text-align: center;
}

.modal-cta {
  width: calc(100% - 3rem);
  margin: 0 1.5rem 1.5rem;
  background: var(--green);
  color: var(--white, #fff);
  padding: 0.85rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.3s;
}

.modal-cta:hover {
  background: #007a3a;
}

@media (max-width: 1180px) {
  .dishes-grid {
    grid-template-columns: repeat(2, 340px);
  }
}

@media (max-width: 768px) {
  .dishes-grid {
    grid-template-columns: 1fr;
  }

  .category-tabs {
    gap: 0.4rem;
  }

  .category-tab {
    padding: 0.4rem 0.9rem;
    font-size: 0.85rem;
  }

  .modal {
    max-width: calc(100% - 1rem);
  }

  .modal-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .modal-image {
    width: 100%;
    height: 160px;
  }
}
</style>
