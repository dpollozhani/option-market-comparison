from simulate_profit import Market, Options
import pandas as pd
import numpy as np
import altair as alt
import streamlit as st

table_col_names = ['Stock price', 'Price ratio %', 'Stock value', 'Net profit']

@st.cache
def simulate(model, start: int, end: int, increments: int):

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

@st.cache
def break_even(simulated_data) -> dict:
    data_slice = simulated_data[simulated_data['Net profit options'] >= 0]
    if len(data_slice.index) > 0:
        lowest_positive_idx = min(data_slice.index)
        return simulated_data.iloc[lowest_positive_idx, :][['Stock price', 'Price ratio %']].to_dict()
    return {'Stock price': 'Range too limited', 'Price ratio %': '-'}

@st.cache
def better_than_market(simulated_data) -> dict:
    data_slice = simulated_data[simulated_data['Net profit options'] > simulated_data['Net profit market']]
    if len(data_slice.index) > 0:
        lowest_better_idx = min(data_slice.index)
        return simulated_data.iloc[lowest_better_idx, :][['Stock price', 'Price ratio %']].to_dict()
    return {'Stock price': 'Range too limited', 'Price ratio %': '-'}

st.set_page_config(page_title='Call option vs market price', page_icon=None, layout='wide')

st.write('## Call option vs market price purchasing: a simulated comparison')
st.caption('by *dpollozhani*')

with st.form('Input parameters'):
    firstrow_col1, firstrow_col2, firstrow_col3 = st.beta_columns(3)
    secondrow_col1, secondrow_col2, secondrow_col3 = st.beta_columns(3)
    
    option_price = firstrow_col1.number_input('Option price', min_value=1, value=10)
    no_of_options = firstrow_col2.number_input('# of options', min_value=1, value=6000)
    subsidy = firstrow_col3.number_input('Subsidy (of which half is assumed taxable):', min_value=0.0, max_value=1.0, value=0.5)
    
    initial_stock_price = secondrow_col1.number_input('Initial stock price', min_value=1, value=130)
    strike_price_factor = secondrow_col2.number_input('Strike price factor', min_value=1.1, max_value=1.5, value=1.25)
    price_increments = secondrow_col3.number_input('Price increments', min_value=1, max_value=5, value=1)
    
    calculate = st.form_submit_button('Calculate')

options = Options(option_price, no_of_options, subsidy, initial_stock_price, strike_price_factor)
market = Market(option_price, no_of_options, subsidy, initial_stock_price, strike_price_factor)

attributes = st.beta_columns(4)
attributes[0].write(f'**Initial investment (option cost)**: {options.option_cost}')
attributes[1].write(f'**Strike price**: {options.strike_price}')
attributes[2].write(f'**Stock cost at strike**: {options.stock_cost_at_strike}')
attributes[3].write(f'**Number of stocks (corresponding to {options.no_of_options} options)**: {round(market.no_of_stocks)}')

range_col1, range_col2 = st.beta_columns(2)
selected_min = range_col1.slider('Lower bound', min_value=50, max_value=initial_stock_price)
selected_max = range_col2.slider('Upper bound', min_value=initial_stock_price+1, max_value=initial_stock_price*3, value=initial_stock_price*2)

option_data = simulate(model=options, start=selected_min, end=selected_max, increments=price_increments)
simulated_options = Options.to_table(option_data, table_col_names)
market_data = simulate(model=market, start=selected_min, end=selected_max, increments=price_increments)
simulated_market = Market.to_table(market_data, table_col_names)

left = simulated_options[['Stock price', 'Price ratio %', 'Stock value', 'Net profit']]
right = simulated_market[['Stock price', 'Stock value', 'Net profit']]
full_data = merge_data(left, right, on='Stock price', suffixes=(" options", " market"))

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
    chart_col2.caption('Simulated net profit for future (three years) stock prices, with call options compared to direct market purchases')

    break_even_price = break_even(full_data)
    better_than_market_price = better_than_market(full_data)

    below_chart = st.beta_columns(2)
    below_chart[0].markdown(f'**Break even for options**:<br> Stock price: {break_even_price["Stock price"]} ({break_even_price["Price ratio %"]}%)', unsafe_allow_html=True)
    below_chart[1].markdown(f'**Options better than market**:<br> Stock price: {better_than_market_price["Stock price"]} ({better_than_market_price["Price ratio %"]}%)', unsafe_allow_html=True)
    
with st.beta_expander('Show data:'):
    _, data_col, _ = st.beta_columns((1,10,1))
    data_col.write(full_data)

st.markdown(''' ### What do we learn? :bulb:
    This simple analysis shows the difference in risk and reward between purchasing call options via your company and going directly to the market.
    
    Call options, if part of a reasonable programme design, always start off at a projected loss on prices close to the initial stock price, due to the fact that the resulting stock will only be available to purchase at strike price.<br>
    Break even ocurrs at a certain point beyond the predetermined strike factor. However, if the stock develops sufficiently enough,
    the options net profit rapidly outperforms the market profit for every unit increase. 

    Note, that one <strike>would</strike> should only buy the resulting stocks it the stock price is *above* break even, or better yet, above the "better-than-market" threshold.<br>
    In other words, with the call options, you **never** have to lose more than the initial investment, as opposed to purchasing directly from the market.
    
    Given that there is a good outlook for the company during the call option programme window,
    and there are feasible financing alternatives for purchasing the resulting shares upon strike, call options are very much worth a consideration.
    
    It might also be good for company spirit :sunglasses:''',
    unsafe_allow_html=True
    )
