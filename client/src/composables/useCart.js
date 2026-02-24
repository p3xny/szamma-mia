import { ref, computed } from 'vue'

const MIN_ORDER = 50

const items = ref([])
const editRequest = ref(null)

let nextId = 0

function calcItemTotal(item) {
  let extra = 0
  if (item.ingredients) {
    for (const ing of item.ingredients) {
      if (ing.included && ing.price) extra += ing.price
    }
  }
  if (item.extras) {
    for (const ext of item.extras) {
      if (ext.selected) extra += ext.price
    }
  }
  return (item.price + extra) * item.quantity
}

export function useCart() {
  const itemCount = computed(() =>
    items.value.reduce((sum, item) => sum + item.quantity, 0)
  )

  const totalPrice = computed(() =>
    items.value.reduce((sum, item) => sum + calcItemTotal(item), 0)
  )

  const meetsMinimum = computed(() => totalPrice.value >= MIN_ORDER)

  function addItem(dish, ingredients, extras, quantity) {
    items.value.push({
      cartId: `cart-${Date.now()}-${nextId++}`,
      dishId: dish.id,
      name: dish.name,
      image: dish.image,
      price: dish.price,
      quantity,
      ingredients: JSON.parse(JSON.stringify(ingredients || [])),
      extras: JSON.parse(JSON.stringify(extras || [])),
    })
  }

  function removeItem(cartId) {
    items.value = items.value.filter(i => i.cartId !== cartId)
  }

  function updateQuantity(cartId, newQty) {
    const item = items.value.find(i => i.cartId === cartId)
    if (!item) return
    if (newQty < 1) {
      removeItem(cartId)
    } else {
      item.quantity = newQty
    }
  }

  function updateItem(cartId, ingredients, extras, quantity) {
    const item = items.value.find(i => i.cartId === cartId)
    if (!item) return
    item.ingredients = JSON.parse(JSON.stringify(ingredients || []))
    item.extras = JSON.parse(JSON.stringify(extras || []))
    item.quantity = quantity
  }

  function clearCart() {
    items.value = []
  }

  function requestEdit(cartId) {
    editRequest.value = items.value.find(i => i.cartId === cartId) || null
  }

  function clearEditRequest() {
    editRequest.value = null
  }

  return {
    MIN_ORDER,
    items,
    itemCount,
    totalPrice,
    meetsMinimum,
    calcItemTotal,
    addItem,
    removeItem,
    updateQuantity,
    updateItem,
    clearCart,
    editRequest,
    requestEdit,
    clearEditRequest,
  }
}
