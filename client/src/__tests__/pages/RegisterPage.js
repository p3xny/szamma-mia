import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import RegisterView from '@/views/RegisterView.vue'

export class RegisterPage {
  static SELECTORS = {
    title: '.auth-title',
    inputs: 'input',
    form: 'form',
    submitButton: '.auth-submit',
    error: '.auth-error',
    altLink: '.auth-link a',
  }

  // Input indices in the form
  static FIELDS = {
    firstName: 0,
    email: 1,
    phone: 2,
    password: 3,
    passwordConfirm: 4,
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
        { path: '/register', component: RegisterView },
        { path: '/account', component: { template: '<div />' } },
      ],
    })
    await router.push('/register')
    await router.isReady()

    const wrapper = mount(RegisterView, { global: { plugins: [router] } })
    return new RegisterPage(wrapper, router)
  }

  // --- Queries ---

  title() {
    return this.wrapper.find(RegisterPage.SELECTORS.title).text()
  }

  inputCount() {
    return this.wrapper.findAll(RegisterPage.SELECTORS.inputs).length
  }

  submitButtonText() {
    return this.wrapper.find(RegisterPage.SELECTORS.submitButton).text()
  }

  errorText() {
    const el = this.wrapper.find(RegisterPage.SELECTORS.error)
    return el.exists() ? el.text() : null
  }

  altLinkText() {
    return this.wrapper.find(RegisterPage.SELECTORS.altLink).text()
  }

  altLinkHref() {
    return this.wrapper.find(RegisterPage.SELECTORS.altLink).attributes('href')
  }

  // --- Actions ---

  async fillField(fieldName, value) {
    const inputs = this.wrapper.findAll(RegisterPage.SELECTORS.inputs)
    await inputs[RegisterPage.FIELDS[fieldName]].setValue(value)
  }

  async fillAll({ firstName, email, phone, password, passwordConfirm }) {
    await this.fillField('firstName', firstName)
    await this.fillField('email', email)
    await this.fillField('phone', phone)
    await this.fillField('password', password)
    await this.fillField('passwordConfirm', passwordConfirm)
  }

  async submit() {
    await this.wrapper.find(RegisterPage.SELECTORS.form).trigger('submit')
    await flushPromises()
  }

  async fillAndSubmit(data) {
    await this.fillAll(data)
    await this.submit()
  }
}
