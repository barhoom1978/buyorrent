document.addEventListener('DOMContentLoaded', function () {
    // Hide the result divs till the open button is clicked (addressed later on)
    document.querySelectorAll('.div_results').forEach(div => {
        // console.log(div);
        div.style.display = 'none';
    });
    // procedures for buttons clicked
    document.querySelectorAll('.btn').forEach(button => {
        button.onclick = function() {
            // if delete button is clicked...
            if (this.innerHTML==="Delete") {
                if (confirm("Delete this scenario?") == true) {
                    const to_be_deleted_scenario_id = this.dataset.id;
                    // console.log(to_be_deleted_scenario_id);
                    // get csrf token, required for fetch request which is csrf secured
                    const csrftoken = getCookie('csrftoken');
                    // create request template, add csrf token to it
                    const request = new Request(
                        '/delete_scenario',
                        {headers: {'X-CSRFToken': csrftoken}}
                    );
                    // sends AJAX fetch request to server
                    fetch(request, {
                        method: 'POST',
                        mode: 'same-origin',
                        body: JSON.stringify({
                            scenario_id: to_be_deleted_scenario_id,
                        })
                    })
                    .then(response => response.json())
                    .then(result => {
                        // console.log(result)
                    })
                }
                // Refresh page
                location.reload();
                return false;
            }
            // if open button is clicked
            else if (this.innerHTML==="Open") {
                // get scenario id, saved in data-id property of div
                const scenario_id = this.dataset.id
                // get csrf token, required for fetch request which is csrf secured
                const csrftoken = getCookie('csrftoken');
                // create request template, add csrf token to it
                const request = new Request(
                    '/do_financial_calcs',
                    {headers: {'X-CSRFToken': csrftoken}}
                );
                // sends AJAX fetch request to server
                fetch(request, {
                    method: 'POST',
                    mode: 'same-origin',
                    body: JSON.stringify({
                        scenario_id: scenario_id,
                    })
                })
                .then(response => response.json())
                .then(result => {
                    // change results div to visible (called 'block' in js)
                    document.querySelector('#div_results'+scenario_id).style.display = 'block';
                    // add results to various divs
                    document.querySelector('#summary_buy'+scenario_id).innerHTML = result.buyer_net_position;
                    document.querySelector('#summary_rent'+scenario_id).innerHTML = result.renter_net_position;
                    document.querySelector('#summary'+scenario_id).innerHTML = result.summary;
                });
                // change title of "Open" button to "Hide"
                this.innerHTML="Hide"
                // do not refresh the page
                return false;
            }
            // hide the detailed scenario info
            else if (this.innerHTML==="Hide") {
                scenario_id = this.dataset.id
                document.querySelector('#div_results'+scenario_id).style.display = 'none';
                // change title of "Hide" button to "Open"
                this.innerHTML="Open"
            }
        };
    });
})

// Code to obtain the session's CSRF token, copied from django dodumentation,
// see: https://docs.djangoproject.com/en/3.1/ref/csrf/
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
