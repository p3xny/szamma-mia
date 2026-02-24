import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import AccountView from '@/views/AccountView.vue'

export class AccountPage {
  static SELECTORS = {
    page: '.acc-page',
    title: '.acc-title',
    sectionTitle: '.acc-section-title',
    profileInputs: '.acc-field input',
    saveButton: '.btn-save',
    profileMessage: '.acc-msg',
    emptyAddresses: '.acc-empty',
    addressCards: '.addr-card',
    addAddressButton: '.btn-add-addr',
    addressForm: '.addr-form',
    logoutButton: '.btn-logout',
  }

  // Profile input indices
  static PROFILE_FIELDS = {
    firstName: 0,
    email: 1,
    phone: 2,
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
        { path: '/account', component: AccountView },
      ],
    })
    await router.push('/account')
    await router.isReady()

    const wrapper = mount(AccountView, { global: { plugins: [router] } })
    await flushPromises()
    return new AccountPage(wrapper, router)
  }

  // --- Queries ---

  currentPath() {
    return this.router.currentRoute.value.path
  }

  title() {
    const el = this.wrapper.find(AccountPage.SELECTORS.title)
    return el.exists() ? el.text() : null
  }

  firstSectionTitle() {
    const el = this.wrapper.find(AccountPage.SELECTORS.sectionTitle)
    return el.exists() ? el.text() : null
  }

  profileFieldValue(fieldName) {
    const inputs = this.wrapper.findAll(AccountPage.SELECTORS.profileInputs)
    return inputs[AccountPage.PROFILE_FIELDS[fieldName]].element.value
  }

  emptyAddressesText() {
    const el = this.wrapper.find(AccountPage.SELECTORS.emptyAddresses)
    return el.exists() ? el.text() : null
  }

  addressCardCount() {
    return this.wrapper.findAll(AccountPage.SELECTORS.addressCards).length
  }

  addressCardText(index) {
    return this.wrapper.findAll(AccountPage.SELECTORS.addressCards)[index].text()
  }

  hasAddressForm() {
    return this.wrapper.find(AccountPage.SELECTORS.addressForm).exists()
  }

  logoutButtonText() {
    const el = this.wrapper.find(AccountPage.SELECTORS.logoutButton)
    return el.exists() ? el.text() : null
  }

  // --- Actions ---

  async setProfileField(fieldName, value) {
    const inputs = this.wrapper.findAll(AccountPage.SELECTORS.profileInputs)
    await inputs[AccountPage.PROFILE_FIELDS[fieldName]].setValue(value)
  }

  async clickSave() {
    await this.wrapper.find(AccountPage.SELECTORS.saveButton).trigger('click')
    await flushPromises()
  }

  async clickAddAddress() {
    await this.wrapper.find(AccountPage.SELECTORS.addAddressButton).trigger('click')
  }

  async clickLogout() {
    await this.wrapper.find(AccountPage.SELECTORS.logoutButton).trigger('click')
    await flushPromises()
  }
}
