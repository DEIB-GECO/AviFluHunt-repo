import pandas
import yaml
import streamlit as st
from query_helper_functions import *


with open('website/resources/text.yaml', 'r') as file:
    text = yaml.safe_load(file)

st.set_page_config(layout="wide")


##### BACKEND #####
db = st.connection(name="thesis", type="sql", url="sqlite:///website/data/thesis.db")
if 'query_results' not in st.session_state:
    st.session_state.query_results = pandas.DataFrame()


def run_query(query, params):

    query_results = db.query(query, params=params)
    st.session_state.query_results = query_results
        
        
##### FRONTEND #####

query_col, space, results_col = st.columns([0.35, 0.10, 0.55])

display_query_dict = {
    text["query_one"]: display_query_1,
}

with query_col:

    st.write(text["website_name"], unsafe_allow_html=True)
    st.write(text["welcome_message"], unsafe_allow_html=True)

    with st.container():

        query_selection = st.selectbox(label=text["query_select_label"],
                                       options=display_query_dict.keys())
        st.write(text["query_label"])
        query_sql, query_inputs = display_query_dict[query_selection](db)
        st.button(label=text["submit_button"], on_click=run_query, args=[query_sql, query_inputs])

with results_col:
    st.dataframe(st.session_state.query_results, use_container_width=True)
    