import { createRouter, createWebHistory } from 'vue-router'
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import DishesView from './views/DishesView.vue'
import DishEditView from './views/DishEditView.vue'
import CategoriesView from './views/CategoriesView.vue'
import CouponsView from './views/CouponsView.vue'
import ReservationsView from './views/ReservationsView.vue'
import OrdersView from './views/OrdersView.vue'
import EventBannersView from './views/EventBannersView.vue'
import SettingsView from './views/SettingsView.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
  { path: '/', name: 'dashboard', component: DashboardView },
  { path: '/dishes', name: 'dishes', component: DishesView },
  { path: '/dishes/:id', name: 'dish-edit', component: DishEditView, props: true },
  { path: '/categories', name: 'categories', component: CategoriesView },
  { path: '/coupons', name: 'coupons', component: CouponsView },
  { path: '/reservations', name: 'reservations', component: ReservationsView },
  { path: '/orders', name: 'orders', component: OrdersView },
  { path: '/event-banners', name: 'event-banners', component: EventBannersView },
  { path: '/settings', name: 'settings', component: SettingsView },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  if (to.meta.public) return true
  const token = localStorage.getItem('admin_token')
  if (!token) return { name: 'login' }
  return true
})

export default router
