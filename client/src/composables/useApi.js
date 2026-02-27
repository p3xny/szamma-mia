import axios from 'axios'

export const api = axios.create({
  baseURL: '/api',
})

export async function createOrder(data) {
  const res = await api.post('/orders', data)
  return res.data
}

export async function getOrder(id) {
  const res = await api.get(`/orders/${id}`)
  return res.data
}

export async function validateCoupon(code) {
  const res = await api.post('/coupons/validate', { code })
  return res.data
}

export async function getSlotOccupancy(dateStr) {
  const res = await api.get('/order-slots', { params: { date_str: dateStr } })
  return res.data
}

export async function initiateAutopay(orderId) {
  const res = await api.post(`/payments/autopay/initiate/${orderId}`)
  return res.data
}
