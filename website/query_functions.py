import yaml
import pandas
from queries import *
import streamlit as st
from streamlit.components.v1 import html

# RESOURCES
with open('website/resources/strings.yaml', 'r') as yaml_file:
    strings = yaml.safe_load(yaml_file)


# FUNCTIONS
def run_query(db, query_selection):

    st.write(strings[f"explanation{query_selection}"], unsafe_allow_html=True)
    query = get_markers_literature  # TODO: change based on selection

    with st.form("query_inputs"):
        if query_selection == 1:
            placeholder, params = params1(db)
            query = query.replace("placeholder", placeholder)

        submitted = st.form_submit_button("Submit")
        if submitted:
            result = db.query(query, params=params)
            return result

    return None


# QUERIES' PARAMS
def params1(db):

    markers = db.query(get_markers)
    selected_markers = st.multiselect(label=strings["param_label1a"], options=markers)

    placeholder = ', '.join(f":{marker.replace(":", "")}" for marker in selected_markers)
    params = {f"{marker.replace(":", "")}": marker for marker in selected_markers}
    return placeholder, params
