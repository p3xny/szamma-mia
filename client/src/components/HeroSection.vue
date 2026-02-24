<template>
  <section class="hero" id="home">
    <FlagAccent />
    <h1>Szamma Mia</h1>
    <p>Autentyczna Włoska kuchnia w sercu miasta</p>
    <button class="btn-order" @click="handleOrder">Zamów Online</button>
    <Transition name="toast">
      <span v-if="showEmptyMsg" class="empty-toast">Koszyk jest pusty — dodaj coś z menu!</span>
    </Transition>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import FlagAccent from './FlagAccent.vue'
import { useCart } from '@/composables/useCart'

const router = useRouter()
const { itemCount } = useCart()

const showEmptyMsg = ref(false)
let emptyTimer = null

function handleOrder() {
  if (itemCount.value === 0) {
    showEmptyMsg.value = true
    clearTimeout(emptyTimer)
    emptyTimer = setTimeout(() => { showEmptyMsg.value = false }, 3000)
  } else {
    router.push('/cart-summary')
  }
}
</script>

<style scoped>
.hero {
  min-height: 100dvh;
  background: linear-gradient(rgba(0, 0, 0, 0.5), rgba(0, 0, 0, 0.5)),
    url('https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1600') center/cover;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  color: var(--white);
  padding-top: 60px;

  font-family: 'Nocturne', serif;
}

.hero h1 {
  font-size: 3.5rem;
  margin-bottom: 1rem;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.hero p {
  font-size: 1.3rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.btn-order {
  background: var(--red);
  color: var(--white);
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.3s, transform 0.2s;
}

.btn-order:hover {
  background: #b02530;
  transform: translateY(-2px);
}

.empty-toast {
  margin-top: 1rem;
  background: rgba(0, 0, 0, 0.7);
  color: var(--white);
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2.5rem;
  }
}
</style>
