import json
import os

import numpy as np
import requests
import streamlit as st
from streamlit.logger import get_logger
from utils import show_result

logger = get_logger(__name__)


BACKEND_HOST = os.environ.get("BACKEND_HOST", "127.0.0.1:80")


def render_optimize():
    st.write("## Number Partitioning")

    numbers_size = st.slider("Size of numbers", 1, 100, 50)
    if st.button("Generate"):
        st.session_state["numbers"] = np.random.randint(1, 100, size=numbers_size)

    if "numbers" in st.session_state:
        st.bar_chart(st.session_state["numbers"])

    num_partitions = st.slider("Number of partitions", 2, 50)

    if "numbers" in st.session_state:
        st.write("## Optimization")

        if st.button("Submit"):
            data = dict(
                numbers=st.session_state["numbers"].tolist(),
                num_partitions=num_partitions,
            )
            res = requests.post(
                f"http://{BACKEND_HOST}/optimize", data=json.dumps(data)
            )
            res_json = res.json()
            st.write(res.text)
            st.session_state["job_id"] = res_json["job_id"]

    if "job_id" in st.session_state:
        st.write("## Results")

        if st.button("Refresh"):
            st.success("Refreshed")

        show_result(st.session_state["job_id"])


render_optimize()
