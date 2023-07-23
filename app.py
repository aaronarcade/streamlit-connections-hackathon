from json import JSONDecodeError
from pathlib import Path

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

chart_data = df[['Longitude', 'Latitude']]

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
           'HexagonLayer',
           data=chart_data,
           get_position='[Longitude, Latitude]',
           radius=15000,
           elevation_scale=4,
           # elevation_scale=chart_data['2018-03-31'],
           elevation_range=[0, 1000],
           pickable=True,
           extruded=True,
        ),
    ],
))
