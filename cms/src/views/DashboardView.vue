<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api.js'

const stats = ref({ dishes: 0, categories: 0, coupons: 0 })
const loading = ref(true)

onMounted(async () => {
  try {
    const [dishes, categories, coupons, orders] = await Promise.all([
      api.get('/admin/dishes'),
      api.get('/admin/categories'),
      api.get('/admin/coupons'),
      api.get('/admin/orders'),
    ])
    stats.value = {
      dishes: dishes.data.length,
      categories: categories.data.length,
      coupons: coupons.data.filter((c) => c.is_active).length,
      orders: orders.data.length,
    }
  } catch {
    // stats stay at 0
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div>
    <div class="page-header">
      <h1>Dashboard</h1>
    </div>

    <div v-if="loading" class="card">Ładowanie...</div>

    <div v-else class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ stats.dishes }}</div>
        <div class="stat-label">Dania w menu</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.categories }}</div>
        <div class="stat-label">Kategorie</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ stats.coupons }}</div>
        <div class="stat-label">Aktywne kupony</div>
      </div>
    </div>

    <div class="card">
      <h3 style="margin-bottom: 0.75rem">Szybkie linki</h3>
      <div style="display: flex; gap: 0.5rem; flex-wrap: wrap">
        <RouterLink to="/dishes" class="btn btn-primary">Zarządzaj daniami</RouterLink>
        <RouterLink to="/orders" class="btn btn-secondary">Zamówienia</RouterLink>
        <RouterLink to="/coupons" class="btn btn-secondary">Kupony</RouterLink>
        <RouterLink to="/settings" class="btn btn-secondary">Ustawienia</RouterLink>
      </div>
    </div>
  </div>
</template>
