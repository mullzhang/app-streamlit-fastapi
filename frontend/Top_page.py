import streamlit as st
from streamlit.logger import get_logger

logger = get_logger(__name__)


def main():
    st.set_page_config(
        page_title="Demo with Streamlit and FastAPI",
        page_icon="👋",
    )

    st.title("Demo with Streamlit and FastAPI")
    st.markdown(
        """
        This is a demo on [the number partitioning problem](https://en.wikipedia.org/wiki/Partition_problem), 
        which implemented with [Streamlit](https://streamlit.io/) and [FastAPI](https://fastapi.tiangolo.com/ja/).
        """
    )


if __name__ == "__main__":
    main()
