from json import JSONDecodeError
import streamlit as st
from st_files_connection import FilesConnection
from pathlib import Path
from utils import get_files

st.set_page_config(
    page_title='Aaronarcade Dataset Explorer',
    page_icon='🏠'
)

"# 🏠 Aaronarcade Dataset Explorer"

"""
This app is a example of st.experimental_connection
with housing prices data from Streamlit.

View the full app code [here](https://github.com/aaronarcade/streamlit-connections-hackathon).
Here's the [data source](https://data-editor.streamlit.app/) if you'd like to play with it too!
"""

from duckdb_connection import DuckDBConnection

conn = st.experimental_connection("duckdb", type=DuckDBConnection, database='file.db')

df = conn.query("select * from integers")
st.dataframe(df)
