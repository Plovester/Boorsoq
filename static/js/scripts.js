function addItemToCart(item_id) {
    const new_item = {
                    item_id: item_id,
                    item_qty: 1
                }

    let response = fetch('cart/add_item', {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(new_item)
        })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                throw new Error('Request failed');
            }
        })
        .then(data => {
            label = document.getElementById('cart-qty-label')
            label.innerHTML = data.result
        })
}



