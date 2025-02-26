let currentDate = new Date().toLocaleDateString();

function changeOrderStatus(id) {
    const selected_status = document.getElementById(`statusOptions${id}`).value

    let response = fetch(`/admin/orders/${id}`, {
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

    let response = fetch(`/admin/orders/${id}`, {
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

    let response = fetch(`/admin/products/${id}`, {
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
    let response = fetch(`/admin/products/${id}`, {
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

    let response = fetch(`/admin/categories/${id}`, {
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

function ordersByStatus() {
    let date_start = document.getElementById('orders-by-status-start').value
    let date_end = document.getElementById('orders-by-status-end').value

    if (!date_start) {
        date_start = new Date();
        date_start.setDate(date_start.getDate() - 7);
        date = new Date(date_start).toISOString()
        document.getElementById('orders-by-status-start').placeholder = `${date.slice(8, 10)}/${date.slice(5, 7)}/${date.slice(0, 4)}`;
    } else {
        date = date_start.split("/");
        date_start = new Date(`${date[2]}-${date[1]}-${date[0]}`);
    }

    if (!date_end) {
        date_end = new Date()
        date = new Date(date_end).toISOString()
        document.getElementById('orders-by-status-end').placeholder = `${date.slice(8, 10)}/${date.slice(5, 7)}/${date.slice(0, 4)}`;
    } else {
        date = date_end.split("/");
        date_end = new Date(`${date[2]}-${date[1]}-${date[0]}`);
    }

    const dates_range = {
        date_start: date_start,
        date_end: date_end
    }

    let response = fetch(`/admin/reports/number_of_orders`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dates_range)
        })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                throw new Error('Request failed');
            }
        })
        .then(data => {
            const colors_for_chart = generate_rgba_for_charts(Object.keys(data).length)

            const ctx = document.getElementById('ordersByStatus').getContext('2d');
            const myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        label: 'Number of orders',
                        data: Object.values(data),
                        backgroundColor: colors_for_chart.backgroundColor,
                        borderColor: colors_for_chart.borderColor,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            min: 0,
                            max: Math.max( ...Object.values(data)) + 1,
                            ticks: {
                                precision: 0,
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        })
    }

function getPopularProducts() {
    let date_start = document.getElementById('popular-products-start').value
    let date_end = document.getElementById('popular-products-end').value

    if (!date_start) {
        date_start = new Date();
        date_start.setDate(date_start.getDate() - 7);
        date = new Date(date_start).toISOString()
        document.getElementById('popular-products-start').placeholder = `${date.slice(8, 10)}/${date.slice(5, 7)}/${date.slice(0, 4)}`
    } else {
        date = date_start.split("/");
        date_start = new Date(`${date[2]}-${date[1]}-${date[0]}`);
    }

    if (!date_end) {
        date_end = new Date()
        date = new Date(date_end).toISOString()
        document.getElementById('popular-products-end').placeholder = `${date.slice(8, 10)}/${date.slice(5, 7)}/${date.slice(0, 4)}`
    } else {
        date = date_end.split("/");
        date_end = new Date(`${date[2]}-${date[1]}-${date[0]}`);
    }

    const dates_range = {
        date_start: date_start,
        date_end: date_end
    }

    let response = fetch(`/admin/reports/most_popular_products`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dates_range)
        })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                throw new Error('Request failed');
            }
        })
        .then(data => {
            const colors_for_chart = generate_rgba_for_charts(Object.keys(data).length)

            const ctx = document.getElementById('mostPopularProducts').getContext('2d');;
            const myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        label: 'Number of sold products',
                        data: Object.values(data),
                        backgroundColor: colors_for_chart.backgroundColor,
                        borderColor: colors_for_chart.borderColor,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            min: 0,
                            max: Math.max( ...Object.values(data)) + 1,
                            ticks: {
                                precision: 0,
                                stepSize: 1
                            }
                        }
                    }
                }
            });
        })
    }

function editAdminName(id) {
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
            let admin_name = document.getElementById("current-user-name")
            admin_name.innerHTML = data.name

        })
}

function editAdminEmail(id) {
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
            let admin_email = document.getElementById("current-user-email")
            admin_email.innerHTML = data.email
        })
}

function editAdminPhone(id) {
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
            let admin_phone = document.getElementById("current-user-phone")
            admin_phone.innerHTML = data.phone_number
        })
}

function editAdminPassword(id) {
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

function createNewAdmin() {
    const new_admin_name = document.getElementById('new-admin-name').value
    const new_admin_phone = document.getElementById('new-admin-phone').value
    const new_admin_email = document.getElementById('new-admin-email').value
    const new_admin_password = document.getElementById('new-admin-password').value

    let response = fetch(`/admin/new_admin`, {
            method: 'POST',
            mode: 'cors',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({name: new_admin_name,
                                  phone_number: new_admin_phone,
                                  email: new_admin_email,
                                  password: new_admin_password})
        })
        .then(response => {
            if (response.ok) {
                return response.json()
            } else {
                throw new Error('Request failed');
            }
        })
        .then(data => {
            console.log('Success')
        })
}

function generate_rgba_for_charts(length) {
    let colors_options = {
        backgroundColor: [],
        borderColor: []
    }

    for (let i = 0; i < length; i++) {
        const r = Math.round(Math.random() * 255)
        const g = Math.round(Math.random() * 255)
        const b = Math.round(Math.random() * 255)

        const new_color = `rgba(${r}, ${g}, ${b},`

        colors_options.backgroundColor.push(new_color + ' 0.2)')
        colors_options.borderColor.push(new_color + ' 1)')
    }

    return colors_options
}

const report_start = document.querySelector('input[name="orders-by-status-start"]')

const datepicker = new Datepicker(report_start, {
    datesDisabled: function (date) {
        let isDateDisabled;
        const current_date = new Date()
        const today = new Date(current_date.getFullYear(), current_date.getMonth(), current_date.getDate());
        if (date > today) {
            isDateDisabled = true
        } else {
            isDateDisabled = false
        }
        return isDateDisabled;
    },
    format: 'dd/mm/yyyy',
    weekStart: 1
});

const report_end = document.querySelector('input[name="orders-by-status-end"]')

const datepicker1 = new Datepicker(report_end, {
    datesDisabled: function (date) {
        let isDateDisabled;
        const current_date = new Date()
        const today = new Date(current_date.getFullYear(), current_date.getMonth(), current_date.getDate());
        if (date > today) {
            isDateDisabled = true
        } else {
            isDateDisabled = false
        }
        return isDateDisabled;
    },
    format: 'dd/mm/yyyy',
    weekStart: 1
});

const products_report_start = document.querySelector('input[name="popular-products-start"]')

const datepicker2 = new Datepicker(products_report_start, {
    datesDisabled: function (date) {
        let isDateDisabled;
        const current_date = new Date()
        const today = new Date(current_date.getFullYear(), current_date.getMonth(), current_date.getDate());
        if (date > today) {
            isDateDisabled = true
        } else {
            isDateDisabled = false
        }
        return isDateDisabled;
    },
    format: 'dd/mm/yyyy',
    weekStart: 1
});

const products_report_end = document.querySelector('input[name="popular-products-end"]')

const datepicker3 = new Datepicker(products_report_end, {
    datesDisabled: function (date) {
        let isDateDisabled;
        const current_date = new Date()
        const today = new Date(current_date.getFullYear(), current_date.getMonth(), current_date.getDate());
        if (date > today) {
            isDateDisabled = true
        } else {
            isDateDisabled = false
        }
        return isDateDisabled;
    },
    format: 'dd/mm/yyyy',
    weekStart: 1
});

document.addEventListener('DOMContentLoaded', ordersByStatus());
document.addEventListener('DOMContentLoaded', getPopularProducts());


