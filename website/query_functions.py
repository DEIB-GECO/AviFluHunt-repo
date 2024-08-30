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
            params = params4()
            query = get_markers_id_by_host_relative_presence.replace("hosts", params["hosts"])
        if query_selection == 5:
            params = params5()
            query = get_marker_host_distribution
        if query_selection == 6:
            params = params6()
            query = get_markers_location_distribution
        if query_selection == 7:
            params = params7()
            query = get_most_common_markers_by_filters
        if query_selection == 8:
            params = params8()
            query = get_host_by_n_of_markers
        if query_selection == 9:
            params = params9()
            query = get_markers_by_relevance
        if query_selection == 10:
            params = params10()
            query = with_query10(params["bins"]) + get_segment_mutability_zones
        if query_selection == 11:
            pass  # TODO
        if query_selection == 12:
            params = params12()
            query = get_group_of_marker
        if query_selection == 13:
            params = params13()
            query = get_effects_by_effect_metadata
        if query_selection == 14:
            params = params14()
            query = get_marker_groups_by_effect

        submitted = st.form_submit_button("Submit")
        if submitted:

            result = db.query(query, params=params)
            graph = None

            if query_selection == 3:
                result = manip_result3(result, params)
                graph = graph3(result, params)
            if query_selection == 4:
                result = manip_result4(result, params)
                graph = graph4(result, params)
            if query_selection == 5:
                graph = graph5(result, params)
            if query_selection == 6:
                graph = graph6(result)
            if query_selection == 9:
                graph = graph9(result)
            if query_selection == 10:
                st.session_state.num_inputs = 1

            return result, graph

    # Custom behaviour
    if query_selection == 10:
        if st.button("Add input"):
            st.session_state.num_inputs += 1

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


def params4():

    host = st.selectbox(label=strings["param_label4a"], options=hosts)
    other_hosts = st.multiselect(label=strings["param_label4b"], options=hosts, max_selections=5)

    return {
        "host": host,
        "other_hosts": other_hosts,
        "hosts": f"'{host}'{', ' if other_hosts else ""}{','.join([f"'{host}'" for host in other_hosts])}"
    }


def manip_result4(results_pre, params):
    pivot_result = results_pre.pivot(index='Marker', columns='host', values='percentage').reset_index()
    sorted_result = pivot_result.sort_values(by=params["host"], ascending=False)
    columns = list(sorted_result.columns)
    columns.remove(params["host"])
    columns.insert(1, params["host"])
    sorted_result = sorted_result[columns]
    return sorted_result


def graph4(result_df, params):

    top_10_df = result_df.head(10)
    fig, ax = plt.subplots(figsize=(14, 8))

    num_markers = len(top_10_df)
    num_hosts = len(top_10_df.columns) - 1
    bar_width = 0.8 / num_hosts
    index = range(num_markers)
    colors = ['r', 'g', 'b', 'c', 'm', 'y']

    for i, host in enumerate(top_10_df.columns[1:]):  # Skip 'marker' column
        offset = (i - (num_hosts - 1) / 2) * bar_width
        ax.bar([p + offset for p in index], top_10_df[host], bar_width, label=host, color=colors[i % len(colors)])

    ax.set_xlabel('Marker')
    ax.set_ylabel('Values')
    ax.set_title('Top 10 Markers Ordered by ' + params["host"] + "%")
    ax.set_xticks(index)
    ax.set_xticklabels(top_10_df['Marker'], rotation=45)
    ax.legend(title='Hosts')
    ax.grid(True, linestyle='--', alpha=0.7)

    return plt.gcf()


def params5():
    marker = st.selectbox(label=strings["param_label5a"], options=markers)
    return {"marker": marker}


def graph5(result_df, params):

    df_sorted = result_df.sort_values(by='#', ascending=False)

    # Select the top 20 rows
    top_20 = df_sorted.head(20)

    # Plotting
    plt.figure(figsize=(12, 8))
    plt.barh(top_20['Host'], top_20['#'], color='skyblue')
    plt.xlabel('#')
    plt.ylabel('Host')
    plt.title('Top Hosts')
    plt.gca().invert_yaxis()  # Optional: To have the highest values at the top
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Return the matplotlib figure object
    return plt.gcf()


def params6():
    marker = st.selectbox(label=strings["param_label6a"], options=markers)
    region = st.selectbox(label=strings["param_label6b"], options=[None] + regions["region"].tolist())
    return {
        "marker": marker,
        "region": region
    }


def graph6(result_df):

    df_sorted = result_df.sort_values(by='Normalized Percentage', ascending=False)

    # Select the top 20 rows
    top_20 = df_sorted.head(20)

    # Plotting
    plt.figure(figsize=(12, 8))
    plt.barh(top_20['State'], top_20['Normalized Percentage'], color='skyblue')
    plt.xlabel('Normalized Percentage')
    plt.ylabel('State')
    plt.title('Top States')
    plt.gca().invert_yaxis()  # Optional: To have the highest values at the top
    plt.grid(axis='x', linestyle='--', alpha=0.7)

    # Return the matplotlib figure object
    return plt.gcf()


def params7():

    l_col, r_col = st.columns(2)
    with l_col:
        subtype = st.selectbox(label=strings["param_label7a"],
                               options=["H7N1"])  # [sub["name"] for _, sub in subtypes.iterrows()])
    with r_col:
        segment = st.selectbox(label=strings["param_label7b"], options=segments)

    location = st.selectbox(label=strings["param_label7c"],
                            options=[None] + regions['region'].tolist()
                                    + [f"{row['region']} - {row['state']}" for _, row in states.iterrows()])
    host = st.selectbox(label=strings["param_label7d"], options=[None] + hosts['host'].tolist())

    if location:
        location = location.split(" - ")
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


def params8():

    l_col, r_col = st.columns(2)
    with l_col:
        subtype = st.selectbox(label=strings["param_label8a"],
                               options=[None, "H5N1"])  # [sub["name"] for _, sub in subtypes.iterrows()])
    with r_col:
        segment = st.selectbox(label=strings["param_label8b"], options=[None] + segments["segment_type"].tolist())

    return {
        "subtype": subtype,
        "segment_type": segment,
    }


def graph8(result_df):

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


def params9():

    l_col, r_col = st.columns(2)
    with l_col:
        min_perc = st.number_input(label=strings["param_label9a"], key=strings["param_label9a"],
                                   min_value=0.0, step=0.1, max_value=100.0)
    with r_col:
        max_perc = st.number_input(label=strings["param_label9b"], key=strings["param_label9b"],
                                   min_value=0.0, step=0.1, max_value=100.0, value=100.0)

    limit = st.number_input(label=strings["param_label9c"], key=strings["param_label9c"],
                            min_value=1, step=1, value=10000)

    return {
        "min_perc": min_perc,
        "max_perc": max_perc,
        "limit": limit
    }


def graph9(result_df):

    df_sorted = result_df.sort_values(by='Percentage', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(12, 8))
    bars = ax.bar(df_sorted['Marker'], df_sorted['Percentage'], color='skyblue')

    ax.set_xlabel('Marker')
    ax.set_ylabel('Markers By Percentage')

    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), va='bottom', ha='center')

    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    return fig


def params10():

    if 'num_inputs' not in st.session_state:
        st.session_state.num_inputs = 1

    start_col, end_col = st.columns(2)
    for i in range(st.session_state.num_inputs):
        with start_col:
            st.number_input(f"Start", key=f"start_{i + 1}", min_value=0, step=1)
        with end_col:
            st.number_input(f"End", key=f"end_{i + 1}", min_value=0, step=1)

    return {
        "bins": [(st.session_state[f"start_{i+1}"], st.session_state[f"end_{i+1}"]) for i in range(st.session_state.num_inputs)]
    }


def with_query10(bins):
    select_statements = " UNION ALL\n".join(
        [f"SELECT {start} AS start_range, {end} AS end_range" for start, end in bins])
    with_query = f"WITH Bin AS (SELECT start_range, end_range FROM ({select_statements})), "
    return with_query


# TODO 11


def params12():
    marker = st.selectbox(label=strings["param_label12a"], options=markers)
    return {"marker_name": marker}


def params13():

    effect_hosts = db.query("SELECT DISTINCT host FROM Effect WHERE host != ''")
    effect_drugs = db.query("SELECT DISTINCT drug FROM Effect WHERE drug != ''")

    effect_host = st.selectbox(label=strings["param_label13a"],
                               options=[None] + effect_hosts["host"].tolist())
    effect_drug = st.selectbox(label=strings["param_label13b"],
                               options=[None] + effect_drugs["drug"].tolist())

    return {
        "host": effect_host,
        "drug": effect_drug
    }


def params14():
    effects = db.query("SELECT DISTINCT effect_full FROM Effect")
    effect_full = st.selectbox(label=strings["param_label14a"],
                               options=effects)
    return {"effect_full": effect_full}
