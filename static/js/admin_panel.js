function changeOrderStatus(id) {
    let selected_status = document.getElementById(`statusOptions${id}`).value

    let response = fetch(`/orders/${id}/status`, {
            method: 'PUT',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({status: selected_status})
        })
        .then(response => {
            if (response.ok) {
                return response
            } else {
                throw new Error('Request failed');
            }
        })
}

function saveProductChanges(id) {
    const name = document.querySelector(`#product${id}-modal #name`).value
    const price = document.querySelector(`#product${id}-modal #price`).value
    const image_url = document.querySelector(`#product${id}-modal #image`).value
    const description = document.querySelector(`#product${id}-modal #description`).value

    const newProductParams = {
                        name: name,
                        price: Math.round(price * 100),
                        image_url: image_url,
                        description: description
                    }

    let response = fetch(`/products/${id}`, {
        method: 'PUT',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(newProductParams)
    })
    .then(response => {
        if (response.ok) {
            return response.json()
        } else {
            throw new Error('Request failed');
        }
    })
    .then(data => {
        let name = document.getElementById(`product${id}-name`);
        name.innerHTML = data.name;

        let price = document.getElementById(`product${id}-price`);
        price.innerHTML = `£${(data.price / 100).toFixed(1)}`;

        let image = document.querySelector(`#product${id}-image .item-img`);
        image.src = data.image_url;

        let description = document.getElementById(`product${id}-description`);
        description.innerHTML = data.description;
    })
}