document.addEventListener('DOMContentLoaded', function() {
    // apply the thousands separator on houseprice and deposit inputs
    add_thousands_comma_sep_on_certain_fields();
    // create short_summary variable, to be used if the scenario is saved
    var short_summary = "";
    // hide result section when data has not been submitted yet
    hide_section('#div_results');
    // sends input data to server for calculations,
    document.querySelector('#submit_input').onclick = sends_csrf_secured_input_data_to_server;
    // save scenario to profile page
    document.querySelector('#save_results_button').onclick = save_results_to_profile;
    // show or hide detailed calcs when requested
    document.querySelector('#show_detailed_calcs_button').onclick = function () {
        if (this.innerHTML === "Show detailed calculations") {
            unhide_section('#div_detailed_results');
            this.innerHTML = "Hide detailed calculations";
        } else {
            hide_section('#div_detailed_results');
            this.innerHTML = "Show detailed calculations";
        };
        // scroll to bottom of page
        window.scrollTo(0,document.body.scrollHeight);
    };
})

// if the save button is clicked, the scenario is saved to the user profile
function save_results_to_profile () {
    // get input data
    let input_data = get_input_data()
    // get csrf token, required for fetch request which is csrf secured
    const csrftoken = getCookie('csrftoken');
    // create request template, add csrf token to it
    const request = new Request(
        '/user_profile',
        {headers: {'X-CSRFToken': csrftoken}}
    );
    // sends AJAX fetch request to server
    fetch(request, {
        method: 'POST',
        mode: 'same-origin',
        body: JSON.stringify({
            houseprice: input_data.houseprice,
            deposit: input_data.deposit,
            interest_rate: input_data.interest_rate,
            buildingfees: input_data.buildingfees,
            maintenancecosts: input_data.maintenancecosts,
            rent: input_data.rent,
            rentersinsurance: input_data.rentersinsurance,
            inflation: input_data.inflation,
            growth_ftse: input_data.growth_ftse,
            growth_house: input_data.growth_house,
            short_summary: short_summary,
        })
    })
    .then(response => response.json())
    .then(result => {
        // console.log(result)
        window.location.href = '/user_profile'
    });
    // do not refresh the page
    return false;
}

// function to shift focus to an element
function focus_on_this_box(input_box_id) {
  const input_box = document.getElementById(input_box_id);
  input_box.focus();
  input_box.select();
}

// post request to server with input data, csrf secured
function sends_csrf_secured_input_data_to_server () {
    // check if there's invalid input data
    // elements considered
    const check_houseprice = document.querySelector('#houseprice').value;
    const check_deposit = document.querySelector('#deposit').value;
    const check_rent = document.querySelector('#rent').value;
    // error messages
    const error_no_zero_values = "Invalid input, value must be larger than 0";
    const error_deposit_smaller_houseprice = "Invalid input, deposit must be smaller than house price";
    // houseprice can't be zero
    if (check_houseprice === "" || check_houseprice === "NaN" || check_houseprice === "0") {
        alert(error_no_zero_values);
        focus_on_this_box("houseprice");
    // rent can't be zero
    } else if (check_rent === "" || check_rent === "NaN" || check_rent === "0") {
        alert(error_no_zero_values);
        focus_on_this_box("rent");
    // deposit can't be bigger than houseprice
    } else if (parseFloat(only_numbers(check_deposit)) > parseFloat(only_numbers(check_houseprice))) {
        alert(error_deposit_smaller_houseprice);
        focus_on_this_box("deposit");
    } else {
        // get input data
        let input_data = get_input_data()
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
                houseprice: input_data.houseprice,
                deposit: input_data.deposit,
                interest_rate: input_data.interest_rate,
                buildingfees: input_data.buildingfees,
                maintenancecosts: input_data.maintenancecosts,
                rent: input_data.rent,
                rentersinsurance: input_data.rentersinsurance,
                inflation: input_data.inflation,
                growth_ftse: input_data.growth_ftse,
                growth_house: input_data.growth_house,
            })
        })
        .then(response => response.json())
        .then(result => {
            // unhide result section
            unhide_section('#div_results');
            // add paragraph results
            document.querySelector('#summary_buy').innerHTML = result.buyer_net_position;
            document.querySelector('#summary_rent').innerHTML = result.renter_net_position;
            document.querySelector('#summary').innerHTML = result.summary;
            // hide detailed results
            hide_section('#div_detailed_results');
            // change title of "Hide detailed calculations"
            document.querySelector('#show_detailed_calcs_button').innerHTML = "Show detailed calculations"
            // create detailed results table and add to div element
            create_table_using_json_data(result.table_data);
            // add notes for results table, but clear list first...
            document.querySelector('#list_of_notes').innerHTML = "";
            add_notes_to_data_table(result.note_sdlt);
            add_notes_to_data_table(result.note_cash);
            // save short_summary in variable, to be used if the scenario is saved
            short_summary = result.short_summary;
            // scroll to bottom
            window.scrollTo(0,document.body.scrollHeight);
        });
        // do not refresh the page
        return false;
    }
};

// function that obtains input data from input boxes
function get_input_data () {
    // get input data
    const houseprice = document.querySelector('#houseprice').value;
    const deposit = document.querySelector('#deposit').value;
    const interest_rate = document.querySelector('#interest_rate').value;
    const buildingfees = document.querySelector('#buildingfees').value;
    const maintenancecosts = document.querySelector('#maintenancecosts').value;
    const rent = document.querySelector('#rent').value;
    const rentersinsurance = document.querySelector('#rentersinsurance').value;
    const inflation = document.querySelector('#inflation').value;
    const growth_ftse = document.querySelector('#growth_ftse').value;
    const growth_house = document.querySelector('#growth_house').value;
    // return input data
    return {
        houseprice,deposit,interest_rate,buildingfees,maintenancecosts,rent,
        rentersinsurance,inflation,growth_ftse,growth_house,
    };
}

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

// function to hide sections of code
function hide_section (elem) {
    document.querySelector(elem).style.display = 'none';
}

// function to unhide sections of code
function unhide_section (elem) {
    document.querySelector(elem).style.display = 'block';
}

// Apply a comma thousands-separator to certain fields with large numbers. The
// function also checks that only numbers, not characters, are typed
function add_thousands_comma_sep_on_certain_fields () {
    // the fields to which thousands separator are added to
    var n1 = document.querySelector('#houseprice');
    var n2 = document.querySelector('#deposit');
    // when typing, check that the input are numbers and add comma separators,
    // do it as the user types
    n1.onkeyup = n1.onchange = n2.onkeyup = n2.onchange = function() {
        let temp = only_numbers(this.value, 0);
        this.value = add_commas(temp);
    };
    // when moving away from a field parse the value as a floating-point number
    // and then add comma separators
    n1.onblur = n2.onblur = function() {
        temp = parseFloat(only_numbers(this.value));
        this.value = add_commas(temp.toFixed(0));
    };
}

// function that inserts commas as thousand separators
function add_commas(n){
    var reg_exp =  /(\d+)(\d{3})/;
    return String(n).replace(/^\d+/, function (x) {
        while(reg_exp.test(x)){
            x = x.replace(reg_exp, '$1,$2');
        }
        return x;
    });
}

// function that checks that input is only numbers, it can also truncate decimals
function only_numbers(input, decimals){
    input = input.replace(/[^\d\.]+/g, '');
    var x_1 = input.indexOf('.'), x_2 = -1;
    if (x_1 != -1) {
        ++x_1;
        x_2= input.indexOf('.', x_1);
        if (x_2 > x_1) input = input.substring(0, x_2);
        if (typeof decimals === 'number') input = input.substring(0, x_1 + decimals);
    }
    return input;
}

// function that creates a data table based on json data from server
function create_table_using_json_data(table_data) {
    // get headers from data table
    var column = [];
    for (var i = 0; i < table_data.length; i++) {
        for (var key in table_data[i]) {
            if (column.indexOf(key) === -1) {
                column.push(key);
            }
        }
    }
    // create table variable
    var table = document.createElement("table");
    // create table header row using headers obtained above
    var tr = table.insertRow(-1);
    for (var i = 0; i < column.length; i++) {
        var th = document.createElement("th");
        th.innerHTML = column[i];
        tr.appendChild(th);
    }
    // populate table rows with json data
    for (var i = 0; i < table_data.length; i++) {
        tr = table.insertRow(-1);
        for (var j = 0; j < column.length; j++) {
            var table_cell = tr.insertCell(-1);
            if (j==0) {
                table_cell.innerHTML = table_data[i][column[j]];
            } else {
                table_cell.innerHTML = add_commas(table_data[i][column[j]].toFixed(0));
            }
        }
    }
    // add table to html element
    var divContainer = document.getElementById("show_table");
    divContainer.innerHTML = "";
    divContainer.appendChild(table);
}

// function that adds notes
function add_notes_to_data_table (note) {
    var ul = document.getElementById("list_of_notes");
    var li = document.createElement("li");
    li.className = "list-group-item";
    li.innerHTML= note;
    ul.appendChild(li);
};
