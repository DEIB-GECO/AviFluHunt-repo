import hmac
import json
from json import JSONDecodeError
from query_functions import *
from pygwalker.api.streamlit import StreamlitRenderer

# CONFIG
st.set_page_config(layout="wide")
db = st.connection(name="thesis", type="sql", url="sqlite:///website/data/fluhunt.db")

if "sort_by" not in st.session_state:
    st.session_state.sort_by = "Effect"
if "result" not in st.session_state:
    st.session_state.result = None
if "graphs" not in st.session_state:
    st.session_state.graphs = {}
if 'current_button' not in st.session_state:
    st.session_state.current_button = 0

with open("website/resources/style.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)


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

# FRONTEND

st.write(strings["website_name"], unsafe_allow_html=True)

query_buttons = ["Markers Effects", "Markers", "Markers with Filters", "Mutations"]
queries_for_button = [[1, 12, 13, 14], [9, 7, 6], [5, 2, 3, 4, 8], [10, 11]]

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


            st.button("Add input", on_click=increment_inputs)

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

if st.session_state.result is not None and not st.session_state.result.empty:

    results_tab, *graph_tabs, explore_tab = (
        st.tabs(["Results"] + [key for key in st.session_state.graphs.keys()] + ["Explore Data"]))

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

            try:
                query_pyg_config_file = json.loads(open((f"website/resources/pygwalker_configs/"
                                                         f"query_{queries[query_selection]}_config.json")).read())
            except FileNotFoundError as e:
                query_pyg_config_file = ""
            except JSONDecodeError:
                query_pyg_config_file = ""

            # TODO: further, query-specific, modifications
            enhance_pygwalker(queries[query_selection], st.session_state.result.columns, query_pyg_config_file)

            def get_pyg_renderer() -> "StreamlitRenderer":
                return StreamlitRenderer(st.session_state.result, appearance="dark",
                                         spec_io_mode="r", spec=query_pyg_config_file)

            renderer = get_pyg_renderer()
            renderer.explorer()

with open("website/resources/highlight.css") as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)
