import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import NavBar from '@/components/NavBar.vue'

export class NavBarPage {
  static SELECTORS = {
    logo: '.logo',
    navLinks: '.nav-links a',
    authLink: '.nav-auth-link',
    userButton: '.btn-user',
    userDropdown: '.user-dropdown',
    userDropdownName: '.user-dropdown-name',
    cartButton: '.btn-cart',
    cartDot: '.cart-dot',
    orderButton: '.btn-order',
  }

  constructor(wrapper, router) {
    this.wrapper = wrapper
    this.router = router
  }

  static async mount() {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', component: { template: '<div />' } },
        { path: '/login', component: { template: '<div />' } },
        { path: '/account', component: { template: '<div />' } },
        { path: '/cart-summary', component: { template: '<div />' } },
      ],
    })
    await router.push('/')
    await router.isReady()

    const wrapper = mount(NavBar, { global: { plugins: [router] } })
    return new NavBarPage(wrapper, router)
  }

  // --- Queries ---

  logoText() {
    return this.wrapper.find(NavBarPage.SELECTORS.logo).text()
  }

  navLinkTexts() {
    return this.wrapper.findAll(NavBarPage.SELECTORS.navLinks).map(l => l.text())
  }

  hasAuthLink() {
    return this.wrapper.find(NavBarPage.SELECTORS.authLink).exists()
  }

  authLinkText() {
    return this.wrapper.find(NavBarPage.SELECTORS.authLink).text()
  }

  hasUserButton() {
    return this.wrapper.find(NavBarPage.SELECTORS.userButton).exists()
  }

  hasUserDropdown() {
    return this.wrapper.find(NavBarPage.SELECTORS.userDropdown).exists()
  }

  userDropdownName() {
    return this.wrapper.find(NavBarPage.SELECTORS.userDropdownName).text()
  }

  orderButtonText() {
    return this.wrapper.find(NavBarPage.SELECTORS.orderButton).text()
  }

  // --- Actions ---

  async clickUserButton() {
    await this.wrapper.find(NavBarPage.SELECTORS.userButton).trigger('click')
  }
}
