import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref, computed } from 'vue'
import { NavBarPage } from './pages/NavBarPage'

// Reactive mock state
const mockUserRef = ref(null)
const mockIsAuthenticated = computed(() => !!mockUserRef.value)

vi.mock('@/composables/useAuth', () => ({
  useAuth: () => ({
    user: mockUserRef,
    isAuthenticated: mockIsAuthenticated,
    logout: vi.fn(() => {
      mockUserRef.value = null
    }),
  }),
}))

vi.mock('@/composables/useCart', () => ({
  useCart: () => ({
    itemCount: ref(0),
  }),
}))

describe('NavBar', () => {
  beforeEach(() => {
    mockUserRef.value = null
  })

  it('shows "Zaloguj się" link when not authenticated', async () => {
    const page = await NavBarPage.mount()

    expect(page.hasAuthLink()).toBe(true)
    expect(page.authLinkText()).toBe('Zaloguj się')
    expect(page.hasUserButton()).toBe(false)
  })

  it('shows user icon button when authenticated', async () => {
    mockUserRef.value = { first_name: 'Jan', role: 'user' }

    const page = await NavBarPage.mount()

    expect(page.hasAuthLink()).toBe(false)
    expect(page.hasUserButton()).toBe(true)
  })

  it('toggles user dropdown on click', async () => {
    mockUserRef.value = { first_name: 'Jan', role: 'user' }

    const page = await NavBarPage.mount()

    expect(page.hasUserDropdown()).toBe(false)
    await page.clickUserButton()
    expect(page.hasUserDropdown()).toBe(true)
    expect(page.userDropdownName()).toBe('Jan')
  })

  it('shows logo with correct text', async () => {
    const page = await NavBarPage.mount()

    expect(page.logoText()).toContain('Szamma')
    expect(page.logoText()).toContain('Mia')
  })

  it('shows Menu and Dojazd navigation links', async () => {
    const page = await NavBarPage.mount()

    expect(page.navLinkTexts()).toContain('Menu')
    expect(page.navLinkTexts()).toContain('Dojazd')
  })

  it('shows "Zamów Teraz" button', async () => {
    const page = await NavBarPage.mount()

    expect(page.orderButtonText()).toBe('Zamów Teraz')
  })
})
