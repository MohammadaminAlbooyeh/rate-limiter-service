import streamlit as st
import requests
from constants import CURRENCIES
from currency_convertor import get_exchange_rate, convert_currency


st.title(':dollar: Currency Converter')
st.markdown('''
This is a simple currency converter app built with Streamlit. Enter the amount you want to convert and the currency you want to convert from and to. 

The app will then calculate the converted amount and display it.
''')


base_currency = st.selectbox('From', CURRENCIES)
target_currency = st.selectbox('To', CURRENCIES)

amount = st.number_input('Amount', min_value=0.0, value=1.0)

if amount and base_currency and target_currency:
    exchange_rate = get_exchange_rate(base_currency, target_currency)
    

    if exchange_rate:
        converted_amount = convert_currency(amount, exchange_rate)
        st.success(f':white_check_mark: Exchange rate: {exchange_rate:.4f}')
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Base Currency", value=f'{amount:.2f} {base_currency}')
        col2.markdown(
    """
    <style>
    .flash-line {
        font-size: 34px;
        font-weight: bold;
        color: red;
        animation: flash 1s infinite;
        text-align: center;
        margin-left: -50px;  /* Shift to the left */
        margin-top: 20px;    /* Move down */
    }

    @keyframes flash {
        0% {opacity: 1;}
        50% {opacity: 0;}
        100% {opacity: 1;}
    }
    </style>

    <div class="flash-line">───➤</div>
    """,
    unsafe_allow_html=True
)
        col3.metric(label="Target Currency", value=f'{converted_amount:.2f} {target_currency}')
        
        

    else:
        st.error('Sorry, we could not find the exchange rate for the selected currencies.')
    
st.markdown('---')
st.markdown('### :grey_exclamation: About this Tools')
st.markdown('''
This is a simple currency converter app built with Streamlit. It uses the [exchangerate-api](https://www.exchangerate-api.com/) to get the exchange rate for the selected currencies. 

The app is built with Python and Streamlit.
''')


