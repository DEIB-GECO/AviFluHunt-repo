import yaml
from matplotlib import pyplot as plt

from queries import *
import streamlit as st

# RESOURCES
with open('website/resources/strings.yaml', 'r') as yaml_file:
    strings = yaml.safe_load(yaml_file)


db = st.connection(name="fluhunt", type="sql", url="sqlite:///website/data/fluhunt.db")


# DB ROWS
markers = db.query(get_markers)
segments = db.query(get_segments)
annotations = db.query(get_annotations)
hosts = db.query(get_hosts).sort_values("host")
states = db.query(get_states).sort_values("state")
regions = db.query(get_regions).sort_values("region")
effects = db.query("SELECT * FROM Effect")


def get_marker():
    marker = st.selectbox(label="Marker", options=markers)
    return {"marker": marker}


def params1():

    selected_markers = st.multiselect(label=strings["param_label1a"], options=markers)

    cleaned_markers = {marker.replace(":", "").replace("-", ""): marker for marker in selected_markers}
    placeholder_string = ', '.join(f":{key}" for key in cleaned_markers.keys())

    return {
        **cleaned_markers,
        "placeholder": placeholder_string
    }


def params2():

    l_col, r_col = st.columns(2)

    with l_col:
        subtype = st.selectbox(label=strings["param_label2a"],  options=["H5N1"])
        min_perc = st.number_input(label=strings["param_label2c"], key=strings["param_label2c"],
                                   min_value=0.0, step=0.1, max_value=100.0)
    with r_col:
        segment = st.selectbox(label=strings["param_label2b"], options=segments)
        max_perc = st.number_input(label=strings["param_label2d"], key=strings["param_label2d"],
                                   min_value=0.0, step=0.1, max_value=100.0, value=100.0)
        min_n_instances = st.number_input(label=strings["param_label2f"], key=strings["param_label2f"],
                                          min_value=1, step=1)

    return {
        "subtype": subtype,
        "segment_type": segment,
        "min_perc": min_perc,
        "max_perc": max_perc,
        "min_n_instances": min_n_instances
    }


def params3():

    host1 = st.selectbox(label=strings["param_label3a"], options=hosts)
    host2 = st.selectbox(label=strings["param_label3b"], options=hosts)
    other_hosts = st.multiselect(label=strings["param_label3c"], options=hosts, max_selections=5)

    return {
        "host1": host1,
        "host2": host2,
        "other_hosts": other_hosts,
        "hosts": f"'{host1}', '{host2}'{', ' if other_hosts else ""}{','.join([f"'{host}'" for host in other_hosts])}"
    }


def params4():

    host = st.selectbox(label=strings["param_label4a"], options=hosts)
    other_hosts = st.multiselect(label=strings["param_label4b"], options=hosts, max_selections=5)

    return {
        "host": host,
        "other_hosts": other_hosts,
        "hosts": f"'{host}'{', ' if other_hosts else ""}{','.join([f"'{host}'" for host in other_hosts])}"
    }


def params7():
    subtype = st.selectbox(label=strings["param_label7a"], options=["H5N1"])
    segment = st.selectbox(label=strings["param_label7b"], options=segments)
    host = st.selectbox(label=strings["param_label7d"], options=hosts)
    return {"subtype": subtype, "segment_type": segment, "host": host}


def params8():
    subtype = st.selectbox(label=strings["param_label8a"], options=["H5N1"])
    segment = st.selectbox(label=strings["param_label8b"], options=segments['segment_type'].tolist())
    return {"subtype": subtype, "segment_type": segment if segment else None}


def params9():
    min_perc = st.number_input(label=strings["param_label9a"], key=strings["param_label9a"],
                               min_value=0.0, step=0.1, max_value=100.0)
    max_perc = st.number_input(label=strings["param_label9b"], key=strings["param_label9b"],
                               min_value=0.0, step=0.1, max_value=100.0, value=100.0)
    return {"min_perc": min_perc, "max_perc": max_perc}


def with_query10(bins):
    select_statements = " UNION ALL\n".join(
        [f"SELECT {start} AS start_range, {end} AS end_range" for start, end in bins])
    with_query = f"WITH Bin AS (SELECT start_range, end_range FROM ({select_statements})), "
    return with_query


def params10():

    annotation_list = annotations['annotation_name'].tolist()
    annotation_list.remove("HA1")
    annotation_list.remove("HA2")

    subtype = st.selectbox(label=strings["param_label10a"], options=[None, "H5N1"])
    segment = st.selectbox(label=strings["param_label10b"], options=annotation_list)

    manual_tab, auto_tab = st.tabs([strings["param_tab10a"], strings["param_tab10b"]])
    with manual_tab:

        if 'num_inputs' not in st.session_state:
            st.session_state.num_inputs = 1

        start_col, end_col = st.columns(2)
        for i in range(st.session_state.num_inputs):
            with start_col:
                st.number_input(f"Start", key=f"start_{i + 1}", min_value=0, step=1)
            with end_col:
                st.number_input(f"End", key=f"end_{i + 1}", min_value=0, step=1)

    with auto_tab:

        bin_size = st.number_input(label=strings["param_label10c"], min_value=0, step=10, value=0)
        offset = st.number_input(label=strings["param_label10d"], min_value=0, step=1, value=0)

    if bin_size == 0:
        bins = None
    else:
        bins = [(i, i + bin_size) for i in range(offset, 1000 + offset, bin_size)][0:500]

    return {"subtype": subtype, "segment_type": segment if segment else None, "bins": bins}


def params11():
    subtype = st.selectbox(label=strings["param_label11a"], options=[None, "H5N1"])
    segment = st.selectbox(label=strings["param_label11b"], options=segments['segment_type'].tolist())
    min_n_instances = st.number_input(label=strings["param_label11e"], key=strings["param_label11e"],
                                      min_value=1, step=1)
    return {"subtype": subtype, "segment_type": segment, "min_n_instances": min_n_instances}


def params13():
    effect_host = st.selectbox(label=strings["param_label13a"], options=set([None] + effects["host"].tolist()))
    effect_drug = st.selectbox(label=strings["param_label13b"], options=set([None] + effects["drug"].tolist()))
    return {"host": effect_host, "drug": effect_drug}


def params14():
    effect_full = st.selectbox(label=strings["param_label14a"], options=effects)
    return {"effect_full": effect_full}


def params15():
    selected_markers = st.multiselect(label=strings["param_label15a"], options=markers, max_selections=10)
    cleaned_markers = {marker.replace(":", "").replace("-", ""): marker for marker in selected_markers}
    placeholder_string = ', '.join(f":{key}" for key in cleaned_markers.keys())
    return {"placeholder": placeholder_string}


def manip_result3(results_pre, params):
    pivot_result = results_pre.pivot(index='Marker', columns='host', values='percentage').reset_index()
    pivot_result[f'Diff {params["host1"]} - {params["host2"]}'] = (
            pivot_result[params["host1"]] - pivot_result[params["host2"]])
    sorted_result = pivot_result.sort_values(by=f'Diff {params["host1"]} - {params["host2"]}', ascending=False)
    columns = list(sorted_result.columns)
    columns.remove(params["host1"])
    columns.insert(1, params["host1"])
    columns.remove(params["host2"])
    columns.insert(2, params["host2"])
    sorted_result = sorted_result[columns]
    return sorted_result

def manip_result4(results_pre, params):
    pivot_result = results_pre.pivot(index='Marker', columns='host', values='percentage').reset_index()
    sorted_result = pivot_result.sort_values(by=params["host"], ascending=False)
    columns = list(sorted_result.columns)
    columns.remove(params["host"])
    columns.insert(1, params["host"])
    sorted_result = sorted_result[columns]
    sorted_result.columns = [col + " %" if col != 'Marker' else col for col in sorted_result.columns]
    return sorted_result

"""def graph3(result_df, params):

    df_sorted = result_df.head(5)
    names = df_sorted['Marker']
    host1_values = df_sorted[params["host1"]]
    host2_values = df_sorted[params["host2"]]
    diff_values = df_sorted[f'Diff {params["host1"]} - {params["host2"]}']

    # Bar width and positions
    bar_width = 0.25
    index = np.arange(len(names))

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Plot bars for host1, host2, and difference
    bars1 = ax.bar(index - bar_width, host1_values, bar_width, label=params["host1"], color='skyblue')
    bars2 = ax.bar(index, host2_values, bar_width, label=params["host2"], color='lightgreen')
    bars3 = ax.bar(index + bar_width, diff_values, bar_width, label=f'Diff {params["host1"]} - {params["host2"]}', color='lightcoral')

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

    return plt.gcf()"""


def plot_data(result_df, sort_column, plot_column, top_n=20, label_column=None, plot_type='barh', title='',
              xlabel='', ylabel='', color='skyblue', is_bar=True, show_values=False, rotation=0):
    """
    Generalized function for plotting graphs with sorting, labeling, and value display.

    Parameters:
    - result_df: DataFrame containing the data
    - sort_column: Column name to sort the DataFrame by
    - plot_column: Column name to plot
    - top_n: Number of top rows to display (default: 20)
    - label_column: Column name for the labels (e.g., Host, State, etc.)
    - plot_type: Type of plot ('barh', 'bar', 'line') (default: 'barh')
    - title: Title of the plot
    - xlabel: X-axis label
    - ylabel: Y-axis label
    - color: Color of the bars or lines (default: 'skyblue')
    - is_bar: Boolean indicating whether it's a bar plot (default: True)
    - show_values: Boolean to show the values on bars (default: False)
    - rotation: Angle for x-tick labels (default: 0)
    """

    # Sort the DataFrame by the specified column and select the top N rows
    df_sorted = result_df.sort_values(by=sort_column, ascending=False).head(top_n)

    # Create the plot
    plt.figure(figsize=(12, 8))

    if plot_type == 'barh' and is_bar:
        plt.barh(df_sorted[label_column], df_sorted[plot_column], color=color)
        plt.gca().invert_yaxis()  # Invert y-axis to have the highest value on top
    elif plot_type == 'bar' and is_bar:
        bars = plt.bar(df_sorted[label_column], df_sorted[plot_column], color=color)
        if show_values:
            for bar in bars:
                yval = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2, yval, int(yval), va='bottom', ha='center')
    elif plot_type == 'line':
        for marker in df_sorted['Marker'].unique():
            subset = df_sorted[df_sorted['Marker'] == marker]
            plt.plot(subset['Year'], subset['Percentage'], marker='o', label=marker)

    # Customize the plot
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    plt.xticks(rotation=rotation)

    # Show the legend for line plots
    if plot_type == 'line':
        plt.legend(title='Markers', loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=5, frameon=False)

    plt.tight_layout()

    return plt.gcf()


