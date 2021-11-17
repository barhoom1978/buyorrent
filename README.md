# Final Project: Buy or Rent

Web Programming with Python and JavaScript

Project summary
"Buy or Rent" is an application that helps prospective buyers of a residence
decide which option (buying or renting) is the best financial option for them.
It assumes the residence to be bought or to be rented are identical, or near
identical and cash flow equivalence between buying and renting. This means that
the difference between what you would pay to rent (ie, monthly rent) or buy (ie,
monthly mortgage) is invested in the stock market. For the rent option, the
deposit the renter would have used to buy a property, is also invested in the
stock market.

The stock market investment is assumed to be in the FTSE 100, a broad index of
UK listed stocks. The comparison is calculated over a period of 10 years and the
mortgage payment schedule is assumed to be over 25 years.

Project features and distinctions
- The project uses the Django web framework with two models, "User" (model for
subscribers of the app) and "Scenario" (model to save various rent/buy scenarios).
- JavaScript is used in the front end. This code includes checks on the validity
of data to be submitted (eg, a house price of zero not allowed) and AJAX/Fetch
communication with the server that is secured against CSRF attacks. The JavaScript
code also dynamically adds comma separators when some large numbers are typed,
for instance, the house price.
- The application is mobile responsive, for instance, when the screen size is
smaller than 600 pixels, it presents the user with a single column of input
blocks and removes detailed explanations and data tables.
- The application does fairly complicated time-value-of-money calculations which
determines the compound growth of investments and expenses over a ten-year period.
Python libraries used to this end includes pandas (data frames) and numpy_financial
- Other Python libraries used: numpy, datetime
- Detailed annotations are provided in the code that explains the calculations
and actions

How to run application:
- Make sure Django and Python vs 3 or higher is installed on your machine
- Make sure all the Python libraries shown in "requirements.txt" is installed
on your machine
- Download the folder "finalproject" and all its contents to your machine
- Open the command line, browse to the above folder eg,
"cd /Users/harvardx/Downloads/finalproject"
- Run the following in the command line: "python manage.py runserver", open
the indicated page eg, "http://127.0.0.1:8000/" in a web browser of your choice
(we recommend Google Chrome)

********

Files

The files and folders and what it contain listed below:

input.html and input.js
input.html is the input file where users add their buy/rent/financials data and
input.js is the JavaScript code that applies to input.html. Most of the fields
are pre-populated with average numbers for the UK. Two fields, the house price
and monthly rent is not pre-populated. The user MUST add data to these fields,
JavaScript code in input.js will prevent the user from submitting the form if
these fields are not populated. input.html also shows the results when the
submission button has been clicked and allows the user to save the results to
her/his profile. Other features of input.html and input.js:
- fetch/AJAX communication with the server that is secure against CSRF attacks
- creation and display of a data table using json data
- functions that force the use of numbers in numeric input fields
- dynamically add comma separators on large number fields

user_profile.html and user_profile.js
user_profile.html presents a list of scenarios saved by the user and
user_profile.js is the JavaScript code that applies to user_profile.html. The
user is presented with two buttons per saved scenario, "Open" and "Delete" which
allow the user to see the details of the scenario or delete it, respectively. A
user can only see his own scenarios.

models.py
The python file that stores two models,
- User: model for registered users to use the application
- Scenario: model for the different buy vs rent scenarios that the users have
saved

views.py
The file with most of the interesting code including financial calculations
to establish if buy is better than rent or vice versa. A summary of all the
different functions and what they do:
- retrieve_input_parameters_from_data_object: a function that retrieves input
parameters from a json object
- index: checks if user is authenticated and if so, open the info/landing page
- input: present the user with the data input form
- delete_scenario: on the user profile, the saved scenarios have a delete button,
this function removes scenarios a user elects to delete
- user_profile: a function that performs a data query for all scenarios that the
user has saved. A user can only see her/his own scenarios.
- do_financial_calcs: the function that takes all the input data, calculates
the respective outcomes for buying and renting, creates summary statements and
data tables which show the net positions over ten years. This function is also
used to recall previously saved scenarios.
- login_page, logout_page, register: three functions that, as the names indicate,
helps the user to log in, out and register

urls.py
list of all the patterns that Django will try to match the requested URL to
find the correct view.

styles.css
Styling sheet with mobile responsive features

index.html
An information page describing the underlying principles of the calculator.
This page is also the landing page when the user logs in.

layout.html
The html page with the common features used on all the different pages that a
signed-in user sees. This includes the navigation bar at the top of the page.

register.html and login.html
Html pages to register new users or log an existing user in

requirements.txt
A list of all the necessary python packages to run this application

templates/buyorrent
folder containing all the html files

static/buyorrent
The folder containing the JavaScript files (input.js and user_profile.js) and
the CSS styles file (styles.css)

Other files:
- migrations, __pycache__, db.sqlite, manage.py etc. created automatically when
Django project was created, and models were created / migrated  

********
