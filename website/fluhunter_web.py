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

st.markdown(
    """
    <style>
    #MainMenu {
      visibility: hidden;
    }
    footer {
      visibility: hidden;
    }
    .ea3mdgi5 {
      padding-top: 0rem;
    }
    .ezrtsby2 {
      height: 0rem;
    }
    .stApp {   
        background-size: cover;   
    }
    .table.table-striped.table-hover {
      color: blue !important;
    }
    table {
      color: white !important;
    }
    .st-emotion-cache-1jicfl2 {
      padding-left: 3.5rem;
      padding-right: 3.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(strings["custom_css"], unsafe_allow_html=True)

st.write(strings["website_name"], unsafe_allow_html=True)


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
                                         spec_io_mode="r", appearance="dark")
            renderer = get_pyg_renderer()
            renderer.explorer()

    with results_tab:

        col_order, col_strategy, col_search, col_searchby = st.columns([1, 1, 2, 1])

        col_order.selectbox('Order by', st.session_state.result.columns, key='order_column',
                            on_change=lambda: order_table())
        col_strategy.selectbox('Strategy', ['Ascending', 'Descending'], key='order_ascending',
                               on_change=lambda: order_table())

        if not st.session_state.result.empty:
            st.download_button(label="Download data as CSV", data=st.session_state.result.to_csv(index=False).encode(),
                               file_name="data.csv", mime="text/csv")
            st.table(st.session_state.result)

        else:
            if error is not None:
                st.write(error)


def order_table():

    order_column = st.session_state.get('order_column', None)
    order_ascending = st.session_state.get('order_ascending', True)

    if order_ascending == 'Ascending':
        order_ascending = True
    elif order_ascending == 'Descending':
        order_ascending = False

    if order_column:
        st.session_state.result.sort_values(by=[order_column], ascending=order_ascending, inplace=True)


def empty_result():
    st.session_state.result = None
    st.session_state.graph = None
