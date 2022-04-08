import logging
import json
import requests
import os

import streamlit as st
import numpy as np

logger = logging.getLogger(__name__)

BACKEND_HOST = os.environ.get('BACKEND_HOST', '127.0.0.1:80')


def show_result(job_id):
    res = requests.get(f"http://{BACKEND_HOST}/result/{job_id}")
    res_json = res.json()

    if res_json['status'] == 'COMPLETED':
        results = res_json['results']['solutions']

        if results is None:
            st.error('Not found feasible solutionss')
        else:
            solution_options = [f'Solution {i}' for i in range(len(results))]

            options = st.multiselect('Select solutions', solution_options, [solution_options[0]])
            if len(options) > 0:
                columns = st.columns(len(options))
                indices = [solution_options.index(option) for option in options]

                for i, index in enumerate(indices):
                    result = results[index]

                    with columns[i]:
                        st.write(f'**{options[i]}**')
                        st.metric('Standard deviation', result['evaluation']['std'])
                        number_sums = [sum(v) for v in result['partition'].values()]
                        st.bar_chart(number_sums)

                selected_results = {options[i]: results[index] for index in indices}

                st.download_button(
                    label="Download these solutions as JSON",
                    data=json.dumps(selected_results),
                    file_name=f'solution-{job_id}.json',
                    mime='application/json',
                )


def render_optimize():
    st.write('## Number Partitioning')

    numbers_size = st.slider('Size of numbers', 1, 100, 50)
    if st.button('Generate'):
        st.session_state['numbers'] = np.random.randint(1, 100, size=numbers_size)

    if 'numbers' in st.session_state:
        st.bar_chart(st.session_state['numbers'])

    num_partitions = st.slider('Number of partitions', 2, 50)

    if 'numbers' in st.session_state:
        st.write('## Optimization')

        if st.button('Submit'):
            data = dict(numbers=st.session_state['numbers'].tolist(), num_partitions=num_partitions)
            res = requests.post(f'http://{BACKEND_HOST}/optimize', data=json.dumps(data))
            res_json = res.json()
            st.write(res.text)
            st.session_state['job_id'] = res_json['job_id']

    if 'job_id' in st.session_state:
        st.write('## Results')

        if st.button('Refresh'):
            st.success('Refreshed')

        show_result(st.session_state['job_id'])


def render_results():
    st.write('## Results')

    res = requests.get(f"http://{BACKEND_HOST}/results")
    file_paths = res.json()

    def extract_job_id(file_path):
        dirname = os.path.dirname(file_path)
        return os.path.basename(dirname)

    options = list(map(extract_job_id, file_paths))

    if len(options) > 0:
        job_id = st.selectbox('Select Job ID', options)
        st.markdown("""---""")
        show_result(job_id)


def main():
    st.title('Demo with Streamlit and FastAPI')

    with st.sidebar:
        page = st.selectbox('Main menu', ('Optimization', 'Results'))

    if page == 'Optimization':
        render_optimize()
    elif page == 'Results':
        render_results()


if __name__ == '__main__':
    main()