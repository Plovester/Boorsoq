function addItemToCart(item_id, item_price) {
    let cart = window.sessionStorage.getItem('cart')
    if (cart) {
        let cart_items = JSON.parse(cart)

        if (cart_items.find(item => item.item_id === item_id)) {
            item = cart_items.find(item => item.item_id === item_id)
            item.item_value += 1
        } else {
            const new_item = {
                item_id: item_id,
                item_price: item_price,
                item_value: 1
            }

            cart_items.push(new_item)
        }

        window.sessionStorage.setItem('cart', JSON.stringify(cart_items))
    } else {
        let cart_items = []
        const new_item = {
                    item_id: item_id,
                    item_price: item_price,
                    item_value: 1
                }
        cart_items.push(new_item)
        window.sessionStorage.setItem('cart', JSON.stringify(cart_items))
    }
}
