import { describe, it, expect, vi, beforeEach } from 'vitest'
import { RegisterPage } from './pages/RegisterPage'

const mockRegister = vi.fn()
const mockIsAuthenticated = { value: false }

vi.mock('@/composables/useAuth', () => ({
  useAuth: () => ({
    register: mockRegister,
    isAuthenticated: mockIsAuthenticated,
  }),
}))

describe('RegisterView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockIsAuthenticated.value = false
  })

  it('renders registration form with all fields', async () => {
    const page = await RegisterPage.mount()

    expect(page.title()).toBe('Zarejestruj się')
    expect(page.inputCount()).toBe(5)
    expect(page.submitButtonText()).toBe('Zarejestruj się')
  })

  it('shows link to login page', async () => {
    const page = await RegisterPage.mount()

    expect(page.altLinkText()).toBe('Zaloguj się')
    expect(page.altLinkHref()).toBe('/login')
  })

  it('shows error when passwords do not match', async () => {
    const page = await RegisterPage.mount()

    await page.fillAndSubmit({
      firstName: 'Jan',
      email: 'jan@test.pl',
      phone: '123456789',
      password: 'password1',
      passwordConfirm: 'password2',
    })

    expect(page.errorText()).toBe('Hasła nie są takie same')
    expect(mockRegister).not.toHaveBeenCalled()
  })

  it('shows error when password too short', async () => {
    const page = await RegisterPage.mount()

    await page.fillAndSubmit({
      firstName: 'Jan',
      email: 'jan@test.pl',
      phone: '123456789',
      password: '12345',
      passwordConfirm: '12345',
    })

    expect(page.errorText()).toBe('Hasło musi mieć minimum 6 znaków')
    expect(mockRegister).not.toHaveBeenCalled()
  })

  it('calls register with correct data on valid submit', async () => {
    mockRegister.mockResolvedValue(undefined)
    const page = await RegisterPage.mount()

    await page.fillAndSubmit({
      firstName: 'Jan',
      email: 'jan@test.pl',
      phone: '123456789',
      password: 'secret123',
      passwordConfirm: 'secret123',
    })

    expect(mockRegister).toHaveBeenCalledWith({
      email: 'jan@test.pl',
      first_name: 'Jan',
      phone: '123456789',
      password: 'secret123',
    })
  })

  it('shows server error on register failure', async () => {
    mockRegister.mockRejectedValue({
      response: { data: { detail: 'Email jest już zarejestrowany' } },
    })
    const page = await RegisterPage.mount()

    await page.fillAndSubmit({
      firstName: 'Jan',
      email: 'existing@test.pl',
      phone: '123456789',
      password: 'secret123',
      passwordConfirm: 'secret123',
    })

    expect(page.errorText()).toBe('Email jest już zarejestrowany')
  })
})
