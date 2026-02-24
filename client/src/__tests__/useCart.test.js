import { describe, it, expect, beforeEach } from 'vitest'
import { useCart } from '@/composables/useCart'

describe('useCart', () => {
  beforeEach(() => {
    const { clearCart } = useCart()
    clearCart()
  })

  it('starts with empty cart', () => {
    const { items, itemCount, totalPrice } = useCart()
    expect(items.value).toEqual([])
    expect(itemCount.value).toBe(0)
    expect(totalPrice.value).toBe(0)
  })

  it('adds an item', () => {
    const { addItem, items, itemCount } = useCart()
    addItem({ id: 1, name: 'Pizza', image: null, price: 30 }, [], [], 1)
    expect(items.value.length).toBe(1)
    expect(items.value[0].name).toBe('Pizza')
    expect(itemCount.value).toBe(1)
  })

  it('calculates total price', () => {
    const { addItem, totalPrice } = useCart()
    addItem({ id: 1, name: 'Pizza', image: null, price: 30 }, [], [], 2)
    expect(totalPrice.value).toBe(60)
  })

  it('removes an item', () => {
    const { addItem, removeItem, items } = useCart()
    addItem({ id: 1, name: 'Pizza', image: null, price: 30 }, [], [], 1)
    const cartId = items.value[0].cartId
    removeItem(cartId)
    expect(items.value.length).toBe(0)
  })

  it('updates quantity', () => {
    const { addItem, updateQuantity, items, totalPrice } = useCart()
    addItem({ id: 1, name: 'Pizza', image: null, price: 30 }, [], [], 1)
    const cartId = items.value[0].cartId
    updateQuantity(cartId, 3)
    expect(items.value[0].quantity).toBe(3)
    expect(totalPrice.value).toBe(90)
  })

  it('removes item when quantity set to 0', () => {
    const { addItem, updateQuantity, items } = useCart()
    addItem({ id: 1, name: 'Pizza', image: null, price: 30 }, [], [], 1)
    const cartId = items.value[0].cartId
    updateQuantity(cartId, 0)
    expect(items.value.length).toBe(0)
  })

  it('clears cart', () => {
    const { addItem, clearCart, items } = useCart()
    addItem({ id: 1, name: 'A', image: null, price: 10 }, [], [], 1)
    addItem({ id: 2, name: 'B', image: null, price: 20 }, [], [], 1)
    expect(items.value.length).toBe(2)
    clearCart()
    expect(items.value.length).toBe(0)
  })

  it('calculates price with extras', () => {
    const { addItem, totalPrice } = useCart()
    const extras = [
      { name: 'Cheese', price: 5, selected: true },
      { name: 'Bacon', price: 3, selected: false },
    ]
    addItem({ id: 1, name: 'Pizza', image: null, price: 30 }, [], extras, 1)
    expect(totalPrice.value).toBe(35) // 30 + 5 (only selected)
  })

  it('calculates price with paid ingredients', () => {
    const { addItem, totalPrice } = useCart()
    const ingredients = [
      { name: 'Ser', included: true, price: 3 },
      { name: 'Szynka', included: false, price: 5 },
    ]
    addItem({ id: 1, name: 'Pizza', image: null, price: 30 }, ingredients, [], 1)
    expect(totalPrice.value).toBe(33) // 30 + 3 (only included)
  })

  it('meetsMinimum computed works', () => {
    const { addItem, meetsMinimum } = useCart()
    addItem({ id: 1, name: 'Pizza', image: null, price: 30 }, [], [], 1)
    expect(meetsMinimum.value).toBe(false) // 30 < 50
    addItem({ id: 2, name: 'Pasta', image: null, price: 25 }, [], [], 1)
    expect(meetsMinimum.value).toBe(true) // 55 >= 50
  })

  it('shares state across multiple useCart() calls', () => {
    const cart1 = useCart()
    const cart2 = useCart()
    cart1.addItem({ id: 1, name: 'Pizza', image: null, price: 30 }, [], [], 1)
    expect(cart2.items.value.length).toBe(1)
  })
})
