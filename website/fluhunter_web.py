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
        
        /* General Styling */
        :root {
            --main-bg-color: #1A1A1A;
            --secondary-bg-color: white;
            --main-text-color: white;
            --accent-color: #67C184;
            --border-color: black;
        }
    
        #MainMenu {
          visibility: hidden;
        }
        
        footer {
          visibility: hidden;
        }
        
        .ea3mdgi5 {
          padding-top: 0rem !important;
        }
        
        .ezrtsby2 {
          height: 0rem;
        }
        
        .stApp {   
            background: rgb(130,165,255);
            background: linear-gradient(45deg, rgba(130,165,255,1) 0%, rgba(203,164,255,1) 100%); 
            background-size: cover;
            background-image: url("https://static.vecteezy.com/system/resources/previews/002/048/142/original/abstract-minimal-geometric-pattern-design-of-black-and-green-decorative-design-background-illustration-vector.jpg");
        }
        
        .st-emotion-cache-1jicfl2 {
          padding-left: 3.5rem;
          padding-right: 3.5rem;
        }
        
        h1 {
            font-size: 4rem;
            font-weight: bold;
            margin-bottom: 2rem;
            border: 2.5px solid var(--border-color);
            padding: 0rem 1rem !important;
            background-color: var(--secondary-bg-color) !important;
        }
        
        [role="tablist"] {
            width: fit-content;
            height: auto !important;
            background-color: var(--secondary-bg-color) !important;
        }
        
        #tabs-bui3-tab-0 p, #tabs-bui3-tab-1 p, #tabs-bui3-tab-2 p {
            font-size: 1rem;
            font-weight: bold;
            padding: 0.1rem 0.5rem;
            background-color: var(--secondary-bg-color) !important;
        }
        
        #tabs-bui3-tab-0 p:hover, #tabs-bui3-tab-1 p:hover, #tabs-bui3-tab-2 p:hover {
            color: var(--border-color);
            background-color: var(--secondary-bg-color) !important;
        }
        
        [aria-selected="true"] p {
            font-weight: bold;
            color: var(--border-color);
            border: 2.5px solid var(--border-color);
            border-bottom: 0px solid var(--border-color);
            padding: 0.1rem 1rem !important;
            background-color: var(--secondary-bg-color) !important;
        }
        
        .st-bq {
            font-size: 1rem !important;
        }
        
        .st-f9 {
            height: 0 !important;
        }
        
        .st-c9 {
            background-color: black;
        }
        
        .st-ak {
            padding-bottom: 0rem !important;
        }
        
        .st-c6 {
            height: 0.125rem;
        }
        
        .st-ff, .st-fg {
            width: 0rem !important;
        }
        
        .st-bw {
            height: 2.25rem;
        }
        
        [data-testid="stForm"] button, [data-testid="baseButton-secondary"] {
            border: 2.5px solid var(--border-color);
            border-radius: 0rem !important;
            padding: 0.1rem 2rem !important;
            float: right;
            font-weight: bold !important;
            margin: 1rem 0rem !important;
            background: var(--secondary-bg-color) !important;
        }
        
        [data-testid="baseButton-secondary"] {
            font-weight: bold !important;
            float: left !important;
            padding: 0.1rem 1rem !important;
        }
        
        [data-testid="stForm"] button:hover, [data-testid="baseButton-secondary"]:hover {
            color: black !important;
            font-weight: bold;
            border: 2.5px solid var(--border-color);
            background-color: var(--accent-color) !important;
        }
        
        [data-testid="stForm"] .stMarkdown p {
            font-weight: bold !important;
            font-size: 1.5rem !important;
        }
        
        [data-testid="stForm"] button p {
            font-weight: bold !important;
        }
        
        [data-baseweb="tab-highlight"] {
            width: 0rem !important;
            background-color: var(--secondary-bg-color) !important;
        }
        
        [data-baseweb="tab-border"] {
            background-color: var(--border-color) !important;
        }
        
        /* Query Tab Styling */
        
        .st-ci, .st-cg, .st-ch, .st-cf {
            border-radius: 0rem !important;
        }
        
        [data-baseweb="select"] {
            border: 2.5px solid var(--border-color);
            background-color: var(--secondary-bg-color) !important;
            font-weight: bold;
            height: auto !important;
            padding-left: .5rem;
            padding-top: .25rem;
            padding-bottom: .25rem;
        }
        
        [data-baseweb="select"] div {
            border: 0px solid var(--border-color) !important;
        }
        
        ul {
            border-radius: 0 !important;
            border: 2.5px solid var(--border-color) !important;
        }
        
        li {
            background: var(--secondary-bg-color) !important;
            font-weight: bold;
        }
        
        li:hover {
            background: black !important;
            color: var(--main-text-color); !important;
            font-weight: bold;
        }
        
        .query_text {
            padding: 1.5rem;
            font-size: 1.1rem !important;
            border: 2.5px solid var(--border-color);
            background-color: var(--secondary-bg-color) !important;
            border-radius: 0rem !important;
        }
        
        .e10yg2by1 {
            border: 2.5px solid var(--border-color);
            border-radius: 0rem;
            padding: 1.5rem;
        }
        
        label p {
            font-weight: bold !important;
            font-size: 1rem !important;
        }
        
        [data-testid="stForm"] {
            background-color: var(--secondary-bg-color) !important;
        }
        
        /* Table Tab Styling */
        
        .table.table-striped.table-hover {
            background-color: var(--accent-color) !important;
        }
        
        #tabs-bui3-tabpanel-1 {
            background-color: var(--secondary-bg-color) !important;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            border: 2.5px solid var(--border-color) !important;
        }
        
        table th, table td {
            padding: 12px;
            border: 1px solid #ddd;
        }
        
        table th {
            background-color:  var(--accent-color);
            color: black !important;
            font-weight: bold !important;
        }
        
        table tr:nth-child(odd) {
            background-color: #fff !important;
        }
        
        table tr:nth-child(even) {
            background-color: #f2f2f2 !important;
        }
        
        table tr:hover {
            background-color: #ddd !important;
        }
        
        /* Graphs Tab Styling */
        
        #tabs-bui3-tabpanel-2 iframe {
            border: 2.5px solid var(--border-color) !important;
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

        query_col, space, input_col = st.columns([0.45, 0.025, 0.525])

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
