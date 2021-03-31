import streamlit as st
from datetime import date
import datetime

import yfinance as yf
from fbprophet import Prophet
from fbprophet.plot import plot_plotly

from plotly import graph_objs as go

import pandas as pd

corona = pd.DataFrame({
    'holiday': 'corona',
    'ds': pd.to_datetime(['2020-03-09', '2020-03-10', '2020-03-11',
                          '2020-03-12','2020-03-13','2020-03-14',
                          '2020-03-15','2020-03-16','2020-03-17',])
    })

START_init = "2007-01-01"
START = st.sidebar.date_input('Startdatum', datetime.datetime.strptime(START_init, '%Y-%m-%d'))

TODAY = date.today().strftime("%Y-%m-%d")

st.title('Forecast APP mit Streamlit')

stocks = ('APC.DE', #Apple
          'BAS.DE', #BASF
          'DAI.DE', #Daimler
          'FRA.DE', #Fraport
          'IFX.DE', #Infineon
          'MSF.DE', #Microsoft
          'R6C.DE', #Shell
          'SAP.DE', #SAP
          '3V64.DE',    #VISA
          'EXXT.DE',    #IShares Nasdaq 100 ETF
          'XDWL.DE',    #Xtrackers MSCI World
          'DBXE.DE',    #Xtrackers Eurostoxx 50 ETF
          'TL0.DE',     #Tesla, aber nicht im Portfolio
          'FB2A.DE',    #FB, aber nicht im Portfolio
          )   

## Funcs
#Get and cache raw data
@st.cache
def load_data(Aktie):
    data = yf.download(Aktie, START, TODAY)
    data.reset_index(inplace=True)
    return data

def plot_raw_data(daten):
    fig = go.Figure()
    # fig.add_trace(go.Scatter(x = data['Date'],
    #                          y = data['Open'], 
    #                          name = 'stock_open'))
    if hasattr(meine_stocks['Close'], 'columns'):
        for cols in daten['Close'].columns:
            fig.add_trace(go.Scatter(x = daten['Date'],
                                     y = daten['Close'][cols], 
                                     name = cols))
    else:
        fig.add_trace(go.Scatter(x = daten['Date'],
                                 y = daten['Open'], 
                                 name = 'stock_open'))
        
    fig.layout.update(title_text = 'Data with Rangeslider', xaxis_rangeslider_visible = True)
    return fig
    #st.plotly_chart(fig)
    
    
## Sidebar

sel_stocks = st.sidebar.multiselect('Meine Aktien', stocks, default=stocks[-2:-1])
selected_stock = st.sidebar.selectbox('Aktie für Forecast auswählen', stocks)

n_multi_months = 1
n_multi_years = 1
#if n_days == 30:
n_multi_months = st.sidebar.slider('Weeks',1,52)
    
if n_multi_months == 52:
    n_multi_years = st.sidebar.slider('Years',1,5)

# Aktienkurse anzeigen
app_status = st.text('Loading data...')
meine_stocks = load_data(sel_stocks)
app_status.write('Loading done!')

#st.write(meine_stocks.tail())
fig_aktien = plot_raw_data(meine_stocks)
st.plotly_chart(fig_aktien)


# Forecast machen

app_status = st.text('Loading data...')
data = load_data(selected_stock)
app_status.write('Loading done!')

# st.subheader('Raw data')
# st.write(data.tail())

#n_months = st.slider('Months of Prediction',1,12)
#n_days = st.slider('Days of Prediction',1,30)


    
    
#period_days = n_months / 12 * 365
period_days = n_multi_months * n_multi_years

#Plot raw data
# def plot_raw_data():
#     fig = go.Figure()
#     # fig.add_trace(go.Scatter(x = data['Date'],
#     #                          y = data['Open'], 
#     #                          name = 'stock_open'))
#     fig.add_trace(go.Scatter(x = data['Date'],
#                              y = data['Close'], 
#                              name = 'stock_close'))
#     fig.layout.update(title_text = 'Data with Rangeslider', xaxis_rangeslider_visible = True)
#     st.plotly_chart(fig)

# st.subheader('Plot of raw data')
# fig_raw = plot_raw_data(data)
# st.plotly_chart(fig_raw)

#Predict Aktienkurs

df_train = data[['Date', 'Close']]
df_train = df_train.rename(columns = {'Date': 'ds', 'Close': 'y'})

m = Prophet(holidays=corona)
m.add_country_holidays(country_name='DE')
m.fit(df_train)

#future = m.make_future_dataframe(periods=period_days)
future = m.make_future_dataframe(periods=period_days, freq="W")
forecast = m.predict(future)

#Plot Forecast

# st.subheader('Forecast')
# st.write(forecast.tail())

st.subheader(f'Plot Forecast for {period_days} weeks')
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)

st.subheader('Forecast components')
fig2 = m.plot_components(forecast)
st.write(fig2)
