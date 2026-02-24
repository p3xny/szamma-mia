<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api.js'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await api.post('/auth/login', {
      email: email.value,
      password: password.value,
    })
    localStorage.setItem('admin_token', data.access_token)

    const { data: user } = await api.get('/auth/me')
    if (user.role !== 'admin') {
      localStorage.removeItem('admin_token')
      error.value = 'Brak uprawnień administratora'
      return
    }

    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Błąd logowania'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-brand">Szamma <span>Mia</span></h1>
      <p class="login-subtitle">Panel administracyjny</p>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            class="form-control"
            required
            autocomplete="email"
          />
        </div>
        <div class="form-group">
          <label for="password">Hasło</label>
          <input
            id="password"
            v-model="password"
            type="password"
            class="form-control"
            required
            autocomplete="current-password"
          />
        </div>
        <button type="submit" class="btn btn-primary login-btn" :disabled="loading">
          {{ loading ? 'Logowanie...' : 'Zaloguj się' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--light-gray);
}

.login-card {
  background: var(--white);
  border-radius: 10px;
  padding: 2.5rem;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.login-brand {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--green);
  text-align: center;
}

.login-brand span {
  color: var(--red);
}

.login-subtitle {
  text-align: center;
  color: #999;
  font-size: 0.85rem;
  margin-bottom: 1.5rem;
}

.login-btn {
  width: 100%;
  padding: 0.65rem;
  font-size: 0.95rem;
  margin-top: 0.5rem;
}
</style>
