import { ref, computed } from 'vue'
import { api } from './useApi'

const user = ref(null)
const token = ref(localStorage.getItem('auth_token'))
const loading = ref(false)

// Set axios header if token exists on load
if (token.value) {
  api.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
}

function setToken(newToken) {
  token.value = newToken
  if (newToken) {
    localStorage.setItem('auth_token', newToken)
    api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
  } else {
    localStorage.removeItem('auth_token')
    delete api.defaults.headers.common['Authorization']
  }
}

export function useAuth() {
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.role === 'admin')

  async function fetchUser() {
    if (!token.value) return
    loading.value = true
    try {
      const res = await api.get('/auth/me')
      user.value = res.data
    } catch {
      setToken(null)
      user.value = null
    } finally {
      loading.value = false
    }
  }

  async function register({ email, first_name, phone, password }) {
    const res = await api.post('/auth/register', { email, first_name, phone, password })
    setToken(res.data.access_token)
    await fetchUser()
  }

  async function login({ email, password }) {
    const res = await api.post('/auth/login', { email, password })
    setToken(res.data.access_token)
    await fetchUser()
  }

  function logout() {
    setToken(null)
    user.value = null
  }

  async function updateProfile(data) {
    const res = await api.patch('/auth/me', data)
    user.value = res.data
  }

  // Address helpers
  async function getAddresses() {
    const res = await api.get('/auth/addresses')
    return res.data
  }

  async function createAddress(data) {
    const res = await api.post('/auth/addresses', data)
    return res.data
  }

  async function updateAddress(id, data) {
    const res = await api.patch(`/auth/addresses/${id}`, data)
    return res.data
  }

  async function deleteAddress(id) {
    await api.delete(`/auth/addresses/${id}`)
  }

  return {
    user,
    token,
    loading,
    isAuthenticated,
    isAdmin,
    fetchUser,
    register,
    login,
    logout,
    updateProfile,
    getAddresses,
    createAddress,
    updateAddress,
    deleteAddress,
  }
}
