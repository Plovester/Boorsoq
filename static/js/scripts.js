function changeQtyLabel(qty) {
    let label = document.getElementById('cart-qty-label')

    if (qty > 0) {
        label.classList.add('visible');
        label.classList.remove('invisible');
        label.innerHTML = qty
    } else {
        label.classList.remove('visible');
        label.classList.add('invisible');
    }
}

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
            changeQtyLabel(data.result)
        })
}

function adjustQty(item_id, adjustment_qty) {
    let qty_input = document.getElementById(item_id + '-qty')
    let updated_qty = +qty_input.value + adjustment_qty

    if (updated_qty > 0) {
        updateQty(item_id, updated_qty, qty_input)
    } else {
        removeItem(item_id)
    }
}

function adjustQtyInput(qty_input, item_id) {
    let updated_qty = +qty_input.value

    if (updated_qty > 0) {
        updateQty(item_id, updated_qty, qty_input)
    } else {
        removeItem(item_id)
    }
}

function updateQty(item_id, updated_qty, qty_input) {
    const updated_item = {
                        item_id: item_id,
                        item_qty: updated_qty
                    }

    let response = fetch('cart/adjust_item_qty', {
            method: 'PUT',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updated_item)
        })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                throw new Error('Request failed');
            }
        })
        .then(data => {
            qty_input.value = data.result_item['item_qty']

            let item_total_price = document.getElementById(item_id + '-total-price')
            item_total_price.innerHTML = '£' + (data.result_item_total_price / 100).toFixed(1)

            let total_qty_cell = document.getElementById('total_qty')
            total_qty_cell.innerHTML = `<strong>${data.result_total_qty}</strong>`;

            changeQtyLabel(data.result_total_qty)

            let total_price_cell = document.getElementById('total_price')
            total_price_cell.innerHTML = `<strong>£${(data.result_total_price / 100).toFixed(1)}</strong>`
        })
}

function removeItem(item_id) {
    let response = fetch('cart/remove_item', {
            method: 'DELETE',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(item_id)
        })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                throw new Error('Request failed');
            }
        })
        .then(data => {
            let item_to_remove = document.getElementById(item_id + '-list-group')
            item_to_remove.remove()

            let total_qty_cell = document.getElementById('total_qty')
            total_qty_cell.innerHTML = `<strong>${data.result_total_qty}</strong>`;

            changeQtyLabel(data.result_total_qty)

            let total_price_cell = document.getElementById('total_price')
            total_price_cell.innerHTML = `<strong>£${(data.result_total_price / 100).toFixed(1)}</strong>`
        })
}

function createOrder() {
    const order_date = document.getElementById('order-date').value

    let response = fetch('confirm_order', {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(order_date)
        })
        .then(response => {
            if (response.ok) {
                changeQtyLabel(0)
                window.location.href = "/";
            } else {
                throw new Error('Request failed');
            }
        })
}

function editUserName(id) {
    const name = document.getElementById('name').value

    let response = fetch(`/user_settings/${id}`, {
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
            let user_name_in_header = document.getElementById("user-name")
            user_name_in_header.innerHTML = data.name

            let user_name_in_settings = document.getElementById("current-user-name")
            user_name_in_settings.innerHTML = data.name

        })
}

function editUserEmail(id) {
    const email = document.getElementById('email').value

    let response = fetch(`/user_settings/${id}`, {
            method: 'PUT',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({email: email})
        })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                throw new Error('Request failed');
            }
        })
        .then(data => {
            let user_email = document.getElementById("current-user-email")
            user_email.innerHTML = data.email
        })
}

function editUserPhone(id) {
    const phone = document.getElementById('phone').value

    let response = fetch(`/user_settings/${id}`, {
            method: 'PUT',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({phone_number: phone})
        })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                throw new Error('Request failed');
            }
        })
        .then(data => {
            let user_phone = document.getElementById("current-user-phone")
            user_phone.innerHTML = data.phone_number
        })
}

function editUserPassword(id) {
    const old_password = document.getElementById('old-password').value
    const new_password = document.getElementById('new-password').value
    const confirmed_password = document.getElementById('confirmed-password').value

    if (new_password === confirmed_password) {
        const password_info = {
                        old_password: old_password,
                        new_password: new_password
                    }

        let response = fetch(`/user_settings/${id}/password`, {
            method: 'PUT',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(password_info)
        })
        .then(response => {
            if (response.ok) {
                return response
            } else {
                throw new Error('Request failed')
            }
        })
    }
}

const elem = document.querySelector('input[name="order-date"]');
const datepicker = new Datepicker(elem, {
    datesDisabled: function (date) {
        let isDateDisabled;
        const current_date = new Date()
        const today = new Date(current_date.getFullYear(), current_date.getMonth(), current_date.getDate());
        if (date < today) {
            isDateDisabled = true
        } else {
            isDateDisabled = false
        }
        return isDateDisabled;
    },
    format: 'dd/mm/yyyy',
    weekStart: 1
});
