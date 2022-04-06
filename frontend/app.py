import logging
import json
import requests
import time
import os

import streamlit as st
import numpy as np

logger = logging.getLogger(__name__)

BACKEND_HOST = os.environ.get('BACKEND_HOST', '127.0.0.1:80')


def main():
    st.title('Demo with streamlit and fastapi')
    st.write('## Number Partitioning')

    numbers_size = st.number_input('Size of numbers', 1, 100, 50)
    if st.button('Generate'):
        st.session_state['numbers'] = np.random.randint(1, 100, size=numbers_size)

    if 'numbers' in st.session_state:
        st.bar_chart(st.session_state['numbers'])

    num_partitions = st.slider('Number of partitions', 2, 50)

    st.write('## Optimization')
    if 'numbers' in st.session_state and st.button('Submit'):
        data = dict(numbers=st.session_state['numbers'].tolist(), num_partitions=num_partitions)
        res = requests.post(f'http://{BACKEND_HOST}/optimize', data=json.dumps(data))
        res_json = res.json()
        st.write(res.text)
        st.session_state['job_id'] = res_json['job_id']

    if 'job_id' in st.session_state:
        st.write('## Result')

        # Refresh button
        if st.button('Refresh'):
            st.success('Refreshed')

        res = requests.get(f"http://{BACKEND_HOST}/results/{st.session_state['job_id']}")
        res_json = res.json()

        if res_json['status'] == 'COMPLETED':
            results = res_json['results']

            st.bar_chart([sum(v) for v in results.values()])
            st.write(results)

        # Alternative: progress bar
        # time_limit = 10
        # my_bar = st.progress(0)
        # for percent_complete in range(time_limit + 1):
        #     res = requests.get(f"http://{BACKEND_HOST}/results/{st.session_state['job_id']}")
        #     res_json = res.json()

        #     if res_json['status'] == 'COMPLETED':
        #         results = res_json['results']
        #         break

        #     time.sleep(1)
        #     my_bar.progress(percent_complete / time_limit)
        # else:
        #     st.error('No solutions')

        # if res_json['status'] == 'COMPLETED':
        #     if results is None:
        #         st.error('Not found feasible solutionss')
        #     else:
        #         st.bar_chart([sum(v) for v in results.values()])
        #         st.write(results)


if __name__ == '__main__':
    main()