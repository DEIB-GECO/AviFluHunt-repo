import hmac
import json

from query_functions import *


# PASSWORD CHECK
def check_auth():

    return True

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
    if "graphs" not in st.session_state:
        st.session_state.graphs = {}
    if 'current_query_type' not in st.session_state:
        st.session_state.current_query_type = "Markers"
    if 'global_region' not in st.session_state:
        st.session_state.global_region = None
    if 'global_locs' not in st.session_state:
        st.session_state.global_locs = None


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
        dataframe.sort_values(by=[order_column], ascending=order_ascending, inplace=True)


def run_query(database_connection, query, local_params):
    run_global_filters_on_isolates(database_connection)
    st.session_state.result = database_connection.query(query, params=local_params | get_global_isolates_params())


def run_global_filters_on_isolates(database_connection):

    pass
    #database_connection.execute(drop_isolates_with_global_filters_view)
    #database_connection.query(create_isolates_with_global_filters_view, params=get_global_isolates_params())

    # TEST
    #test = "SELECT COUNT(*) FROM IsolatesFiltered"
    #res_test = database_connection.query(test)
    #print("Filtered Isolates Are: " + str(res_test))


def get_global_isolates_params():
    return {
        "global_region": st.session_state.global_region,
        "global_state": None
    }  # TODO


def replace_query_placeholders(selected_query_index, query, params):
    if selected_query_index in {1, 15}:
        query = query.replace("placeholder", params["placeholder"])
    if selected_query_index in {3, 4}:
        query = query.replace("hosts", params["hosts"])

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
    df = [df.loc[i: i + rows - 1, :] for i in range(0, len(df), rows)]
    return df


def fe_get_filtered_isolates_count(database_connection):
    return database_connection.query(get_filtered_isolates_count, params=get_global_isolates_params())


def fe_get_all_isolates_count(database_connection):
    return database_connection.query(get_isolates_count)


def fe_get_regions(database_connection):
    return database_connection.query(get_regions)


def get_locations_from_regions(database_connection, regions):

    locations_from_regions = \
        ("SELECT state FROM Location "
         "WHERE region IN (" + ",".join([f":{reg.strip()}" for reg in regions]) + ")")
    return database_connection.query(locations_from_regions, params={f"{reg.strip()}": reg for reg in regions})


query_mapping = {
        1: {
            'query': get_markers_literature,
            'params_func': params1
        },
        2: {
            'query': get_markers_by_human_percentage,
            'params_func': params2
        },
        3: {
            'query': get_markers_id_by_host_relative_presence,
            'params_func': params3
        },
        4: {
            'query': get_markers_id_by_host_relative_presence,
            'params_func': params4
        },
        5: {
            'query': get_marker_host_distribution,
            'params_func': params5
        },
        6: {
            'query': get_markers_location_distribution,
            'params_func': params6
        },
        7: {
            'query': get_most_common_markers_by_filters,
            'params_func': params7
        },
        8: {
            'query': get_host_by_n_of_markers,
            'params_func': params8
        },
        9: {
            'query': get_markers_by_relevance,
            'params_func': params9
        },
        10: {
            'query': get_segment_mutability_zones,
            'params_func': params10
        },
        11: {
            'query': get_mutability_peak_months,
            'params_func': params11
        },
        12: {
            'query': get_group_of_marker,
            'params_func': params12
        },
        13: {
            'query': get_effects_by_effect_metadata,
            'params_func': params13
        },
        14: {
            'query': get_marker_groups_by_effect,
            'params_func': params14
        },
        15: {
            'query': get_markers_over_time,
            'params_func': params15
        }
    }

