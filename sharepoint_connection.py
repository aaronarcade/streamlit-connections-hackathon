import io
import pandas as pd

import streamlit as st
from streamlit.connections import ExperimentalBaseConnection
from streamlit.runtime.caching import cache_data

from office365.sharepoint.client_context import ClientContext


class SharepointConnection(ExperimentalBaseConnection[ClientContext]):
    """Basic st.experimental_connection implementation for SharePoint"""

    def _connect(self, **kwargs) -> ClientContext:
        sharepoint_url = st.secrets['sharepoint_url']
        client_id = st.secrets['client_id']
        client_secret = st.secrets['client_secret']

        ctx = ClientContext(sharepoint_url).with_client_credentials(client_id, client_secret)
        return ctx

    def cursor(self) -> ClientContext:
        if hasattr(self, "_instance") and self._instance:
            return self._instance

        self._instance = self._connect()
        return self._instance

    def query(self, query: str, ttl: int = 3600, **kwargs) -> pd.DataFrame:
        @cache_data(ttl=ttl)
        def _query(query: str, **kwargs) -> pd.DataFrame:
            cur = self.cursor()
            file = cur.web.get_file_by_server_relative_url(query).get().execute_query()
            file_content = file.read()

            df = pd.read_csv(io.BytesIO(file_content))
            return df

        return _query(query, **kwargs)