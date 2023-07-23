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

import streamlit as st
import pydeck as pdk
import numpy as np
import matplotlib.cm as cm
import matplotlib.colors as colors

# Assuming you have already defined the DataFrame 'df'

df['Difference'] = df[to_date] - df[from_date]

# Create a new column for absolute difference
df['Abs_Difference'] = df['Difference'].abs()

# Create a custom color map with compressed scale using 'RdYlGn' colormap
def create_compressed_color_map(df, column_name):
    cmap = cm.get_cmap('RdYlGn')
    vmin = df[column_name].min() / 2
    vmax = df[column_name].max() / 3
    vcenter = (vmin + vmax) / 2  # Adjust vcenter to compress the color scale
    norm = colors.TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    colors_array = df[column_name].apply(lambda x: [*np.array(cmap(norm(x)))[:-1] * 255, 100]).values
    return colors_array

chart_data = df[['RegionName', 'Longitude', 'Latitude', 'Difference']]

max_difference = chart_data['Difference'].max()
min_difference = chart_data['Difference'].min()
max_magnitude = max([abs(max_difference), abs(min_difference)])

chart_data['Pos_Scale_Diff'] = chart_data['Difference'] / max_difference
chart_data['Neg_Scale_Diff'] = abs(chart_data['Difference']) / abs(min_difference)
chart_data['Abs_Difference'] = chart_data['Difference'].abs()

# st.dataframe(chart_data[['RegionName', 'Difference', 'Abs_Difference', 'Pos_Scale_Diff', 'Neg_Scale_Diff']])

pitch = st.slider('Map Pitch', 0, 60, 40)

# Call the function to create the compressed 'RdYlGn' color map
colors_array = create_compressed_color_map(chart_data, 'Difference')

# Assign the colors_array to the 'Color' column of the DataFrame
chart_data['Color'] = colors_array.tolist()

# Define the tooltip content using HTML with double curly braces for escaping
# tooltip_html = f"""
#     <div>
#         <h3>{RegionName}</h3>
#         <p><strong>Difference:</strong> {Difference}</p>
#         <p><strong>Absolute Difference:</strong> {Abs_Difference}</p>
#     </div>
# """
tooltip = {
    'html': '<b>Elevation Value:</b>',
    'style': {
        'color': 'white'
    }
}

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
            data=chart_data,
            get_position='[Longitude, Latitude]',
            radius=15000,
            elevation_scale=max_magnitude / 1000000,
            get_fill_color='Color',
            get_elevation='Abs_Difference',
            pickable=True,
            extruded=True,
            auto_highlight=True,
            tooltip=tooltip  # Enable tooltips
            # get_tooltip=tooltip_html,  # Use the defined tooltip content
        ),
    ],
))