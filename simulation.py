from simulate_profit import Market, Options
from typing import Union
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

table_col_names = ['Stock price', 'Price ratio %', 'Stock value', 'Net profit']

@st.cache
def simulate(model: Union[Market, Options], start: int, end: int, increments: int):

    sim_range = range(start, end, increments)

    sim_stock_price = [price for price in sim_range]
    sim_stock_price_ratio = [model.stock_price_ratio(price) for price in sim_range]
    sim_stock_value = [model.stock_value(price) for price in sim_range]
    sim_net_profit = [model.net_profit(value) for value in sim_stock_value]
   
    return sim_stock_price, sim_stock_price_ratio, sim_stock_value, sim_net_profit

@st.cache(show_spinner=False)
def merge_data(left, right, on, suffixes):
    full_data = pd.merge(left=left, right=right, on=on, suffixes=suffixes)
    return full_data


st.set_page_config(page_title='Call option vs market price', page_icon=None, layout='wide')

st.write('## Call option vs market price purchasing: a simulated comparison')
st.caption('by *dpollozhani*')

with st.form('Input parameters'):
    firstrow_col1, firstrow_col2 = st.beta_columns(2)
    secondrow_col1, secondrow_col2, secondrow_col3 = st.beta_columns(3)
    option_price = firstrow_col1.number_input('Option price', min_value=1, value=10)
    no_of_options = firstrow_col2.number_input('# of options', min_value=1, value=6000)
    initial_stock_price = secondrow_col1.number_input('Initial stock price', min_value=1, value=130)
    strike_price_factor = secondrow_col2.number_input('Strike price factor', min_value=1.1, max_value=1.5, value=1.25)
    price_increments = secondrow_col3.number_input('Price increments', min_value=1, max_value=5, value=1)
    calculate = st.form_submit_button('Calculate')

options = Options(option_price, no_of_options, initial_stock_price, strike_price_factor)
market = Market(option_price, no_of_options, initial_stock_price, strike_price_factor)

range_col1, range_col2 = st.beta_columns(2)
selected_min = range_col1.slider('Lower bound', min_value=50, max_value=initial_stock_price)
selected_max = range_col2.slider('Upper bound', min_value=initial_stock_price+1, max_value=initial_stock_price*3, value=initial_stock_price*2)

option_data = simulate(model=options, start=selected_min, end=selected_max, increments=price_increments)
simulated_options = Options.to_table(option_data, table_col_names)
market_data = simulate(model=market, start=selected_min, end=selected_max, increments=price_increments)
simulated_market = Market.to_table(market_data, table_col_names)

left = simulated_options[['Stock price', 'Price ratio %', 'Stock value', 'Net profit']]
right = simulated_market[['Stock price', 'Stock value', 'Net profit']]
full_data = merge_data(left, right, on='Stock price', suffixes=(" otions", " market"))

plot_dict = {
   'Market net profit': simulated_market.set_index('Stock price')['Net profit'],
   'Options net profit': simulated_options.set_index('Stock price')['Net profit'],
   }

with st.beta_container():
    chart_col1, chart_col2 = st.beta_columns((1,8))
    chart_type = chart_col1.radio('Chart type', options=['area', 'line'])
    chart_height = 500
    if chart_type == 'area':
        chart_col2.area_chart(plot_dict, height=chart_height)
    else:
        chart_col2.line_chart(plot_dict, height=chart_height)
    chart_col2.caption('Simulated net profit for future (three years) stock prices, with LTIP call options compared to direct market purchases')

with st.beta_expander('Show data:'):
    _, data_col, _ = st.beta_columns((1,10,1))
    data_col.write(full_data)

st.write(''' ### What do we learn?
    This simple analysis shows the difference in risk and reward between purchasing call options via your company and going directly to the market.
    
    Call options, if part of a reasonable programme design, always start off at a loss (negative net profit) at the time of purchase,
    with a break even ocurring at a certain point beyond the predetermined strike factor. However, if the stock develops sufficiently enough,
    the net profit rapidly outperforms the market profit for every unit increase. 
    
    Given that there is a good outlook for the company during the call option programme window,
    and there are feasible financing alternatives for purchasing the resulting shares upon strike, call options are very much worth a consideration.
    
    It might also be good for company spirit :sunglasses:'''
    )
