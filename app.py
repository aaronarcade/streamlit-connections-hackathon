from json import JSONDecodeError
import streamlit as st
from st_files_connection import FilesConnection
from pathlib import Path

st.set_page_config(
    page_title='Aaronarcade Dataset Explorer',
    page_icon='🏠'
)

"# 🏠 M365 GraphAPI Explorer"

"""
This app is a example of st.experimental_connection
with housing prices data from Streamlit.

View the full app code [here](https://github.com/aaronarcade/streamlit-connections-hackathon).
Here's the [data source](https://www.kaggle.com/datasets/claygendron/us-household-income-by-zip-code-2021-2011?resource=download) if you'd like to play with it too!
"""

# from duckdb_connection import DuckDBConnection
#
# conn = st.experimental_connection("duckdb", type=DuckDBConnection, database='file.db')
#
# df = conn.query("select * from integers")

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

from office365.sharepoint.client_context import ClientContext
import pandas as pd
import numpy as np
import io

ctx = ClientContext(st.secrets['url']).with_client_credentials(st.secrets['client_id'], st.secrets['client_secret'])
file_url = st.secrets['file_relative_url'] + st.secrets['file_name']
file = ctx.web.get_file_by_server_relative_url(file_url).get().execute_query()
file_content = file.read()
df = pd.read_csv(io.BytesIO(file_content))

st.write(df.head())



# ctx = ClientContext(app_settings['url']).with_client_credentials(app_settings['client_id'], app_settings['client_secret'])
# file_url = app_settings['file_relative_url'] + app_settings['file_name']
# file = ctx.web.get_file_by_server_relative_url(file_url).get().execute_query()
# file_content = file.read()
# df = pd.read_csv(io.BytesIO(file_content))

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
