import hmac
import json
from json import JSONDecodeError

from query_functions import *
from pygwalker.api.streamlit import StreamlitRenderer

# CONFIG
st.set_page_config(layout="wide", page_title="AviFluHunt")
db = st.connection(name="fluhunt", type="sql", url="sqlite:///website/data/fluhunt.db")

if "sort_by" not in st.session_state:
    st.session_state.sort_by = "Effect"
if "result" not in st.session_state:
    st.session_state.result = None
if "graphs" not in st.session_state:
    st.session_state.graphs = {}
if 'current_button' not in st.session_state:
    st.session_state.current_button = 0

#with open("website/resources/style.css") as css:
    #st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.markdown(f'<style>{
"""
/* General Styling */
:root {
    --main-bg-color: #1A1A1A;
    --secondary-bg-color: white;
    --main-text-color: white;
    --accent-color: rgb(160, 204, 197);
    --border-color: black;
}

@import url("https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap");

body {
    font-family: Poppins, sans-serif !important;
}

.stApp {
    background-color: #627d98;
}

/* Webkit-based browsers (Chrome, Safari) */
::-webkit-scrollbar {
    width: 10px; /* Width of the scrollbar */
    background: rgba(255, 255, 255, 0); /* Background color of the scrollbar */
}

::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0); /* Color of the draggable part of the scrollbar */
    border-radius: 10px; /* Rounded corners */
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0); /* Darker color when hovered */
}

/* Firefox */
* {
    scrollbar-width: thin; /* Make scrollbar thinner */
    scrollbar-color: rgba(0, 0, 0, 0) rgba(255, 255, 255, 0); /* Thumb and background color */
}

.st-emotion-cache-1jicfl2 {
    padding: 0;
    font-family: Poppins, sans-serif !important;
}

h1 {

    margin: 0;
    margin-top: -1rem;
    width: 100% !important;
    padding: 0.5rem !important;
    
    color: white;
    font-size: 20px;
    font-weight: bold;
    background-color: transparent;
    border-bottom: 2.5px solid white;
    font-family: Poppins, sans-serif !important;
}

[data-testid="stHorizontalBlock"] {
    padding-top: 1rem;
}

[data-testid='stTabs'] {
    min-height: 0;
    margin-top: 5rem;
}

[role='tablist'] {
    gap: 0;
    width: fit-content;
    height: fit-content !important;
    border: 2.5px solid var(--border-color);
    background-color: transparent !important;
    padding-bottom: 0 !important;
    font-family: Poppins, sans-serif !important;
}

[data-baseweb='tab'] p {
    height: fit-content !important;
    font-size: 1rem !important;
    font-weight: bold !important;
    background-color: transparent !important;
    font-family: Poppins, sans-serif !important;
}

[data-baseweb='tab'] {
    padding: 0.1rem 1rem !important;
    height: fit-content !important;
    background-color: var(--secondary-bg-color) !important;
    font-family: Poppins, sans-serif !important;
}

[data-baseweb='tab']:hover {
    color: var(--border-color) !important;
    background-color: var(--accent-color) !important;
    font-family: Poppins, sans-serif !important;
}

[aria-selected='true'] {
    font-weight: bold !important;
    color: var(--border-color) !important;
    padding: 0.1rem 1rem !important;
    background-color: var(--accent-color) !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stVerticalBlockBorderWrapper'] button {
    margin-right: 0.125rem;
    margin-bottom: 1rem;
    font-weight: bold !important;
    float: left;
    border-radius: 0 !important;
    background-color: var(--secondary-bg-color);
    font-family: Poppins, sans-serif !important;
    border-top: 2.5px solid black;
    border-bottom: 2.5px solid black;
    border-right: 2.5px solid black;
    border-left: 2.5px solid black;
}

[data-testid="stVerticalBlock"] > div:nth-of-type(2) > div > button  {
    background-color: black;
    color: white;
}

[data-testid="stVerticalBlock"] > div:nth-of-type(2) > div > button:hover  {
    background-color: black !important;
    color: white !important;
}

[data-testid="stVerticalBlock"] > div:nth-of-type(2) > div > button:focus  {
    background-color: black !important;
    color: white !important;
}

[data-testid='stVerticalBlockBorderWrapper'] button > div > p {
    font-weight: bold !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stVerticalBlockBorderWrapper'] button:hover {
    border-radius: 0 !important;
    background-color: var(--accent-color);
    font-family: Poppins, sans-serif !important;
}

[data-testid='stVerticalBlockBorderWrapper'] button:focus {
    border-radius: 0 !important;
    background-color: var(--accent-color);
    font-family: Poppins, sans-serif !important;
}

[data-testid='stVerticalBlock'] > [data-testid='stVerticalBlockBorderWrapper'] > div > [data-testid='stVerticalBlock']:has(#fake) {
    display: inline-block;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stForm'] button {
    border: 2.5px solid var(--border-color);
    border-radius: 0 !important;
    padding: 0.1rem 2rem !important;
    float: right;
    font-weight: bold !important;
    margin: 1rem 0 !important;
    background: var(--secondary-bg-color) !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stForm'] button:hover, [data-testid='baseButton-secondary']:hover {
    color: black !important;
    font-weight: bold;
    border: 2.5px solid var(--border-color);
    background-color: var(--accent-color) !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stNumberInputContainer'], [data-testid='stDateInput-Input'] {
    border-radius: 0 !important;
    height: fit-content !important;
    border: 2.5px solid var(--border-color);
    font-family: Poppins, sans-serif !important;
}

[aria-roledescription='datepicker'] {
    font-weight: bold !important;
    border: 2.5px solid var(--border-color);
    background-color: var(--secondary-bg-color) !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stDateInput-Input'] {
    font-weight: bold !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stNumberInputContainer'] button {
    color: black !important;
    border: 0 solid var(--border-color);
    margin: 0 0 !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stNumberInputContainer'] button:hover {
    color: black !important;
    border: 0 solid var(--border-color);
    margin: 0 0 !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stForm'] .stMarkdown p {
    font-weight: bold !important;
    font-size: 1.5rem !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stForm'] button p {
    font-weight: bold !important;
    font-family: Poppins, sans-serif !important;
}

[data-baseweb='tab-highlight'] {
    width: 0 !important;
    background-color: var(--secondary-bg-color) !important;
    font-family: Poppins, sans-serif !important;
}

[data-baseweb='tab-border'] {
    background-color: var(--border-color) !important;
    font-family: Poppins, sans-serif !important;
}

/* Query Tab Styling */

.st-ci, .st-cg, .st-ch, .st-cf {
    border-radius: 0 !important;
    font-family: Poppins, sans-serif !important;
}

[data-baseweb='select'] {
    border: 2.5px solid var(--border-color);
    background-color: var(--secondary-bg-color) !important;
    font-weight: bold;
    height: auto !important;
    padding-left: .5rem;
    padding-top: .25rem;
    padding-bottom: .25rem;
    font-family: Poppins, sans-serif !important;
}

[data-baseweb='select'] div {
    border: 0 solid var(--border-color) !important;
    font-family: Poppins, sans-serif !important;
}

ul {
    border-radius: 0 !important;
    border: 2.5px solid var(--border-color) !important;
    font-family: Poppins, sans-serif !important;
}

li {
    background: var(--secondary-bg-color) !important;
    font-weight: bold;
    font-family: Poppins, sans-serif !important;
}

li:hover {
    background: var(--accent-color) !important;
    color: black !important;
    font-weight: bold;
    font-family: Poppins, sans-serif !important;
}

.query_text {
    padding: 1.5rem;
    font-size: 1.1rem !important;
    border: 2.5px solid var(--border-color);
    background-color: var(--secondary-bg-color) !important;
    border-radius: 0 !important;
    font-family: Poppins, sans-serif !important;
}

.e10yg2by1 {
    border: 2.5px solid var(--border-color);
    border-radius: 0;
    padding: 1.5rem;
    font-family: Poppins, sans-serif !important;
}

label p {
    font-weight: bold !important;
    font-size: 1rem !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stForm'] {
    background-color: var(--secondary-bg-color) !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stTabs'] [role='tablist'] {
    gap: 0;
    width: fit-content;
    border: 2.5px solid var(--border-color);
    background-color: transparent !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stTabs'] [role='tablist'] button {
    border: 0 solid var(--border-color);
    margin: 0 0 !important;
    font-family: Poppins, sans-serif !important;
}

[data-testid='stForm'] [role='tablist'] [aria-selected='true'] {
    font-weight: bold;
    color: var(--border-color);
    background-color: var(--accent-color) !important;
    font-family: Poppins, sans-serif !important;
}

#error_div {
    border-radius: 1rem;
    border: 2.5px solid var(--border-color);
    padding: 1.5rem !important;
    background: rgb(210,3,3);
    background: linear-gradient(270deg, rgb(172, 4, 4) 0%, rgb(142, 0, 0) 100%);
    color: white;
    font-weight: bold;
    text-align: center;
    font-family: Poppins, sans-serif !important;
}

#error_icon {
    height: 3rem;
    margin-right: 1rem;
    font-family: Poppins, sans-serif !important;
}

/* Table Tab Styling */

.table.table-striped.table-hover {
    background-color: var(--accent-color) !important;
    font-family: Poppins, sans-serif !important;
}

#tabs-bui3-tabpanel-1 {
    background-color: transparent !important;
    font-family: Poppins, sans-serif !important;
}

table {
    width: 100%;
    border-collapse: collapse;
    border: 2.5px solid var(--border-color) !important;
    font-family: Poppins, sans-serif !important;
}

table th, table td {
    padding: 12px;
    border: 1px solid #ddd;
    font-family: Poppins, sans-serif !important;
}

table th {
    background-color:  var(--accent-color);
    color: black !important;
    font-weight: bold !important;
    font-family: Poppins, sans-serif !important;
}

table tr:nth-child(odd) {
    background-color: #fff !important;
    font-family: Poppins, sans-serif !important;
}

table tr:nth-child(even) {
    background-color: #f2f2f2 !important;
    font-family: Poppins, sans-serif !important;
}

table tr:hover {
    background-color: #ddd !important;
    font-family: Poppins, sans-serif !important;
}

/* Graphs Tab Styling */

#tabs-bui3-tabpanel-2 iframe {
    border: 2.5px solid var(--border-color) !important;
    font-family: Poppins, sans-serif !important;
}

/* OTHER */
.code {
    font-family: Poppins, sans-serif !important;
    background-color: #000;
    color: #fff;
    padding: 1rem 2rem;
    border: 0 solid #ccc;
    border-radius: 0;
    overflow-x: auto;
    margin: 10px 0;
    font-weight: bold;
}

.code > ul {
    list-style-type: none;
    margin: 0rem 0 !important;
}
.code > ul > li {
    background-color: transparent !important;
    margin-left: 0 !important;
    padding-left: 0 !important;
    font-weight: normal;
}
.code > ul > li:hover {
    background-color: transparent !important;
    color: white !important;
}
[data-testid="stVerticalBlock"] > div > div > [data-testid='stVerticalBlockBorderWrapper'] > div > div > div > div > button {
    position: absolute;
    margin-top: 322.5px !important;
    margin-left: 26.5px !important;
    z-index: 10000 !important;
}

/*[data-testid="stNumberInputContainer"] {
    max-width: 50%;
}*/

[aria-label="Limit:"] {
    border-radius: 0 !important;
    background-color: white !important;
}

[data-testid="stVerticalBlockBorderWrapper"] > div > div > div > div > div > div > img {
    border-radius: 10px;
    border: 2.5px solid black;
    padding: 1.5%;
    background: white;
}
"""
}</style>', unsafe_allow_html=True)

# PASSWORD CHECK
def check_password():
    return True
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


# HELPERS
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


def enhance_pygwalker(selection, dataframe_columns, pyg_json_config):

    if selection == 3:
        host_1_name = dataframe_columns[1]
        host_2_name = dataframe_columns[2]
        rows = [
            {
                "fid": host_1_name,
                "name": host_1_name,
                "basename": host_1_name,
                "analyticType": "measure",
                "semanticType": "quantitative",
                "aggName": "sum",
                "offset": 0
            },
            {
                "fid": host_2_name,
                "name": host_2_name,
                "basename": host_2_name,
                "analyticType": "measure",
                "semanticType": "quantitative",
                "aggName": "sum",
                "offset": 0
            }
        ]
        pyg_json_config[0]['encodings']['rows'] = rows

    elif selection == 4:
        host_1_name = dataframe_columns[1]
        host_2_name = dataframe_columns[2]
        host_3_name = dataframe_columns[2]
        host_4_name = dataframe_columns[2]
        host_5_name = dataframe_columns[2]
        host_6_name = dataframe_columns[2]
        host_names = [host_1_name, host_2_name, host_3_name, host_4_name, host_5_name, host_6_name]
        rows = [
            {
                "fid": host_name,
                "name": host_name,
                "basename": host_name,
                "analyticType": "measure",
                "semanticType": "quantitative",
                "aggName": "sum",
                "offset": 0
            } for host_name in host_names
        ]
        pyg_json_config[0]['encodings']['rows'] = rows

    return pyg_json_config


def choose_default_order(selection, columns):
    if selection == 2:
        default_column = "Percentage"
    elif selection == 3:
        default_column = "Diff"
    elif selection == 5:
        default_column = "#"
    elif selection == 6:
        default_column = "Normalized Percentage"
    elif selection == 7:
        default_column = "Found in #Isolates"
    elif selection == 8:
        default_column = "Distinct Markers Per Host"
    elif selection == 9:
        default_column = "Percentage"
    elif selection == 11:
        default_column = "#Mutation per Sample"
    else:
        return columns

    return [x for x in columns if default_column in x] + [x for x in columns if x != default_column]


# FRONTEND
st.write(strings["website_name"], unsafe_allow_html=True)

query_buttons = ["About", "Markers Effects", "Markers", "Markers with Filters", "Mutations"]
queries_for_button = [[], [1, 12, 13, 14], [9, 7, 6, 15], [5, 2, 3, 4, 8], [10, 11]]

with st.container():
    fake = st.html("<div id='fake'></div>")
    for index, title in enumerate(query_buttons):
        if st.button(title):
            st.session_state.current_button = index

queries = {strings[f"label{x}"]: x for x in queries_for_button[st.session_state.current_button]}

with st.container():

    if st.session_state.current_button != st.session_state.get('last_button', -1):
        empty_result()

    st.session_state.last_button = st.session_state.current_button

    if st.session_state.current_button != 0:

        query_col, space, input_col = st.columns([0.45, 0.025, 0.525])

        with query_col:
            query_selection = st.selectbox(label=strings["query_select_label"],
                                           options=queries.keys(),
                                           on_change=lambda: empty_result(),
                                           key=f"query_selection{st.session_state.current_button}",
                                           label_visibility="collapsed")

        with input_col:
            if queries[query_selection] == 10:
                def increment_inputs():
                    st.session_state.num_inputs += 1


                st.button("Add Manual Zone", on_click=increment_inputs)

        result, graphs, error = run_query(queries[query_selection], db,
                                          query_col, input_col)

        if result is not None:
            empty_result()
            st.session_state.result = result
            st.session_state.graphs = graphs

        if result is None or result.empty:
            if error is not None:
                with query_col:
                    with st.container():
                        st.html(f"<div id='error_div'>"
                                f"<img id='error_icon' src='https://pngimg.com/uploads/attention/attention_PNG5.png'>"
                                f"{error}!"
                                f"</div>")

    else:
        with open("website/resources/about.html") as about_html:
            st.html(about_html.read())

if st.session_state.result is not None and not st.session_state.result.empty:

    results_tab, *graph_tabs, explore_tab = (
        st.tabs(["Results"] + [key for key in st.session_state.graphs.keys()] + ["Explore Data"]))

    with results_tab:

        col_order, col_strategy, col_search, col_searchby = st.columns([1, 1, 2, 1])

        col_order.selectbox('Order by', choose_default_order(queries[query_selection], st.session_state.result.columns),
                            key='order_column', on_change=lambda: order_table())
        col_strategy.selectbox('Strategy', ['Descending', 'Ascending'], key='order_ascending',
                               on_change=lambda: order_table())

        limit = st.number_input(label=strings["param_label9c"], key=strings["param_label9c"],
                                min_value=1, step=1, value=10000)

        if not st.session_state.result.empty:
            st.download_button(label="Download data as CSV", data=st.session_state.result.to_csv(index=False).encode(),
                               file_name="data.csv", mime="text/csv")
            st.table(st.session_state.result.reset_index(drop=True).head(limit))

    for index, graph_tab in enumerate(graph_tabs):
        with graph_tab:

            graph = st.session_state.graphs[[key for key in st.session_state.graphs.keys()][index]]
            fn = 'results.png'
            graph.savefig(fn)

            with open(fn, "rb") as img:
                st.text("")
                btn = st.download_button(label="Download Plot", data=img,
                                         file_name=fn, mime="image/png")

            empty1, img_col, empty2 = st.columns([0.025, 0.9, 0.025])
            with img_col:
                st.pyplot(graph)

    with explore_tab:

        if not st.session_state.result.empty:

            try:
                query_pyg_config_file = json.loads(open((f"website/resources/pygwalker_configs/"
                                                         f"query_{queries[query_selection]}_config.json")).read())
            except FileNotFoundError as e:
                query_pyg_config_file = ""
            except JSONDecodeError:
                query_pyg_config_file = ""

            enhance_pygwalker(queries[query_selection], st.session_state.result.columns, query_pyg_config_file)

            def get_pyg_renderer() -> "StreamlitRenderer":
                return StreamlitRenderer(st.session_state.result, appearance="dark",
                                         spec_io_mode="r", spec=query_pyg_config_file)

            renderer = get_pyg_renderer()
            renderer.explorer()

#with open("website/resources/highlight.css") as css:
    #st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
