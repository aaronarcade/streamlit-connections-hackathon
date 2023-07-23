from json import JSONDecodeError
from pathlib import Path

from datetime import datetime
import numpy as np
import pandas as pd
import pydeck as pdk
import streamlit as st
import matplotlib.cm as cm
import matplotlib.colors as colors

from office365.sharepoint.client_context import ClientContext
from sharepoint_connection import SharepointConnection
from st_files_connection import FilesConnection


# Scaled colormap
def create_compressed_color_map(df, min_difference, max_difference):
    cmap = cm.get_cmap('RdYlGn')
    vmin = min_difference / 2
    vmax = max_difference / 3
    vcenter = (vmin + vmax) / 2  # Adjust vcenter to compress the color scale
    norm = colors.TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    colors_array = df['Difference'].apply(lambda x: [*np.array(cmap(norm(x)))[:-1] * 255, 100]).values
    return colors_array.tolist()


# Page setup
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

# Connect to sharepoint
conn = st.experimental_connection("duckdb", type=SharepointConnection, database='file.db')
file_url = st.secrets['file_relative_url'] + st.secrets['file_name']
df = conn.query(file_url)


# Clean data
df = df.fillna(0)


# User input
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

pitch = st.slider('Map Pitch', 0, 60, 40)


# Data transformation
df['Difference'] = df[to_date] - df[from_date]
df['Abs_Difference'] = df['Difference'].abs()


# Plot setup
min_difference = df['Difference'].min()
max_difference = df['Difference'].max()
max_magnitude = max([abs(max_difference), abs(min_difference)])

df['Color'] = create_compressed_color_map(df, min_difference, max_difference)

st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=35,
        longitude=-85,
        zoom=4,
        pitch=pitch,
    ),
    layers=[
        pdk.Layer(
            'ColumnLayer',
            data=df,
            get_position='[Longitude, Latitude]',
            radius=15000,
            elevation_scale=max_magnitude / 1000000,
            get_fill_color='Color',
            get_elevation='Abs_Difference',
            pickable=True,
            extruded=True,
            auto_highlight=True,
        ),
    ],
))