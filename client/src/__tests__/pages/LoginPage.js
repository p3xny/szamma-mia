import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'

export class LoginPage {
  static SELECTORS = {
    title: '.auth-title',
    emailInput: 'input[type="email"]',
    passwordInput: 'input[type="password"]',
    form: 'form',
    submitButton: '.auth-submit',
    error: '.auth-error',
    altLink: '.auth-link a',
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
        { path: '/login', component: LoginView },
        { path: '/register', component: { template: '<div />' } },
        { path: '/account', component: { template: '<div />' } },
      ],
    })
    await router.push('/login')
    await router.isReady()

    const wrapper = mount(LoginView, { global: { plugins: [router] } })
    return new LoginPage(wrapper, router)
  }

  // --- Queries ---

  title() {
    return this.wrapper.find(LoginPage.SELECTORS.title).text()
  }

  hasEmailInput() {
    return this.wrapper.find(LoginPage.SELECTORS.emailInput).exists()
  }

  hasPasswordInput() {
    return this.wrapper.find(LoginPage.SELECTORS.passwordInput).exists()
  }

  submitButtonText() {
    return this.wrapper.find(LoginPage.SELECTORS.submitButton).text()
  }

  errorText() {
    const el = this.wrapper.find(LoginPage.SELECTORS.error)
    return el.exists() ? el.text() : null
  }

  altLinkText() {
    return this.wrapper.find(LoginPage.SELECTORS.altLink).text()
  }

  altLinkHref() {
    return this.wrapper.find(LoginPage.SELECTORS.altLink).attributes('href')
  }

  // --- Actions ---

  async fillEmail(value) {
    await this.wrapper.find(LoginPage.SELECTORS.emailInput).setValue(value)
  }

  async fillPassword(value) {
    await this.wrapper.find(LoginPage.SELECTORS.passwordInput).setValue(value)
  }

  async submit() {
    await this.wrapper.find(LoginPage.SELECTORS.form).trigger('submit')
    await flushPromises()
  }

  async fillAndSubmit(email, password) {
    await this.fillEmail(email)
    await this.fillPassword(password)
    await this.submit()
  }
}
