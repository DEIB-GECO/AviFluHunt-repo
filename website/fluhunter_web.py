import hmac
from query_functions import *
from pygwalker.api.streamlit import StreamlitRenderer

st.set_page_config(layout="wide")

# DATABASE
db = st.connection(name="thesis", type="sql", url="sqlite:///website/data/thesis.db")


# PASSWORD CHECK
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

# FRONTEND
N_QUERIES = 15
if "sort_by" not in st.session_state:
    st.session_state.sort_by = "Effect"
if "result" not in st.session_state:
    st.session_state.result = None
if "graphs" not in st.session_state:
    st.session_state.graphs = {}

st.markdown(
    """
    <style>
        
        /* General Styling */
        :root {
            --main-bg-color: #1A1A1A;
            --secondary-bg-color: white;
            --main-text-color: white;
            --accent-color: rgba(6,188,157,1);
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
            background: rgb(188,6,95);
            background: linear-gradient(90deg, rgba(6,188,157,1) 0%, rgba(23,6,89,1) 100%); 
        }
        
        .st-emotion-cache-1jicfl2 {
          padding-left: 3.5rem;
          padding-right: 3.5rem;
        }
        
        h1 {
            width: fit-content !important;
            font-size: 4rem;
            font-weight: bold;
            margin-bottom: 2rem;
            border: 2.5px solid var(--border-color);
            padding: 0rem 1rem !important;
            background-color: var(--secondary-bg-color) !important;
        }
        
        data-testid="stTabs"] {
            min-height: 0vh;
        }
        
        [role="tablist"] {
            gap: 0;
            width: fit-content;
            height: fit-content !important;
            border: 2.5px solid var(--border-color);
            background-color: transparent !important;
        }
        
        [data-baseweb="tab"] p {
            height: fit-content !important;
            font-size: 1rem;
            font-weight: bold;
            background-color: transparent !important;
        }
        
        [data-baseweb="tab"]  {
            padding: 0.1rem 1rem !important;
            height: fit-content !important;
            background-color: var(--secondary-bg-color) !important;
        }
        
        [data-baseweb="tab"]:hover {
            color: var(--border-color);
            background-color: var(--accent-color) !important;
        }
        
        [aria-selected="true"] {
            font-weight: bold;
            color: var(--border-color);
            padding: 0.1rem 1rem !important;
            background-color: var(--accent-color) !important;
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
        
        [data-testid="stNumberInputContainer"], [data-testid="stDateInput-Input"] {
            border-radius: 0rem !important;
            height: fit-content !important;
            border: 2.5px solid var(--border-color);
        }
        
        [aria-roledescription="datepicker"] {
            font-weight: bold !important;
            border: 2.5px solid var(--border-color);
            background-color: var(--secondary-bg-color) !important;
        }
        
        [data-testid="stDateInput-Input"] {
            font-weight: bold !important;
        }
        
        [data-testid="stNumberInputContainer"] button {
            color: black !important;
            border: 0px solid var(--border-color);
            margin: 0rem 0rem !important;
        }
        
        [data-testid="stNumberInputContainer"] button:hover {
            color: black !important;
            border: 0px solid var(--border-color);
            margin: 0rem 0rem !important;
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
            background: var(--accent-color) !important;
            color: black !important;
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
        
        #tabs-bui3-tabpanel-3 button {
            float: right !important;
        }
        
        #tabs-bui3-tabpanel-3 [role="tablist"] {
            gap: 0;
            width: fit-content;
            border: 2.5px solid var(--border-color);
            background-color: transparent !important;
        }
        
        #tabs-bui3-tabpanel-3 [role="tablist"] button {
            border: 0 solid var(--border-color);
            margin: 0rem 0rem !important;
        }
        
        #tabs-bui3-tabpanel-3 [role="tablist"] [aria-selected="true"] {
            font-weight: bold;
            color: var(--border-color);
            background-color: var(--accent-color) !important;
        }
        
        /* Table Tab Styling */
        
        .table.table-striped.table-hover {
            background-color: var(--accent-color) !important;
        }
        
        #tabs-bui3-tabpanel-1 {
            background-color: transparent !important;
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


query_tabs = st.tabs(["Markers' Effects", "Markers", "Markers with Filters", "Mutations"])
queries_for_tab = [[1, 12, 13, 14], [9, 7, 6], [5, 2, 3, 4, 8], [10, 11]]

for tab_index, query_tab in enumerate(query_tabs):

    queries = {strings[f"label{x}"]: x for x in queries_for_tab[tab_index]}

    with query_tab:

        with st.container():

            query_col, space, input_col = st.columns([0.45, 0.025, 0.525])

            with query_col:
                query_selection = st.selectbox(label=strings["query_select_label"],
                                               options=queries.keys(),
                                               on_change=lambda: empty_result(),
                                               key=f"query_selection{query_tab}",
                                               label_visibility="collapsed")
            result, graphs, error = run_query(queries[query_selection], db,
                                              query_col, input_col)

            if result is not None:
                st.session_state.result = result
                if graphs is not None:
                    st.session_state.graphs = graphs
                else:
                    st.session_state.graphs = {}

if st.session_state.result is not None:

    results_tab, *graph_tabs, explore_tab = (
        st.tabs(["Results"] + [key for key in st.session_state.graphs.keys()] + ["Explore Data"]))

    for index, graph_tab in enumerate(graph_tabs):
        with graph_tab:
            graph = st.session_state.graphs[[key for key in st.session_state.graphs.keys()][index]]
            fn = 'results.png'
            graph.savefig(fn)
            with open(fn, "rb") as img:
                btn = st.download_button(label="Download Plot", data=img,
                                         file_name=fn, mime="image/png")
            st.pyplot(graph)

    with explore_tab:
        if not st.session_state.result.empty:
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
            st.table(st.session_state.result.reset_index(drop=True))

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
    st.session_state.graphs = {}
