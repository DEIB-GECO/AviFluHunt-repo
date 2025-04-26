import hmac
import json
import re

from query_functions import *


# PASSWORD CHECK
def check_auth():

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


def init_session():
    if "sort_by" not in st.session_state:
        st.session_state.sort_by = "Effect"
    if "result" not in st.session_state:
        st.session_state.result = None
    if "graph" not in st.session_state:
        st.session_state.graph = None
    if 'current_query_type' not in st.session_state:
        st.session_state.current_query_type = "Markers"
    if 'global_regions' not in st.session_state:
        st.session_state.global_regions = {f"{region.replace(" ", "")}": region for region in fe_get_regions(db)['region'].tolist()}
    if 'g_regions' not in st.session_state:
        st.session_state.g_regions = fe_get_regions(db)['region'].tolist()
    if 'global_states' not in st.session_state:
        st.session_state.global_states = None
    if 'global_start_year' not in st.session_state:
        st.session_state.global_start_year = 2000
    if 'global_end_year' not in st.session_state:
        st.session_state.global_end_year = 2025
    if 'global_start_month' not in st.session_state:
        st.session_state.global_start_month = 1
    if 'global_end_month' not in st.session_state:
        st.session_state.global_end_month = 1


def set_default_table_order(selection, columns):

    column_map = {
        2: "Percentage",
        3: "Diff",
        5: "#",
        6: "Normalized Percentage",
        7: "Found in #Isolates",
        8: "Distinct Markers Per Host",
        9: "Percentage",
        11: "#Mutation per Sample"
    }

    default_column = column_map.get(selection)
    if not default_column:
        return columns

    return [default_column] + [other_col for other_col in columns if other_col != default_column]


def order_table(dataframe):
    order_column = st.session_state.get('order_column', None)
    order_ascending = st.session_state.get('order_ascending', True)

    if order_ascending == 'Ascending':
        order_ascending = True
    else:
        order_ascending = False

    if order_column:
        dataframe.sort_values(by=[order_column], ascending=order_ascending, inplace=True, ignore_index=True)
        dataframe.reset_index(drop=True, inplace=True)


def run_query(database_connection, query_selection, query, local_params):
    result = database_connection.query(query, params=local_params | get_global_isolates_params())
    st.session_state.result = manip_result(result, query_selection, local_params)


def manip_result(result, query_selection, local_params):
    if result is not None:
        if query_selection == 3:
            return manip_result3(result, local_params)
        if query_selection == 4:
            return manip_result4(result, local_params)
    return result


def get_result_graph(selection):
    if st.session_state.result is not None:
        plot_params = query_mapping[selection]["plot_params"]
        if plot_params:
            if not st.session_state.result.empty:
                st.session_state.graph = plot_data(st.session_state.result, **plot_params)
        else:
            st.session_state.graph = None


def get_global_isolates_params():
    return {
        "global_start_year": st.session_state.global_start_year,
        "global_end_year": st.session_state.global_end_year,
        "global_start_month": st.session_state.global_start_month,
        "global_end_month": st.session_state.global_end_month,
        **(st.session_state.global_regions if st.session_state.global_regions else {}),
        **(st.session_state.global_states | {"global_states": "NotNull"}
           if st.session_state.global_states
           else {"global_states": None}
           )
    }


def replace_query_placeholders(selected_query_index, query, params):

    if selected_query_index == 10:
        query = with_query10(params["bins"]) + query

    if selected_query_index in {1, 15}:
        query = query.replace("markers_placeholder", params["markers_placeholder"])
    if selected_query_index in {3, 4}:
        query = query.replace("hosts", params["hosts"])

    if st.session_state.global_regions:
        global_regions = ", ".join(f":{region.replace(' ', '')}" for region in st.session_state.global_regions)
        query = query.replace("global_regions_placeholder", global_regions)
    else:
        query = query.replace("global_regions_placeholder", "")

    if st.session_state.global_states:
        global_states = ", ".join(
            f":{re.sub(r'[^a-zA-Z]', '', state)}" for state in st.session_state.global_states.values())
    else:
        global_states = ""

    query = query.replace("global_states_placeholder", global_states)
    return query


def get_pygwalker_default_config(selected_query_index):

    config_file_path = f"website/resources/pygwalker_configs/query_{selected_query_index}_config.json"

    try:
        query_pyg_config_file = json.loads(open(config_file_path).read())
    except (FileNotFoundError, json.JSONDecodeError):
        query_pyg_config_file = ""

    return query_pyg_config_file


@st.cache_data(show_spinner=False)
def split_frame(df, rows):
    return [df.iloc[i:i + rows] for i in range(0, len(df), rows)]


def fe_get_filtered_isolates_count(database_connection):

    query = replace_query_placeholders(-1, get_filtered_isolates_count, {})
    return database_connection.query(query, params=get_global_isolates_params())


def fe_get_all_isolates_count(database_connection):
    return database_connection.query(get_isolates_count)


def fe_get_regions(database_connection):
    return database_connection.query(get_regions)


def get_locations_from_regions(database_connection, regions):

    locations_from_regions = \
        ("SELECT DISTINCT state FROM Location "
         "WHERE region IN (" + ",".join([f":{reg.replace(" ", "")}" for reg in regions]) + ")")
    return database_connection.query(locations_from_regions,
                                     params={reg.replace(" ", ""): regions[reg] for reg in regions})


query_mapping = {
        1: {
            'query': get_markers_literature,
            'params_func': params1,
            'plot_params': {}
        },
        2: {
            'query': get_markers_by_human_percentage,
            'params_func': params2,
            'plot_params': {}
        },
        3: {
            'query': get_markers_id_by_host_relative_presence,
            'params_func': params3,
            'plot_params': {
                'plot_type': "bar",
                'top_n': 20,
                'title': '',
                'xlabel': 'Host',
                'ylabel': 'Distinct Markers Per Host',
                'color': 'skyblue',
                'show_values': True,
                'sort_column': 'Diff',
                'plot_column': 'Distinct Markers Per Host',
                'label_column': 'Host',
                'host_comparison': True
            }
        },
        4: {
            'query': get_markers_id_by_host_relative_presence,
            'params_func': params4,
            'plot_params': {}
        },
        5: {
            'query': get_marker_host_distribution,
            'params_func': get_marker,
            'plot_params': {
                'plot_type': "bar",
                'top_n': 20,
                'title': 'Top Hosts',
                'xlabel': 'Host',
                'ylabel': '#',
                'color': 'skyblue',
                'sort_column': '#',
                'plot_column': '#',
                'label_column': "Host",
                'host_comparison': False
            }
        },
        6: {
            'query': get_markers_location_distribution,
            'params_func': get_marker,
            'plot_params': {
                'plot_type': "bar",
                'top_n': 20,
                'title': 'Top States',
                'xlabel': 'State',
                'ylabel': 'Normalized Percentage',
                'color': 'skyblue',
                'sort_column': 'Normalized Percentage',
                'plot_column': 'Normalized Percentage',
                'label_column': "State",
                'host_comparison': False
            }
        },
        7: {
            'query': get_most_common_markers_by_filters,
            'params_func': params7,
            'plot_params': {}
        },
        8: {
            'query': get_host_by_n_of_markers,
            'params_func': params8,
            'plot_params': {
                'plot_type': "bar",
                'top_n': 10,
                'title': 'Top 10 Hosts by Distinct Markers',
                'xlabel': 'Host',
                'ylabel': 'Distinct Markers Per Host',
                'color': 'skyblue',
                'show_values': True,
                'sort_column': 'Host',
                'plot_column': 'Distinct Markers Per Host',
                'label_column': 'Host',
                'host_comparison': False
            }
        },
        9: {
            'query': get_markers_by_relevance,
            'params_func': params9,
            'plot_params': {
                'plot_type': "bar",
                'top_n': 10,
                'title': 'Top 10 Markers by Percentage',
                'xlabel': 'Marker',
                'ylabel': 'Percentage',
                'color': 'skyblue',
                'show_values': False,
                'sort_column': 'Percentage',
                'plot_column': 'Percentage',
                'label_column': 'Marker',
                'host_comparison': False
            }
        },
        10: {
            'query': get_segment_mutability_zones,
            'params_func': params10,
            'plot_params': {}
        },
        11: {
            'query': get_mutability_peak_months,
            'params_func': params11,
            'plot_params': {}
        },
        12: {
            'query': get_group_of_marker,
            'params_func': get_marker,
            'plot_params': {}
        },
        13: {
            'query': get_effects_by_effect_metadata,
            'params_func': params13,
            'plot_params': {}
        },
        14: {
            'query': get_marker_groups_by_effect,
            'params_func': params14,
            'plot_params': {}
        },
        15: {
            'query': get_markers_over_time,
            'params_func': params15,
            'plot_params': {
                'plot_type': "line",
                'top_n': 1000,
                'title': 'Marker prevalence over the years',
                'xlabel': 'Year',
                'ylabel': 'Prevalence',
                'color': 'skyblue',
                'show_values': True,
                'sort_column': 'Year',
                'plot_column': 'Year',
                'label_column': 'Year',
                'host_comparison': False
            }
        }
    }

