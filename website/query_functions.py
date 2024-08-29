import numpy as np
import yaml
import pandas
from matplotlib import pyplot as plt
from numpy.matlib import empty

from queries import *
import streamlit as st
from streamlit.components.v1 import html

st.set_page_config(layout="wide")

# RESOURCES
with open('website/resources/strings.yaml', 'r') as yaml_file:
    strings = yaml.safe_load(yaml_file)

db = st.connection(name="thesis", type="sql", url="sqlite:///website/data/thesis.db")
hosts = db.query(get_hosts)
markers = db.query(get_markers)
subtypes = db.query(get_subtypes)
segments = db.query(get_segments)
regions = db.query(get_regions)
states = db.query(get_states)


# FUNCTIONS
def run_query(query_selection):

    st.write(strings[f"explanation{query_selection}"], unsafe_allow_html=True)

    with st.form("query_inputs"):
        if query_selection == 1:
            placeholder, params = params1()
            query = get_markers_literature.replace("placeholder", placeholder)
        if query_selection == 2:
            params = params2()
            query = get_markers_by_human_percentage
        if query_selection == 3:
            params = params3()
            query = get_markers_id_by_host_relative_presence.replace("hosts", params["hosts"])
        if query_selection == 4:
            pass
        if query_selection == 5:
            params = params5()
            query = get_most_common_markers_by_filters
        if query_selection == 6:
            params = params6()
            query = get_host_by_n_of_markers

        submitted = st.form_submit_button("Submit")
        if submitted:

            result = db.query(query, params=params)
            graph = None

            if query_selection == 3:
                result = manip_result3(result, params)
                graph = graph3(result, params)
            if query_selection == 6:
                graph = graph6(result)

            return result, graph

    return None, None


# QUERIES' FUNCTIONS
def params1():

    """def update_markers(selected):
        marker_names = ', '.join([f"'{marker}'" for marker in selected_markers])
        query = \
            ("WITH SelectedMarkersIds AS ("
             "SELECT DISTINCT marker_id "
             "FROM Marker "
             f"WHERE name in ({marker_names})), "
             ""
             "PossibleGroups AS ("
             "SELECT marker_group_id "
             "FROM MarkerToGroup "
             "WHERE marker_id IN (SELECT * FROM SelectedMarkersIds) "
             "GROUP BY marker_group_id "
             "HAVING COUNT(DISTINCT marker_id) = (SELECT COUNT(DISTINCT marker_id) FROM SelectedMarkersIds)), "
             ""
             "SelectableMarkers AS ("
             "SELECT DISTINCT marker_id "
             "FROM MarkerToGroup "
             "WHERE marker_group_id IN (SELECT * FROM PossibleGroups) "
             "AND marker_id NOT IN (SELECT * FROM SelectedMarkersIds))"
             ""
             "SELECT DISTINCT marker.name "
             "FROM Marker marker "
             "JOIN SelectableMarkers selectableMarkers ON marker.marker_id = selectableMarkers.marker_id")
        new_options = db.query(query)
        return new_options"""

    selected_markers = st.multiselect(label=strings["param_label1a"], options=markers)

    placeholder = ', '.join(f":{marker.replace(":", "")}" for marker in selected_markers)
    params = {f"{marker.replace(":", "")}": marker for marker in selected_markers}
    return placeholder, params


def params2():

    l_col, r_col = st.columns(2)
    with l_col:
        subtype = st.selectbox(label=strings["param_label2a"],
                               options=["H5N1"])  # [sub["name"] for _, sub in subtypes.iterrows()])
        min_perc = st.number_input(label=strings["param_label2c"], key=strings["param_label2c"],
                                   min_value=0.0, step=0.1, max_value=100.0)
        limit = st.number_input(label=strings["param_label2e"], key=strings["param_label2e"],
                                min_value=1, step=1, value=10000)
    with r_col:
        segment = st.selectbox(label=strings["param_label2b"],
                               options=segments)
        max_perc = st.number_input(label=strings["param_label2d"], key=strings["param_label2d"],
                                   min_value=0.0, step=0.1, max_value=100.0, value=100.0)
        min_n_instances = st.number_input(label=strings["param_label2f"], key=strings["param_label2f"],
                                          min_value=1, step=1)

    return {
        "subtype": subtype,
        "segment_type": segment,
        "min_perc": min_perc,
        "max_perc": max_perc,
        "limit": limit,
        "min_n_instances": min_n_instances
    }


def params3():

    host1 = st.selectbox(label=strings["param_label3a"],
                         options=hosts)
    host2 = st.selectbox(label=strings["param_label3b"],
                         options=hosts)

    other_hosts = st.multiselect(label=strings["param_label3c"], options=hosts, max_selections=5)

    return {
        "host1": host1,
        "host2": host2,
        "other_hosts": other_hosts,
        "hosts": f"'{host1}', '{host2}'{', ' if other_hosts else ""}{','.join([f"'{host}'" for host in other_hosts])}"
    }


def manip_result3(results_pre, params):
    pivot_result = results_pre.pivot(index='Marker', columns='host', values='percentage').reset_index()
    pivot_result['Diff'] = pivot_result[params["host2"]] - pivot_result[params["host1"]]
    sorted_result = pivot_result.sort_values(by='Diff', ascending=False)
    columns = list(sorted_result.columns)
    columns.remove(params["host1"])
    columns.insert(1, params["host1"])
    columns.remove(params["host2"])
    columns.insert(2, params["host2"])
    sorted_result = sorted_result[columns]
    return sorted_result


def graph3(result_df, params):

    df_sorted = result_df.head(5)
    names = df_sorted['Marker']
    host1_values = df_sorted[params["host1"]]
    host2_values = df_sorted[params["host2"]]
    diff_values = df_sorted["Diff"]

    # Bar width and positions
    bar_width = 0.25
    index = np.arange(len(names))

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot bars for host1, host2, and difference
    bars1 = ax.bar(index - bar_width, host1_values, bar_width, label=params["host1"], color='skyblue')
    bars2 = ax.bar(index, host2_values, bar_width, label=params["host2"], color='lightgreen')
    bars3 = ax.bar(index + bar_width, diff_values, bar_width, label='Diff', color='lightcoral')

    # Set the x-axis labels and title
    ax.set_xlabel('Marker')
    ax.set_ylabel('Percentage (%)')
    ax.set_title('Top 5 Entries: Host1, Host2, and Difference')
    ax.set_xticks(index)
    ax.set_xticklabels(names)
    ax.legend()

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45, ha='right')

    # Return the figure and axes
    return fig


# TODO: 4


def params5():

    l_col, r_col = st.columns(2)
    with l_col:
        subtype = st.selectbox(label=strings["param_label5a"],
                               options=["H5N1"])  # [sub["name"] for _, sub in subtypes.iterrows()])
    with r_col:
        segment = st.selectbox(label=strings["param_label5b"], options=segments)

    location = st.selectbox(label=strings["param_label5c"],
                            options=[None] + regions['region'].tolist()
                                    + [f"{row['region']} - {row['state']}" for _, row in states.iterrows()])
    host = st.selectbox(label=strings["param_label5d"], options=[None] + hosts['host'].tolist())

    if location:
        location = location.strip().split("-")
        region = location[0]
        state = location[1] if len(location) > 1 else None
    else:
        region = None
        state = None

    return {
        "subtype": subtype,
        "region": region,
        "segment_type": segment,
        "state": state,
        "host": host
    }


def params6():

    l_col, r_col = st.columns(2)
    with l_col:
        subtype = st.selectbox(label=strings["param_label6a"],
                               options=[None, "H5N1"])  # [sub["name"] for _, sub in subtypes.iterrows()])
    with r_col:
        segment = st.selectbox(label=strings["param_label6b"], options=[None] + segments["segment_type"].tolist())

    return {
        "subtype": subtype,
        "segment_type": segment,
    }


def graph6(result_df):

    df_sorted = result_df.sort_values(by='Distinct Markers Per Host', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(df_sorted['Host'], df_sorted['Distinct Markers Per Host'], color='skyblue')

    ax.set_xlabel('Host')
    ax.set_ylabel('Distinct Markers Per Host')
    ax.set_title('Top 10 Hosts by Distinct Markers')

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), va='bottom', ha='center')

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig
