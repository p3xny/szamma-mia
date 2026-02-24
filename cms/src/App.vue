<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import AdminSidebar from './components/AdminSidebar.vue'

const route = useRoute()
const isLoginPage = computed(() => route.name === 'login')
</script>

<template>
  <div v-if="isLoginPage">
    <RouterView />
  </div>
  <div v-else class="admin-layout">
    <AdminSidebar />
    <main class="admin-main">
      <RouterView />
    </main>
  </div>
</template>
