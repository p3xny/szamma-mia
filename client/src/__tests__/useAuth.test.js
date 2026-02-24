import { describe, it, expect, vi, beforeEach } from 'vitest'

// Mock localStorage
const storage = {}
vi.stubGlobal('localStorage', {
  getItem: vi.fn((key) => storage[key] ?? null),
  setItem: vi.fn((key, val) => { storage[key] = val }),
  removeItem: vi.fn((key) => { delete storage[key] }),
})

// Create mock api object
const mockApi = {
  get: vi.fn(),
  post: vi.fn(),
  patch: vi.fn(),
  delete: vi.fn(),
  defaults: { headers: { common: {} } },
}

vi.mock('@/composables/useApi', () => ({
  api: mockApi,
}))

const { useAuth } = await import('@/composables/useAuth')

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    const auth = useAuth()
    auth.logout()
    Object.keys(storage).forEach((k) => delete storage[k])
  })

  it('starts with null user and not authenticated', () => {
    const { user, isAuthenticated } = useAuth()
    expect(user.value).toBeNull()
    expect(isAuthenticated.value).toBe(false)
  })

  it('isAdmin is false when not authenticated', () => {
    const { isAdmin } = useAuth()
    expect(isAdmin.value).toBe(false)
  })

  describe('register', () => {
    it('sets token, fetches user, and marks authenticated', async () => {
      mockApi.post.mockResolvedValueOnce({
        data: { access_token: 'test-token', token_type: 'bearer' },
      })
      mockApi.get.mockResolvedValueOnce({
        data: { id: 1, email: 'a@b.pl', first_name: 'Jan', phone: '123', role: 'user' },
      })

      const { register, user, isAuthenticated } = useAuth()
      await register({ email: 'a@b.pl', first_name: 'Jan', phone: '123', password: 'secret' })

      expect(mockApi.post).toHaveBeenCalledWith('/auth/register', {
        email: 'a@b.pl', first_name: 'Jan', phone: '123', password: 'secret',
      })
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'test-token')
      expect(user.value).toEqual({
        id: 1, email: 'a@b.pl', first_name: 'Jan', phone: '123', role: 'user',
      })
      expect(isAuthenticated.value).toBe(true)
    })
  })

  describe('login', () => {
    it('sets token and fetches user', async () => {
      mockApi.post.mockResolvedValueOnce({
        data: { access_token: 'login-token', token_type: 'bearer' },
      })
      mockApi.get.mockResolvedValueOnce({
        data: { id: 2, email: 'x@y.pl', first_name: 'Ewa', phone: '456', role: 'user' },
      })

      const { login, user } = useAuth()
      await login({ email: 'x@y.pl', password: 'pass' })

      expect(mockApi.post).toHaveBeenCalledWith('/auth/login', {
        email: 'x@y.pl', password: 'pass',
      })
      expect(user.value.email).toBe('x@y.pl')
    })
  })

  describe('logout', () => {
    it('clears user and token', async () => {
      mockApi.post.mockResolvedValueOnce({ data: { access_token: 'tok' } })
      mockApi.get.mockResolvedValueOnce({
        data: { id: 1, email: 'a@b.pl', first_name: 'J', phone: '1', role: 'user' },
      })

      const { login, logout, user, isAuthenticated, token } = useAuth()
      await login({ email: 'a@b.pl', password: 'p' })
      expect(isAuthenticated.value).toBe(true)

      logout()
      expect(user.value).toBeNull()
      expect(token.value).toBeNull()
      expect(isAuthenticated.value).toBe(false)
      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token')
    })
  })

  describe('fetchUser', () => {
    it('does nothing when no token', async () => {
      const { fetchUser } = useAuth()
      await fetchUser()
      expect(mockApi.get).not.toHaveBeenCalled()
    })

    it('clears state on API error', async () => {
      mockApi.post.mockResolvedValueOnce({ data: { access_token: 'bad' } })
      mockApi.get.mockRejectedValueOnce(new Error('nope'))

      const { login, user, token } = useAuth()
      try { await login({ email: 'a@b.pl', password: 'p' }) } catch {}

      expect(user.value).toBeNull()
      expect(token.value).toBeNull()
    })
  })

  describe('updateProfile', () => {
    it('updates the user ref', async () => {
      mockApi.post.mockResolvedValueOnce({ data: { access_token: 'tok' } })
      mockApi.get.mockResolvedValueOnce({
        data: { id: 1, email: 'a@b.pl', first_name: 'Jan', phone: '1', role: 'user' },
      })

      const { login, updateProfile, user } = useAuth()
      await login({ email: 'a@b.pl', password: 'p' })

      mockApi.patch.mockResolvedValueOnce({
        data: { id: 1, email: 'a@b.pl', first_name: 'Janek', phone: '999', role: 'user' },
      })
      await updateProfile({ first_name: 'Janek', phone: '999' })

      expect(user.value.first_name).toBe('Janek')
      expect(mockApi.patch).toHaveBeenCalledWith('/auth/me', { first_name: 'Janek', phone: '999' })
    })
  })

  describe('address helpers', () => {
    it('getAddresses calls GET /auth/addresses', async () => {
      mockApi.get.mockResolvedValueOnce({ data: [{ id: 1, city: 'Waw' }] })

      const { getAddresses } = useAuth()
      const result = await getAddresses()
      expect(result).toEqual([{ id: 1, city: 'Waw' }])
    })

    it('createAddress calls POST /auth/addresses', async () => {
      const addrData = { city: 'Piaseczno', street: 'ul. X', house_number: '1' }
      mockApi.post.mockResolvedValueOnce({ data: { id: 5, ...addrData } })

      const { createAddress } = useAuth()
      const result = await createAddress(addrData)
      expect(result.id).toBe(5)
      expect(mockApi.post).toHaveBeenCalledWith('/auth/addresses', addrData)
    })

    it('deleteAddress calls DELETE /auth/addresses/:id', async () => {
      mockApi.delete.mockResolvedValueOnce({})

      const { deleteAddress } = useAuth()
      await deleteAddress(7)
      expect(mockApi.delete).toHaveBeenCalledWith('/auth/addresses/7')
    })
  })

  describe('isAdmin', () => {
    it('returns true when user role is admin', async () => {
      mockApi.post.mockResolvedValueOnce({ data: { access_token: 'tok' } })
      mockApi.get.mockResolvedValueOnce({
        data: { id: 1, email: 'admin@test.pl', first_name: 'A', phone: '0', role: 'admin' },
      })

      const { login, isAdmin } = useAuth()
      await login({ email: 'admin@test.pl', password: 'p' })
      expect(isAdmin.value).toBe(true)
    })
  })
})
