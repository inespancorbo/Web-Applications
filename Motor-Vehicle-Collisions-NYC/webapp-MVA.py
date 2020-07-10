import streamlit as st
import pandas as pd
import numpy as np
import random
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import altair as alt
import pydeck as pdk

URL = "https://data.cityofnewyork.us/api/views/h9gi-nx95/rows.csv?accessType=DOWNLOAD"
# URL = "~/Downloads/Motor_Vehicle_Collisions_-_Crashes.csv"
NUM_RECORDS = 1686115

st.title("Motor Vehicle Collisions in New York City")
st.markdown(
    """**This application is a Streamlit dashboard that can be used to analyze motor vehicle collisions in NYC** 🏙️🗽💥🚗. 
    \n If interested: 
    \n [See source data](https://data.cityofnewyork.us/Public-Safety/Motor-Vehicle-Collisions-Crashes/h9gi-nx95)
    \n [See source code](https://github.com/inespancorbo/Web-Applications/blob/master/Motor-Vehicle-Collisions-NYC/webapp-MVA.py)
    """)

st.markdown(
    """ Keep in mind the dataset has ~ 1.6 million motor vehicle collision records. 
    \n As such, computationally, this is expensive to display using Streamlit.
    \n Use the option below if you want the analysis to look at a random sample of the ~ 1.6 million records. 
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
    old_names = list(data.columns[8:16])
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

# Types
###############################################################################################################
st.header("Yearly Motor Vehicle Collision Injuries by Type")
option = st.selectbox('Choose a category:', new_names)
st.write(px.pie(data, values=str(option), names='year', title=str(option)))
###############################################################################################################

# 2D map
###############################################################################################################
st.header('Where are the most people injured/killed in NYC over time?')
option = st.selectbox('Select an option', ['Injured', 'Killed'])
gpd_data = pd.DataFrame(data.query(f'`Number Of People {option}` > 0').groupby(['latitude', 'longitude'])[
    f'Number Of People {option}'].sum()).reset_index()
max = gpd_data[f'Number Of People {option}'].max()
st.write('Number of People ', option, ' in Vehicle Collisions')
if max > 1:
    num_people = st.slider('', 1, int(max))
else:
    num_people = 1

gpd_data = gpd_data.query(f'`Number Of People {option}` >= @num_people')[['latitude', 'longitude']]
st.write(pdk.Deck(
    map_style=f'mapbox://styles/mapbox/dark-v9',
    initial_view_state={
        'latitude': np.average(data['latitude']),
        'longitude': np.average(data['longitude']),
        'zoom': 9,
        'pitch': 40,
    },
    layers=[
        pdk.Layer(
            #"ScatterplotLayer",
            "HeatmapLayer",
            data=gpd_data,
            get_position=['longitude', 'latitude'],
            auto_highlight=True,
            radius=100,
            pickable=True,
        ),
    ],
))
###############################################################################################################

# 3D map
###############################################################################################################
st.header('How many collisions occur during a given time of day?')
hour = st.slider('Hour to look at:', 0, 23)
year = st.selectbox('Select a year:', [2013, 2014, 2015, 2016, 2017, 2018, 2019, "All Years"])
month = st.slider('Select a month (0 for all months):', 0, 12)
hr_data = data[(data['date'].dt.hour == hour)]

if year != 'All Years':
    hr_data = hr_data[hr_data['year'] == year]
if month != 0:
    hr_data = hr_data[hr_data['date'].dt.month == month]

st.markdown('Vehicle Collisions between %i:00 and %i:00' % (hour, (hour + 1) % 24))

if hour in range(7, 19):
    color = 'light'
else:
    color = 'dark'

st.write(pdk.Deck(
    map_style=f'mapbox://styles/mapbox/{color}-v9',
    initial_view_state={
        'latitude': np.average(data['latitude']),
        'longitude': np.average(data['longitude']),
        'zoom': 9,
        'pitch': 40,
    },
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=hr_data[['date', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            auto_highlight=True,
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=3,
            elevation_range=[0, 3000],
        ),
    ],
))

st.subheader('Breakdown by minute between %i:00 and %i:00' % (hour, (hour + 1) % 24))
min_data = hr_data[(hr_data['date'].dt.hour >= hour) & (hr_data['date'].dt.hour < (hour + 1))]
hist = np.histogram(min_data['date'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'])
st.write(fig)
###############################################################################################################

# Dangerous streets
###############################################################################################################
st.header("Top 5 streets with the most injured/killed people by type, over time")
option = st.selectbox('Select an option:', ['Injured', 'Killed'])
type = st.selectbox('Select an option:', ['Pedestrians', 'Cyclists', 'Motorists', 'All'])

if type != 'All':
    st_data = data.dropna(subset=['on street name']).query(f'`Number Of {type} {option}` > 0').groupby(
        ['on street name'])[f'Number Of {type} {option}'].sum().sort_values(ascending=False)
else:
    st_data = data.dropna(subset=['on street name']).query(f'`Number Of People {option}` > 0').groupby(
        ['on street name'])[f'Number Of People {option}'].sum().sort_values(ascending=False)

st.write(st_data[0:5])
###############################################################################################################

