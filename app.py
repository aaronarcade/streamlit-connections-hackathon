from json import JSONDecodeError
from pathlib import Path

from datetime import datetime
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st

from office365.sharepoint.client_context import ClientContext
from sharepoint_connection import SharepointConnection
from st_files_connection import FilesConnection


st.set_page_config(
    page_title='Aaronarcade Dataset Explorer',
    page_icon='🏠'
)

"# 🏠 Office365 Sharepoint Explorer"

"""
This app is a example of st.experimental_connection
with housing prices data from Zillow.

View the full app code [here](https://github.com/aaronarcade/streamlit-connections-hackathon).
Here's the [data source](https://www.zillow.com/research/data/) if you'd like to play with it too!
"""

conn = st.experimental_connection("duckdb", type=SharepointConnection, database='file.db')

file_url = st.secrets['file_relative_url'] + st.secrets['file_name']
df = conn.query(file_url)

df = df.fillna(0)



col_a, col_b = st.columns(2)

with col_a:
    from_dates_array = [d for d in df.columns if d[0] == '2']
    from_date = st.selectbox(
    'From Date:',
    sorted(from_dates_array, reverse=False))

with col_b:
    to_dates_array = [d for d in from_dates_array if datetime.strptime(d, "%Y-%m-%d") > datetime.strptime(from_date, "%Y-%m-%d")]
    to_date = st.selectbox(
    'To Date:',
    sorted(to_dates_array, reverse=True))

df['Difference'] = df[to_date] - df[from_date]

chart_data = df[['Longitude', 'Latitude', 'Difference']]

min_elevation, max_elevation = chart_data['Difference'].min(), chart_data['Difference'].max()
max_difference = chart_data['Difference'].max()
min_difference = chart_data['Difference'].min()
# st.write(max_difference)
# st.write(min_difference)

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=35,
        longitude=-85,
        zoom=4,
        pitch=40,
    ),
    layers=[
        pdk.Layer(
           'ColumnLayer',
           data=chart_data,
           get_position='[Longitude, Latitude]',
           radius=15000,
           elevation_scale=max_difference / 1000000,
           # color_scale='Reds',
           get_fill_color='[Difference > 0 ? 0 : 255, 2018-03-31 > 0 ? 255 : 0, 0, 140]',
           # get_fill_color='[Difference > 0 ? 0 : 255, 0, 0, 150]',
           # get_fill_color=['2018-03-31', 0, 200, 140],
           get_elevation='Difference',
           pickable=True,
           extruded=True,
           auto_highlight=True,
        ),
    ],
))



# df['Difference'] = df[to_date] - df[from_date]
# df['Abs_Difference'] = abs(df[to_date] - df[from_date])
#
# chart_data = df[['Longitude', 'Latitude', 'Difference']]
#
# min_elevation, max_elevation = chart_data['Difference'].min(), chart_data['Difference'].max()
# max_difference = chart_data['Difference'].max()
# min_difference = chart_data['Difference'].min()
# max_magnitude = max(max_difference, min_difference)
# st.write(max_difference)
# st.write(min_difference)
#
# st.pydeck_chart(pdk.Deck(
#     map_style=None,
#     initial_view_state=pdk.ViewState(
#         latitude=35,
#         longitude=-85,
#         zoom=4,
#         pitch=40,
#     ),
#     layers=[
#         pdk.Layer(
#            'ColumnLayer',
#            data=chart_data,
#            get_position='[Longitude, Latitude]',
#            radius=15000,
#            elevation_scale=max_magnitude / 1000000,
#            # color_scale='Reds',
#            get_fill_color='[Difference > 0 ? 0 : 255, 2018-03-31 > 0 ? 255 : 0, 0, 140]',
#            # get_fill_color='[Difference > 0 ? 0 : 255, 0, 0, 150]',
#            # get_fill_color=['2018-03-31', 0, 200, 140],
#            get_elevation='Abs_Difference',
#            pickable=True,
#            extruded=True,
#            auto_highlight=True,
#         ),
#     ],
# ))
