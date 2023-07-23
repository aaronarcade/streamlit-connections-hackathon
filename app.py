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
    vcenter = (min_difference + max_difference) / 4
    vmax = max_difference / 2
    
    norm = colors.TwoSlopeNorm(vmin=vmin, vcenter=vcenter, vmax=vmax)
    colors_array = df['Difference'].apply(lambda x: [*np.array(cmap(norm(x)))[:-1] * 255, 200]).values
    return colors_array.tolist()
    
# Formats for tooltip
def format_difference(difference):
    if difference > 0:
        return '+$' + '{:,.0f}'.format(difference)
    else:
        return '-$' + '{:,.0f}'.format(abs(difference))
        
def format_percentage(value):
    if value >= 0:
        return "+{:.2f}%".format(abs(value) * 100)
    else:
        return "-{:.2f}%".format(abs(value) * 100)
    
    
# Session state vars
if 'pitch' not in st.session_state:
    st.session_state['pitch'] = 40


# Page setup
st.set_page_config(
    page_title='Sharepoint Connection',
    page_icon='🏠'
)

"# 🏠 Sharepoint Connection"

"""
This app is an example of st.experimental_connection
with housing prices data from Zillow.

View the full app code 
[here](https://github.com/aaronarcade/streamlit-connections-hackathon).
Here's the [sales data source](https://www.zillow.com/research/data/) 
if you'd like to play with it too!
"""

site_url = st.secrets['sharepoint_url']
file_path =  st.secrets['file_relative_url'] + st.secrets['file_name']

# st.caption("It's as easy as:")
with st.echo():
    ## It's as simple as:
    conn = st.experimental_connection("sp", type=SharepointConnection, site=site_url)
    df = conn.query(file_path) 


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

with st.expander("Filters"):
    states = np.sort([s for s in df['StateName'].drop_duplicates() if s != 0])
    selected_states = st.multiselect(
        'States Selected',
        states,
        states,)
    
# Data transformation
if selected_states == []:
    st.warning("Please select a state")
    
else:
    df = df[df['StateName'].isin(selected_states)]
    df['Difference'] = df[to_date] - df[from_date]
    df['Pct_Difference'] = (df[to_date]/df[from_date])-1
    df['Abs_Difference'] = df['Difference'].abs()


    # Plot setup
    start_date = datetime.strptime(from_date, '%Y-%m-%d')
    end_date = datetime.strptime(to_date, '%Y-%m-%d')
    time_difference = end_date - start_date
    years = time_difference.days / 365
    
    df['Formatted_Difference'] = df['Difference'].apply(format_difference)
    df['Formatted_Pct_Difference'] = df['Pct_Difference'].apply(format_percentage)
    df['Formatted_Annual_Difference'] = (df['Difference']/years).apply(format_difference)
    df['Formatted_Annual_Pct_Difference'] = (df['Pct_Difference']/years).apply(format_percentage)
    
    min_difference = df['Difference'].min()
    max_difference = df['Difference'].max()
    max_magnitude = max([abs(max_difference), abs(min_difference)])

    df['Color'] = create_compressed_color_map(df, min_difference, max_difference)
    
    st.subheader("Pydeck Column Chart")
    height = 300

    chart = pdk.Deck(
    height=height,
        map_style='light',
        initial_view_state=pdk.ViewState(
            latitude=35,
            longitude=-85,
            zoom=3.5,
            pitch=st.session_state.pitch,
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
        tooltip = {
            'html': f"""
                <b>{{RegionName}}</b> </br>
                <table border="1">
        <tr>
            <td><b>Total</b></td>
            <td><b>Annual</b></td>
        </tr>
        <tr>
            <td>{{Formatted_Difference}}</td>
            <td>{{Formatted_Annual_Difference}}</td>
        </tr>
        <tr>
            <td> {{Formatted_Pct_Difference}}</td>
            <td>{{Formatted_Annual_Pct_Difference}}</td>
        </tr>
    </table>
            """,
            'style': {
                'color': 'white'
            }
        }
    )
    
    st.components.v1.html(chart.to_html(as_string=True), height=height)
    
    
    pitch = st.slider('Map Tilt', 0, 60, 40)
    if pitch != st.session_state['pitch']:
        st.session_state['pitch'] = pitch
        st.experimental_rerun()