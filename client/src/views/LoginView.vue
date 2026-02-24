<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { login, isAuthenticated } = useAuth()

if (isAuthenticated.value) {
  router.push('/account')
}

const email = ref('')
const password = ref('')
const error = ref('')
const submitting = ref(false)

async function handleLogin() {
  if (submitting.value) return
  error.value = ''
  submitting.value = true
  try {
    await login({ email: email.value, password: password.value })
    router.push('/account')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Nie udało się zalogować'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="auth-page">
    <div class="auth-card">
      <h1 class="auth-title">Zaloguj się</h1>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="auth-field">
          <label>Email</label>
          <input v-model="email" type="email" required autocomplete="email">
        </div>

        <div class="auth-field">
          <label>Hasło</label>
          <input v-model="password" type="password" required autocomplete="current-password">
        </div>

        <p v-if="error" class="auth-error">{{ error }}</p>

        <button type="submit" class="auth-submit" :disabled="submitting">
          {{ submitting ? 'Logowanie...' : 'Zaloguj się' }}
        </button>
      </form>

      <p class="auth-link">
        Nie masz konta?
        <router-link to="/register">Zarejestruj się</router-link>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--light-gray);
  padding: 2rem 1rem;
}

.auth-card {
  background: var(--white);
  border-radius: 12px;
  padding: 2.5rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.auth-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--dark);
  text-align: center;
  margin-bottom: 1.5rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.auth-field {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.auth-field label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
}

.auth-field input {
  padding: 0.7rem 0.75rem;
  border: 1.5px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
}

.auth-field input:focus {
  border-color: var(--green);
}

.auth-error {
  color: var(--red);
  font-size: 0.85rem;
  font-weight: 600;
  text-align: center;
}

.auth-submit {
  background: var(--green);
  color: var(--white);
  border: none;
  padding: 0.8rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 700;
  cursor: pointer;
  transition: background 0.3s;
  margin-top: 0.5rem;
}

.auth-submit:hover:not(:disabled) {
  background: #007a3a;
}

.auth-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.auth-link {
  text-align: center;
  margin-top: 1.25rem;
  font-size: 0.9rem;
  color: #555;
}

.auth-link a {
  color: var(--green);
  font-weight: 600;
  text-decoration: none;
}

.auth-link a:hover {
  text-decoration: underline;
}
</style>
