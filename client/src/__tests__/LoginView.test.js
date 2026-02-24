import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import { LoginPage } from './pages/LoginPage'

const mockLogin = vi.fn()
const mockIsAuthenticated = { value: false }

vi.mock('@/composables/useAuth', () => ({
  useAuth: () => ({
    login: mockLogin,
    isAuthenticated: mockIsAuthenticated,
  }),
}))

describe('LoginView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockIsAuthenticated.value = false
  })

  it('renders login form with title', async () => {
    const page = await LoginPage.mount()

    expect(page.title()).toBe('Zaloguj się')
    expect(page.hasEmailInput()).toBe(true)
    expect(page.hasPasswordInput()).toBe(true)
    expect(page.submitButtonText()).toBe('Zaloguj się')
  })

  it('shows link to register page', async () => {
    const page = await LoginPage.mount()

    expect(page.altLinkText()).toBe('Zarejestruj się')
    expect(page.altLinkHref()).toBe('/register')
  })

  it('calls login on form submit', async () => {
    mockLogin.mockResolvedValue(undefined)
    const page = await LoginPage.mount()

    await page.fillAndSubmit('test@example.pl', 'password123')

    expect(mockLogin).toHaveBeenCalledWith({
      email: 'test@example.pl',
      password: 'password123',
    })
  })

  it('shows error message on login failure', async () => {
    mockLogin.mockRejectedValue({
      response: { data: { detail: 'Nieprawidłowy email lub hasło' } },
    })
    const page = await LoginPage.mount()

    await page.fillAndSubmit('test@example.pl', 'wrong')

    expect(page.errorText()).toBe('Nieprawidłowy email lub hasło')
  })

  it('disables button while submitting', async () => {
    let resolveLogin
    mockLogin.mockReturnValue(new Promise((r) => { resolveLogin = r }))
    const page = await LoginPage.mount()

    await page.fillEmail('t@t.pl')
    await page.fillPassword('pass')
    await page.submit()

    expect(page.submitButtonText()).toBe('Logowanie...')

    resolveLogin()
    await flushPromises()
  })
})
