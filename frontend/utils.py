import json
import os

import requests
import streamlit as st
from streamlit.logger import get_logger

logger = get_logger(__name__)

BACKEND_HOST = os.environ.get("BACKEND_HOST", "127.0.0.1:80")


def show_result(job_id):
    res = requests.get(f"http://{BACKEND_HOST}/result/{job_id}")
    res_json = res.json()

    if res_json.get("status", None) == "COMPLETED":
        results = res_json["results"]["solutions"]

        if results is None:
            st.error("Not found feasible solutionss")
        else:
            solution_options = [f"Solution {i}" for i in range(len(results))]

            options = st.multiselect(
                "Select solutions", solution_options, [solution_options[0]]
            )
            if len(options) > 0:
                columns = st.columns(len(options))
                indices = [solution_options.index(option) for option in options]

                for i, index in enumerate(indices):
                    result = results[index]

                    with columns[i]:
                        st.write(f"**{options[i]}**")
                        st.metric("Standard deviation", result["evaluation"]["std"])
                        number_sums = [sum(v) for v in result["partition"].values()]
                        st.bar_chart(number_sums)

                selected_results = {options[i]: results[index] for index in indices}

                st.download_button(
                    label="Download these solutions as JSON",
                    data=json.dumps(selected_results),
                    file_name=f"solution-{job_id}.json",
                    mime="application/json",
                )
