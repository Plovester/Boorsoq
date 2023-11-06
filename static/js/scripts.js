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
        });
}

