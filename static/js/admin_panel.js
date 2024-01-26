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