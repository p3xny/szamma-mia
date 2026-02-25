import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/cart-summary',
      name: 'cart-summary',
      component: () => import('@/views/CartSummaryView.vue'),
    },
    {
      path: '/order-summary',
      name: 'order-summary',
      component: () => import('@/views/OrderSummaryView.vue'),
    },
    {
      path: '/order-confirmation/:id',
      name: 'order-confirmation',
      component: () => import('@/views/OrderConfirmationView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
    },
    {
      path: '/account',
      name: 'account',
      component: () => import('@/views/AccountView.vue'),
    },
    {
      path: '/reservation',
      name: 'reservation',
      component: () => import('@/views/ReservationView.vue'),
    },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) {
      // Cross-route: page has just rendered but images may not have loaded yet,
      // causing layout shifts that would put the scroll position at the wrong spot.
      // Wait for the layout to stabilize before scrolling.
      if (from.name && from.path !== to.path) {
        return new Promise(resolve => {
          setTimeout(() => {
            resolve({ el: to.hash, top: +32, behavior: 'smooth' })
          }, 400)
        })
      }
      // Same-route hash push (rare, NavBar handles this via scrollIntoView directly)
      return { el: to.hash, top: +32, behavior: 'smooth' }
    }
    return { top: 0 }
  },
})

export default router
