import streamlit as st
import pandas as pd
import plotly.express as px
import random
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import numpy as np
import altair as alt
import pydeck as pdk

#URL = "https://data.cityofnewyork.us/api/views/h9gi-nx95/rows.csv?accessType=DOWNLOAD"
#URL = "~/Downloads/Motor_Vehicle_Collisions_-_Crashes.csv"
NUM_RECORDS = 1686115


st.title("Motor Vehicle Collisions in New York City")
st.markdown(
    """**This application is a Streamlit dashboard that can be used to analyze motor vehicle collisions in NYC** 🏙️🗽💥🚗. 
    \n If interested: 
    
    \n [See source data](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)
    \n [See source code](https://github.com/inespancorbo/Web-Apps/tree/master/Motor-Vehicle-Collisions-NYC)
    """)

st.markdown(
    """ Keep in mind the dataset has ~ 1.6 million motor vehicle collision records. 
    \n As such, computationally, this is expensive to display using Streamlit.
    \n Use the option below if you want the analysis to look at a subset of the ~ 1.6 million records. 
    Bear in mind some aspects of the analysis will be nonsensical if we are missing records.
    If you want the entire dataset please choose the maximum number on the slider 
    and be patient as visualizations load! Have fun 😊😊😊
    """)

nrows = st.slider('Select how many records:', 1, NUM_RECORDS, 1)

@st.cache(persist=True)
def load_data():
    skip = sorted(random.sample(range(1, NUM_RECORDS+1), NUM_RECORDS-nrows))
    data = pd.read_csv(URL, skiprows=skip)
    data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
    data.drop(data[data['LATITUDE'] == 0.0].index, inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis=1, inplace=True)

    # Date
    data['date'] = data['crash date'] + ' ' + data['crash time']
    data['date'] = pd.to_datetime(data['date'], format='%m/%d/%Y %H:%M')
    data['year'] = data['date'].dt.year
    data.drop(['crash date', 'crash time'], axis=1, inplace=True)
    data.drop(data[(data['date'].dt.year == 2012) | (data['date'].dt.year == 2020)].index, inplace=True)

    # Sorting by Date
    # data.sort_values('Date', ascending=True, inplace=True)
    # data.reset_index(drop=True, inplace=True)

    # Renaming certain columns
    old_names = list(data.columns[8:15])
    data.rename(columns=dict(zip(old_names, new_names)), inplace=True)

    return data


new_names = ['Number Of People Injured', 'Number Of People Killed',
             'Number Of Pedestrians Injured', 'Number Of Pedestrians Killed',
             'Number Of Cyclists Injured', 'Number Of Cyclists Killed',
             'Number Of Motorists Injured', 'Number Of Motorists Killed'
             ]

data = load_data()

# Create a check box to display raw data
if st.checkbox('Show Raw Data'):
    st.subheader('Raw Data')
    load_state = st.text('Loading Data ... ')
    st.write(data)
    load_state.text('Loading Completed!')

###############################################################################################################
st.header("Yearly Motor Vehicle Collision Injuries by Type")
option = st.selectbox('Choose a category:', new_names)
st.write(px.pie(data, values=str(option), names='year', title=str(option)))
###############################################################################################################

###############################################################################################################
st.header('Where are the most people injured/killed in NYC?')
option = st.selectbox('Select an option', ['Injured', 'Killed'])
gpd_data = pd.DataFrame(data.query(f'`Number Of People {option}` > 0').groupby(['latitude', 'longitude'])[
    f'Number Of People {option}'].sum()).reset_index()
max = gpd_data[f'Number Of People {option}'].max()
st.write('Number of People ', option, ' in Vehicle Collisions')
num_people = st.slider('', 0, int(max))
st.map(gpd_data.query(f'`Number Of People {option}` > @num_people')[['latitude', 'longitude']])
###############################################################################################################



