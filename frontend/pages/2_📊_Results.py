import os

import requests
import streamlit as st
from streamlit.logger import get_logger
from utils import show_result

logger = get_logger(__name__)

BACKEND_HOST = os.environ.get("BACKEND_HOST", "127.0.0.1:80")


def render_results():
    st.write("## Results")

    res = requests.get(f"http://{BACKEND_HOST}/results")
    file_paths = res.json()

    def extract_job_id(file_path):
        dirname = os.path.dirname(file_path)
        return os.path.basename(dirname)

    options = list(map(extract_job_id, file_paths))

    if len(options) > 0:
        job_id = st.selectbox("Select Job ID", options)
        st.markdown("""---""")
        show_result(job_id)


render_results()
