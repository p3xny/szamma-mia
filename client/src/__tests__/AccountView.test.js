import { describe, it, expect, vi, beforeEach } from 'vitest'
import { AccountPage } from './pages/AccountPage'

const mockUser = { value: null }
const mockIsAuthenticated = { value: false }
const mockUpdateProfile = vi.fn()
const mockGetAddresses = vi.fn()
const mockCreateAddress = vi.fn()
const mockDeleteAddress = vi.fn()
const mockLogout = vi.fn()

vi.mock('@/composables/useAuth', () => ({
  useAuth: () => ({
    user: mockUser,
    isAuthenticated: mockIsAuthenticated,
    logout: mockLogout,
    updateProfile: mockUpdateProfile,
    getAddresses: mockGetAddresses,
    createAddress: mockCreateAddress,
    updateAddress: vi.fn(),
    deleteAddress: mockDeleteAddress,
  }),
}))

describe('AccountView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockGetAddresses.mockResolvedValue([])
  })

  it('redirects to /login when not authenticated', async () => {
    mockIsAuthenticated.value = false
    mockUser.value = null

    const page = await AccountPage.mount()

    expect(page.currentPath()).toBe('/login')
  })

  it('renders account page when authenticated', async () => {
    mockIsAuthenticated.value = true
    mockUser.value = { id: 1, first_name: 'Jan', email: 'jan@test.pl', phone: '123', role: 'user' }

    const page = await AccountPage.mount()

    expect(page.title()).toBe('Moje konto')
    expect(page.firstSectionTitle()).toBe('Dane osobowe')
  })

  it('initializes profile form with user data', async () => {
    mockIsAuthenticated.value = true
    mockUser.value = { id: 1, first_name: 'Jan', email: 'jan@test.pl', phone: '555', role: 'user' }

    const page = await AccountPage.mount()

    expect(page.profileFieldValue('firstName')).toBe('Jan')
    expect(page.profileFieldValue('email')).toBe('jan@test.pl')
    expect(page.profileFieldValue('phone')).toBe('555')
  })

  it('calls updateProfile on save', async () => {
    mockIsAuthenticated.value = true
    mockUser.value = { id: 1, first_name: 'Jan', email: 'j@t.pl', phone: '1', role: 'user' }
    mockUpdateProfile.mockResolvedValue(undefined)

    const page = await AccountPage.mount()

    await page.setProfileField('firstName', 'Janek')
    await page.clickSave()

    expect(mockUpdateProfile).toHaveBeenCalledWith({
      first_name: 'Janek',
      email: 'j@t.pl',
      phone: '1',
    })
  })

  it('shows empty addresses message', async () => {
    mockIsAuthenticated.value = true
    mockUser.value = { id: 1, first_name: 'J', email: 'j@t.pl', phone: '1', role: 'user' }

    const page = await AccountPage.mount()

    expect(page.emptyAddressesText()).toBe('Brak zapisanych adresów')
  })

  it('renders saved addresses from API', async () => {
    mockIsAuthenticated.value = true
    mockUser.value = { id: 1, first_name: 'J', email: 'j@t.pl', phone: '1', role: 'user' }
    mockGetAddresses.mockResolvedValue([
      { id: 1, label: 'Dom', city: 'Piaseczno', street: 'Kwiatowa', house_number: '5', apartment: null },
      { id: 2, label: null, city: 'Warszawa', street: 'Marszałkowska', house_number: '10', apartment: '3' },
    ])

    const page = await AccountPage.mount()

    expect(page.addressCardCount()).toBe(2)
    expect(page.addressCardText(0)).toContain('Kwiatowa')
    expect(page.addressCardText(0)).toContain('Dom')
  })

  it('shows add address form on button click', async () => {
    mockIsAuthenticated.value = true
    mockUser.value = { id: 1, first_name: 'J', email: 'j@t.pl', phone: '1', role: 'user' }

    const page = await AccountPage.mount()

    await page.clickAddAddress()
    expect(page.hasAddressForm()).toBe(true)
  })

  it('shows logout button', async () => {
    mockIsAuthenticated.value = true
    mockUser.value = { id: 1, first_name: 'J', email: 'j@t.pl', phone: '1', role: 'user' }

    const page = await AccountPage.mount()

    expect(page.logoutButtonText()).toBe('Wyloguj się')
  })

  it('calls logout on logout click', async () => {
    mockIsAuthenticated.value = true
    mockUser.value = { id: 1, first_name: 'J', email: 'j@t.pl', phone: '1', role: 'user' }

    const page = await AccountPage.mount()

    await page.clickLogout()

    expect(mockLogout).toHaveBeenCalled()
  })
})
