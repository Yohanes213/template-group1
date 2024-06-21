import streamlit as st
from datetime import datetime
import requests
from kafka import KafkaConsumer
import json

with st.sidebar:

    options=['BTC']

    selected_options = st.selectbox("Select Strategy", options)
    start_date = st.date_input("Select Start Date", datetime.now())
    end_date = st.date_input("Select End Date", datetime.now())

    if st.button('Send Request'):

        data = {'Startegy': selected_options,
                'Start date': start_date.strftime("%Y-%m-%d"),
                'End date': end_date.strftime("%Y-%m-%d")
                }
        
        response = requests.post("http://127.0.0.1:5000/process", json=data)

        if response.status_code == 200:
            st.write("Backend response: ",response.json())

        else:
            st.write("Failed")



consumer = KafkaConsumer(
    'metrics',
    bootstrap_servers='localhost:9092',
    #auto_offset_reset = 'earliest',
    # enable_auto_commit=True,
    # group_id='my-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)


for message in consumer:
    st.write(message.value)