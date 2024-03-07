function changeOrderStatus(id) {
    const selected_status = document.getElementById(`statusOptions${id}`).value

    let response = fetch(`/orders/${id}`, {
            method: 'PUT',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({status: selected_status})
        })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                throw new Error('Request failed');
            }
        })
        .then(data => {
            let status = document.querySelector(`#order${id}-modal #status`)
            status.value = data.status
        })
}

function changeOrderDetails(id) {
    const status = document.querySelector(`#order${id}-modal #status`).value

    let response = fetch(`/orders/${id}`, {
            method: 'PUT',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({status: status})
        })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                throw new Error('Request failed');
            }
        })
        .then(data => {
            let status = document.getElementById(`statusOptions${id}`)
            status.value = data.status
        })

}

function saveProductChanges(id) {
    const name = document.querySelector(`#product${id}-modal #name`).value
    const category_id = document.querySelector(`#product${id}-modal #category`).value
    const price = document.querySelector(`#product${id}-modal #price`).value
    const image_url = document.querySelector(`#product${id}-modal #image`).value
    const description = document.querySelector(`#product${id}-modal #description`).value
    const visibility = document.querySelector(`#product${id}-modal .form-check #visibility`).checked

    const newProductParams = {
                        name: name,
                        category_id: category_id,
                        price: Math.round(price * 100),
                        image_url: image_url,
                        description: description,
                        visibility: visibility
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

        let category = document.getElementById(`product${id}-category`);
        category.innerHTML = data.category;

        let price = document.getElementById(`product${id}-price`);
        price.innerHTML = `£${(data.price / 100).toFixed(1)}`;

        let image = document.querySelector(`#product${id}-image .item-img`);
        image.src = data.image_url;

        let description = document.getElementById(`product${id}-description`);
        description.innerHTML = data.description;

        let visibility = document.getElementById(`product${id}-visibility`)
        if (data.visibility) {
            visibility.innerHTML = `<i class="fa-solid fa-eye-slash" style="color: #ff7a00;"></i>`
        } else {
            visibility.innerHTML = `<i class="fa-solid fa-eye" style="color: #ff7a00;"></i>`
        }
    })
}

function changeProductVisibility(element, id) {
    let response = fetch(`/products/${id}`, {
        method: 'PUT',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({visibility: !(+element.dataset.visibility)})
    })
    .then(response => {
        if (response.ok) {
            return response.json()
        } else {
            throw new Error('Request failed');
        }
    })
    .then(data => {
        element.dataset.visibility = `${+data.visibility}`
        const visibility = document.querySelector(`#product${id}-modal .form-check #visibility`)

        if (data.visibility) {
            element.innerHTML = `<i class="fa-solid fa-eye-slash" style="color: #ff7a00;"></i>`
            visibility.checked = true
        } else {
            element.innerHTML = `<i class="fa-solid fa-eye" style="color: #ff7a00;"></i>`
            visibility.checked = false
        }
    })
}

function saveCategoryChanges(id) {
    const name = document.querySelector(`#category${id}-modal #name`).value

    let response = fetch(`/categories/${id}`, {
        method: 'PUT',
        mode: 'cors',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({name: name})
    })
    .then(response => {
        if (response.ok) {
            return response.json()
        } else {
            throw new Error('Request failed');
        }
    })
    .then(data => {
        let name = document.getElementById(`category${id}-name`);
        name.innerHTML = data;
    })
}