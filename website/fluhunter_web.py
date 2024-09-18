import pandas as pd
from duckdb.duckdb import aggregate

from query_functions import *
import awesome_table
from pygwalker.api.streamlit import StreamlitRenderer

st.set_page_config(layout="wide")

# DATABASE
db = st.connection(name="thesis", type="sql", url="sqlite:///website/data/thesis.db")

# FRONTEND
N_QUERIES = 15
queries = {strings[f"label{x}"]: x for x in range(1, N_QUERIES)}
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "Effect"
if "result" not in st.session_state:
    st.session_state.result = None
if "graph" not in st.session_state:
    st.session_state.graph = None


st.markdown(strings["custom_css"], unsafe_allow_html=True)

st.write(strings["website_name"], unsafe_allow_html=True)

query_tab, readme_tab = st.tabs(["Run Query", "About"])

with readme_tab:
    for i in range(1, N_QUERIES):
        label = strings[f"label{i}"]
        explanation = strings[f"explanation{i}"]
        labels, explanations = st.columns([1, 2])
        with labels:
            st.markdown(f"**{label}:**", unsafe_allow_html=True)
        with explanations:
            st.markdown(f"<div style='border-left: 1px solid gray; padding-left: 10px;'>{explanation}</div>",
                        unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    st.write('')
    st.write(strings["ack"])

with query_tab:

    query_tab, results_tab, graph_tab = st.tabs(["Query", "Results", "Graphs"])

    with query_tab:

        with st.container():

            query_col, space_col, input_col = st.columns([0.45, 0.05, 0.5])

            with query_col:
                query_selection = st.selectbox(label=strings["query_select_label"],
                                               options=queries.keys(),
                                               on_change=lambda: empty_result(),
                                               key="query_selection",
                                               label_visibility="collapsed")
            result, graphs, error = run_query(queries[st.session_state.query_selection], db,
                                              query_col, input_col)

            if result is not None:
                st.session_state.result = result
            if graphs is not None:
                st.session_state.graph = graphs

    if st.session_state.result is not None:

        with graph_tab:
            if st.session_state.graph and not st.session_state.result.empty:
                def get_pyg_renderer() -> "StreamlitRenderer":
                    return StreamlitRenderer(st.session_state.result, spec="./gw_config.json",
                                             spec_io_mode="r", appearance="light")
                renderer = get_pyg_renderer()
                renderer.explorer()

        with results_tab:

            if not st.session_state.result.empty:
                st.download_button(label="Download data as CSV", data=st.session_state.result.to_csv(index=False).encode(),
                                   file_name="data.csv", mime="text/csv")

                columns_list = []
                for col in st.session_state.result.columns:
                    columns_list.append(awesome_table.Column(name=f'{col}', label=f'{col.replace('_', ' ').title()}'))
                awesome_table.AwesomeTable(st.session_state.result, columns=columns_list,
                                           show_order=True, show_search=True)

                st.markdown(
                    """
                    <style>
                    th {
                      color: blue !important;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

            else:
                if error is not None:
                    st.write(error)


def empty_result():
    st.session_state.result = None
    st.session_state.graph = None

