import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# creating a title for streamlit
st.title("Crypto Currency Price Chart")

# this function takes 3 parameters
# symbol ===> like "BTC-USD"
def get_crypto_data(symbol, startdate, enddate):
    crp = yf.Ticker(symbol)                                         # creates a ticker object to fetch data later
    df = crp.history(start=startdate, end=enddate, interval='1d')   # fetches price data between given dates
    return df[['Open', 'High', 'Low', 'Close', 'Volume']]           # filtering out column we dont need

# adding a menu named 'setting' on the side
st.sidebar.header('Settings')

# -----------------------------------------------------------------------------------------------
# ~~~~~~~CRYPTO CURRENCY SELECT BOX~~~~~~~

# creating a dictionary of currecies with their symbols
CRYPTO_MAP = {
    "Bitcoin" : "BTC-USD",
    "Ethereum" : "ETH-USD",
    "Dogecoin" : "DOGE-USD",
    "Tron" : "TRX-USD",
    "Tether" : "USDT-USD",
    "Shiba" : "SHIB-USD",
    "Pepe" : "PEPE24478-USD"
}

# adds a select box to the setting
# works like a drop down menu ==> you click on it, it shows available choices to make 
crypto_currency = st.sidebar.selectbox(
    "Select Crypto Currency",           # select box name
    options=list(CRYPTO_MAP.keys()),    # available choices for user
    index=0                             # default choice
)

# -----------------------------------------------------------------------------------------------
# ~~~~~~~CHART TYPES SELECT BOX~~~~~~~

# creating a dictionary for different charts
CHART_TYPES = {
    "Candlestick" : "candlestick",
    "Line" : "line",
}

# adds another select box to the setting menu for different charts
chart_type = st.sidebar.selectbox(
    "Select Chart Type",                # select box name
    options=list(CHART_TYPES.keys()),   # available choices for user 
    index=0                             # default selected choice
)

# -----------------------------------------------------------------------------------------------
# ~~~~~~~DATE RANGE SELECT BOX~~~~~~~

# creating a dictionary for predefined date ranges
DAYS_MAP = {
    '7 days' : 7, 
    '30 days' : 30, 
    '60 days' : 60, 
    '90 days' : 90, 
    '180 days' : 180, 
    '1 year' : 365
}

# creating a select box for 2 different date types (predefined and custom)
time_period = st.sidebar.selectbox(
    'Select Time Range Type',
    options=['Predefined Period', 'Custom Range'],
    index = 0
)

# if user selects predefined add another select box name 'Time Period' 
if time_period == 'Predefined Period':
    selected_period = st.sidebar.selectbox(
        'Time Period',
        options=list(DAYS_MAP.keys()),
        index=1
    )
    selected_days = DAYS_MAP[selected_period]              # fetches corresponding values from the DAYS_MAP
    enddate = datetime.now()                               # calculate end date which is now
    startdate = enddate - timedelta(days=selected_days)    # calculating start date by subtracting selected date from today's date
    time_label = f"Last {selected_period}"

# if user selects custom date 
else:
    # create 2 side by side columns (start date, end date)
    col1, col2 = st.sidebar.columns(2)
    with col1:
        # st.date_input creates a widget to select custom date
        # default start date is 30 days ago
        startdate = st.date_input("Start Date", value=datetime.now() - timedelta(days=30))
    with col2:
        enddate = st.date_input("end Date", value=datetime.now())


    if startdate > enddate:
        st.sidebar.error("Error: Invalid Date Range!!")
        st.stop()

    # format the dates with 'strftime' to the given format 
    time_label = f"{startdate.strftime('%Y-%m-%d')} to {enddate.strftime('%Y-%m-%d')}"

# -----------------------------------------------------------------------------------------------

# fethces selected crypto coin data with the given date range
# adds an extra day to include final day's data
data = get_crypto_data(CRYPTO_MAP[crypto_currency], startdate, enddate + timedelta(days=1))

# -----------------------------------------------------------------------------------------------

# calculates stuff and rounds them to 2 decimals
curr_price = round(data['Close'].iloc[-1], 2)
start_price = round(data['Close'].iloc[0], 2)
highest = round(data['High'].max(), 2)
lowest = round(data['Low'].min(), 2)
vol = data['Volume'].mean()

# adds 4 columns on top of  the screen
# ',' adds commas
# '.2' specifiy 2 detimal places
# 'f' tells it's a float number
col1, col2, col3, col4 = st.columns(4)
col1.metric("Current Price", f"${curr_price:,.2f}")
col2.metric("Starting Price", f"${start_price:,.2f}")
col3.metric("Period High", f"${highest:,.2f}", f"{(highest - start_price)/start_price*100:+.2f}%")
col4.metric("Period Low", f"${lowest:,.2f}", f"{(lowest - start_price)/start_price*100:+.2f}%")

# -----------------------------------------------------------------------------------------------

# create an empty plot
fig1 = go.Figure()

# if user chooses candlestick in 'Chart Type Select Box' create the chart
# add_trace() is used to add new set of data to fig1
if CHART_TYPES[chart_type] == "candlestick":
    fig1.add_trace(go.Candlestick(
        x = data.index,
        open = data['Open'],
        high = data['High'],
        low = data['Low'],
        close = data['Close'],
        increasing_line_color = 'green',
        decreasing_line_color = 'red'
    ))

elif CHART_TYPES[chart_type] == "line":
    fig1.add_trace(go.Scatter(
        x = data.index,
        y = data['Close'],
        mode = 'lines',
        line = dict(color='blue', width=3)
    ))


fig1.update_layout(
    title=f'{crypto_currency} Price ({time_label}) - {chart_type} Chart',
    xaxis_title='Date',
    yaxis_title='Price (USD)',
    xaxis_rangeslider_visible=False    # hides range slider
)

# -----------------------------------------------------------------------------------------------

# create the second empty plot for volume chart(amount of trading activity)
fig2 = go.Figure()

# 
fig2.add_trace(go.Bar(
    x=data.index,
    y=data['Volume'],
    name='Volume',
    marker_color='lightblue'
))

fig2.update_layout(
    title=f'{crypto_currency} Trading Volume ({time_label})',
    xaxis_title='Date',
    yaxis_title='Volume',
    height=300
)

# -----------------------------------------------------------------------------------------------

# plot out figures on streamlit
st.plotly_chart(fig1)
st.plotly_chart(fig2)
