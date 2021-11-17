from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.db import IntegrityError
from django.urls import reverse
from .models import User
import json
from django.views.decorators.csrf import csrf_exempt
from .models import User, Scenario

# financial, numerical and dataframe libraries
import pandas as pd
import numpy as np
import numpy_financial as npf
import datetime

# column titles of the multiyear data frame to be created
COLUMN_NAMES = ['year', 'rent', 'new_investment_renter', 'old_investment_deposit',
                'renters_cashflow', 'pre_inv_diff', 'mortgage_interest_payments',
                'mortgage_capital_payments','fees_and_maintenance','new_investment_buyer',
                'buyers_cashflow'
                ]

# a function that retrieves input parameters from json object
def retrieve_input_parameters_from_data_object(data_from_post):
    houseprice = float(data_from_post.get('houseprice','').replace(',',''))
    deposit = float(data_from_post.get('deposit', '').replace(',',''))
    interest_rate = float(data_from_post.get('interest_rate', '').replace(',',''))
    buildingfees = float(data_from_post.get('buildingfees', '').replace(',',''))
    maintenancecosts = float(data_from_post.get('maintenancecosts', '').replace(',',''))
    rent = float(data_from_post.get('rent', '').replace(',',''))
    rentersinsurance = float(data_from_post.get('rentersinsurance', '').replace(',',''))
    inflation = float(data_from_post.get('inflation', '').replace(',',''))
    growth_ftse = float(data_from_post.get('growth_ftse', '').replace(',',''))
    growth_house = float(data_from_post.get('growth_house', '').replace(',',''))
    return houseprice, deposit, interest_rate, buildingfees, maintenancecosts, \
            rent, rentersinsurance, inflation, growth_ftse, growth_house

def index(request):
    if request.user.is_authenticated:
        return render(request, 'buyorrent/index.html')
    else:
        return HttpResponseRedirect(reverse('login'))

@login_required
def input(request):
    return render(request, 'buyorrent/input.html')

@login_required
def delete_scenario(request):
    if request.method == "POST":
        data_from_post = json.loads(request.body)
        scenario_id = data_from_post.get('scenario_id','')
        Scenario.objects.filter(id=scenario_id).delete()
        return JsonResponse({'scenario_id': scenario_id,'status': 200})

@login_required
def user_profile(request):
    if request.method == "POST":
        # load data
        data_from_post = json.loads(request.body)
        # use retrieve_input_parameters_from_data_object function
        houseprice, deposit, interest_rate, buildingfees, maintenancecosts, rent, \
        rentersinsurance, inflation, growth_ftse, growth_house \
            = retrieve_input_parameters_from_data_object(data_from_post)
        # save short summary, to be used in scenario model
        short_summary = data_from_post.get('short_summary', '')
        # save input data and short summary in scenario model
        scenario = Scenario(
            owner = request.user,
            houseprice = houseprice,
            deposit = deposit,
            interest_rate = interest_rate,
            buildingfees = buildingfees,
            maintenancecosts = maintenancecosts,
            rent = rent,
            rentersinsurance = rentersinsurance,
            inflation = inflation,
            growth_ftse = growth_ftse,
            growth_house = growth_house,
            summary = short_summary,
        )
        scenario.save()
        # send an all clear 200 signal to the client and also the id of the post
        # just created
        return JsonResponse({'status': 200,
                                'id': scenario.id})
    # if a get request is sent, load the user's saved scenarios
    else:
        user = User.objects.get(username=request.user.username)
        scenarios_list = Scenario.objects.all().filter(owner=user)
        scenarios_list = scenarios_list.order_by("-timestamp").all()
        return render(request, "buyorrent/user_profile.html", {
                "scenarios": scenarios_list,
            })

@login_required
def do_financial_calcs(request):
    if request.method == "POST":
        # load data
        data_from_post = json.loads(request.body)
        # draw scenario id from request object if a scenario instance has
        # already been created
        scenario_id = data_from_post.get('scenario_id','')
        # if a scenario exists, load its data onto variables
        if scenario_id != "":
            temp_scenario_return_variable = Scenario.objects.get(pk=scenario_id)
            houseprice, deposit, interest_rate, buildingfees, maintenancecosts, rent, \
            rentersinsurance, inflation, growth_ftse, growth_house \
                = temp_scenario_return_variable.serialise()
        # otherwise download data from inputform
        else:
            # use retrieve_input_parameters_from_data_object function
            houseprice, deposit, interest_rate, buildingfees, maintenancecosts, rent, \
            rentersinsurance, inflation, growth_ftse, growth_house \
                = retrieve_input_parameters_from_data_object(data_from_post)
        # create data frame to store data created in the following steps
        df = pd.DataFrame(columns=COLUMN_NAMES)
        # create year column
        this_year = datetime.date.today().year
        number_of_years_into_future =  10
        years_column = [i for i in range(this_year+1, this_year + number_of_years_into_future+1)]
        df.year = years_column
        # create rent column
        rent_column = [(rent*12+rentersinsurance)*(1+inflation/100)**(i-1) for i in range(1,number_of_years_into_future+1)]
        df.rent = rent_column
        # calculate stamp duty, it is used to calculate loan amount
        if houseprice > 1500000:
            stamp_duty = (houseprice-1500000)*0.12+(1500000-925000)*0.1+(925000-250000)*0.05+(250000-125000)*0.02
        elif houseprice > 925000:
             stamp_duty = (houseprice-925000)*0.1+(925000-250000)*0.05+(250000-125000)*0.02
        elif houseprice > 250000:
             stamp_duty = (houseprice-250000)*0.05+(250000-125000)*0.02
        elif houseprice > 125000:
             stamp_duty = (houseprice-125000)*0.02
        else:
            stamp_duty = 0
        # add surveyor and solicitor fees
        other_fees = 4400
        stamp_duty_and_fees = stamp_duty + other_fees
        # calculate loan amount
        loan_amount = houseprice + stamp_duty_and_fees - deposit
        # create interest_payments column
        per = np.arange(number_of_years_into_future) + 1
        ipmt = -npf.ipmt(interest_rate/100, per, 25, loan_amount)
        df.mortgage_interest_payments = ipmt
        # create capital_payments column
        ppmt = -npf.ppmt(interest_rate/100, per, 25, loan_amount)
        df.mortgage_capital_payments = ppmt
        # calculate building fees
        fees_and_maintenance = [(buildingfees+maintenancecosts)*(1+inflation/100)**(i-1) for i in range(1,number_of_years_into_future+1)]
        df.fees_and_maintenance = fees_and_maintenance
        # calculate pre-inv diff
        df.pre_inv_diff = df.mortgage_capital_payments + df.mortgage_interest_payments \
            + df.fees_and_maintenance - df.rent
        # calculate new_investment_renter & new_investment_buyer
        temp_series=[]
        for i in range(1,number_of_years_into_future+1):
            if i == 1:
                temp_num = abs(df.pre_inv_diff[i-1])*(1+growth_ftse/2/100)
                temp_series.append(temp_num)
            else:
                temp_num = abs(df.pre_inv_diff[i-1])*(1+growth_ftse/2/100) + \
                    temp_series[i-2]*(1+growth_ftse/100)
                temp_series.append(temp_num)
        if df.pre_inv_diff[0]>0:
            df.new_investment_renter = temp_series
            df.new_investment_buyer = [0] * 10
        else:
            df.new_investment_buyer = temp_series
            df.new_investment_renter = [0] * 10
        # calculate old_investment_deposit
        deposit_investment_function = lambda year : deposit*(1+growth_ftse/100)**year
        years = [i for i in range(1,number_of_years_into_future+1)]
        old_investment_deposit =list(map(deposit_investment_function,years))
        df.old_investment_deposit = old_investment_deposit
        # calculate renters_cashflow & buyers_cashflow
        if df.pre_inv_diff[0]>0:
            df.renters_cashflow = df.rent + df.pre_inv_diff
            df.buyers_cashflow = df.mortgage_capital_payments + \
                df.mortgage_interest_payments + df.fees_and_maintenance
        else:
            df.renters_cashflow = df.rent
            df.buyers_cashflow = df.mortgage_capital_payments + \
                df.mortgage_interest_payments + df.fees_and_maintenance + \
                    abs(df.pre_inv_diff)
        # summary of the renter's position, calcs
        renter_deposit = df.old_investment_deposit[number_of_years_into_future-1]
        renter_additional_investment = df.new_investment_renter[number_of_years_into_future-1]
        rent_net_position = renter_deposit + renter_additional_investment
        # summary of the renter's position, text
        renter_net_position = f"After {number_of_years_into_future} years the renter's "
        renter_net_position += "investment of her/his deposit in the stock market "
        renter_net_position += f"will be worth £{renter_deposit:,.0f}"
        if renter_additional_investment > 0:
            renter_net_position += " plus an additional investment in the stock market "
            renter_net_position += f"of £{renter_additional_investment:,.0f}. "
            renter_net_position += "Therefore, the renter has a net position of "
            renter_net_position += f"£{rent_net_position:,.0f}."
        else:
            renter_net_position += f". The renter has a net position of £{rent_net_position:,.0f}."
        # summary of the buyer's position, calcs
        outstanding_mortgage = houseprice + stamp_duty_and_fees - deposit - \
            df.mortgage_capital_payments.sum()
        housevalue_in_future = houseprice * (1+growth_house/100)**10
        buyer_additional_investment = df.new_investment_buyer[number_of_years_into_future-1]
        buy_net_position = housevalue_in_future - outstanding_mortgage + buyer_additional_investment
        # summary of the buyer's position, text
        buyer_net_position = f"After {number_of_years_into_future} years the buyer "
        buyer_net_position += f"will have a house valued at £{housevalue_in_future:,.0f}"
        if buyer_additional_investment > 0:
            buyer_net_position += f", an outstanding mortgage of £{outstanding_mortgage:,.0f} "
            buyer_net_position += "and an stock market investment of "
            buyer_net_position += f"£{buyer_additional_investment:,.0f}. "
        else:
            buyer_net_position += f" and an outstanding mortgage of £{outstanding_mortgage:,.0f}. "
        buyer_net_position +=f"Therefore, the buyer has a net position of £{buy_net_position:,.0f}."
        # overall summary
        sum_net_position = buy_net_position - rent_net_position
        summary = "You will be "
        if sum_net_position > 0:
            summary += f"£{sum_net_position:,.0f} <span style='color:blue'>better"
            summary += " off buying</span> a place than renting."
            short_summary = f"Pro buy: £{sum_net_position:,.0f}"
        else:
            sum_net_position = abs(sum_net_position)
            summary += f"£{sum_net_position:,.0f} <span style='color:blue'>better"
            summary += " off renting</span> a place than buying."
            short_summary = f"Pro rent: £{sum_net_position:,.0f}"
        # create narrowed down data frame to present as detailed calcs
        df2 = df.filter(['year'], axis=1)
        df2 = df2.rename(columns={"year": "Year"})
        house_value = [houseprice*(1+growth_house/100)**i for i in range(1,number_of_years_into_future+1)]
        df2['Buyer: value of house'] = house_value
        temp_series=[]
        for i in range(1,number_of_years_into_future+1):
            if i == 1:
                temp_num = houseprice - deposit + stamp_duty_and_fees \
                    - df.mortgage_capital_payments[i-1]
                temp_series.append(temp_num)
            else:
                temp_num = temp_series[i-2]-df.mortgage_capital_payments[i-1]
                temp_series.append(temp_num)
        df2['Buyer: outstanding mortgage'] = temp_series
        df2['Buyer: FTSE 100 investment'] = df['new_investment_buyer']
        df2['Renter: FTSE 100 investment (deposit)'] = df['old_investment_deposit']
        df2['Renter: FTSE 100 investment'] = df['new_investment_renter']
        df2['Cash flow'] = df['renters_cashflow']
        # create notes for data table
        note_sdlt = f"Stamp Duty Land Tax (£{stamp_duty:,.0f}) and fees "
        note_sdlt += f"(£{other_fees:,.0f}) are included in the outstanding "
        note_sdlt += "mortgage amount"
        note_cash = "Cashflow is for the buyer and renter is the same eg, "
        note_cash += f"£{df2['Cash flow'][number_of_years_into_future-1]:,.0f} in "
        note_cash += f"the year {df2['Year'][number_of_years_into_future-1]}."
        # transform df to json object
        json_records = df2.to_json(orient ='records')
        table_data = []
        table_data = json.loads(json_records)
        return JsonResponse({'buyer_net_position': buyer_net_position,
                                'renter_net_position': renter_net_position,
                                'summary': summary,
                                'short_summary': short_summary,
                                'table_data': table_data,
                                'note_sdlt': note_sdlt,
                                'note_cash': note_cash,
                                'status': 200})

def login_page(request):
    if request.method == "POST":
        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request,username=username,password=password)
        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, 'buyorrent/login.html', {
                'message':'Invalid credentials',
            })
    else:
        return render(request, 'buyorrent/login.html')

def logout_page(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

def register(request):
    if request.method == "POST":
        # username and email
        username = request.POST['username']
        email = request.POST['email']
        # check passwords match
        password = request.POST['password']
        confirmation = request.POST['confirmation']
        if password != confirmation:
            return render(request, 'buyorrent/register.html', {
            'message':'Passwords must match'
            })
        # check if username is already used, create user account if not
        try:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
        except IntegrityError:
            return render(request, 'buyorrent/register.html', {
            'message':'Username already taken'
            })
        # log user in, route to index
        login(request, user)
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'buyorrent/register.html')
