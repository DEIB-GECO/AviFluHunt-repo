import pandas
import streamlit

from query_helper_functions import *
from streamlit.components.v1 import html


display_query_dict = {
    text["query_one_label"]: display_query_1,
    text["query_two_label"]: display_query_2,
    text["query_three_label"]: display_query_3,
    text["query_four_label"]: display_query_4,
    text["query_five_label"]: display_query_5,
    text["query_six_label"]: display_query_6,
    text["query_seven_label"]: display_query_7,
    text["query_eight_label"]: display_query_8,
    text["query_nine_label"]: display_query_9,
    text["query_ten_label"]: display_query_10,
}

with open('website/resources/text.yaml', 'r') as file:
    text = yaml.safe_load(file)

st.set_page_config(layout="wide")


# BACKEND

db = st.connection(name="thesis", type="sql", url="sqlite:///website/data/thesis.db")
if 'query_results' not in st.session_state:
    st.session_state.query_results = pandas.DataFrame()

if 'error_message' not in st.session_state:
    st.session_state.error_message = text["no_result"]


def run_query(query, params):

    query_results = db.query(query, params=params)
    st.session_state.query_results = query_results


# FRONTEND

st.write(text["website_name"], unsafe_allow_html=True)
query_tab, readme_tab = st.tabs(["Run Query", "About"])

with readme_tab:

    for i in ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]:
        label = text[f"query_{i}_label"]
        explanation = text[f"query_{i}_explanation"]

        # Create two columns
        col1, col2 = st.columns([1, 2])  # Adjust the width ratio of columns as needed

        # Display the label and explanation in their respective columns
        with col1:
            st.markdown(f"**{label}:**", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div style='border-left: 1px solid gray; padding-left: 10px;'>{explanation}</div>",
                        unsafe_allow_html=True)

        # Add a horizontal line for separation between rows
        st.markdown("<hr>", unsafe_allow_html=True)

    st.write('')
    st.write(text["ack"])

with query_tab:

    query_col, space, results_col = st.columns([0.35, 0.10, 0.55])

    with query_col:

        with st.container():

            query_selection = st.selectbox(label=text["query_select_label"],
                                           options=display_query_dict.keys(), )
            query_sql, query_inputs, error = display_query_dict[query_selection](db)
            st.session_state.error_message = error
            st.markdown(text["css"], unsafe_allow_html=True)
            st.button(label=text["submit_button"], on_click=run_query, args=[query_sql, query_inputs])

    with results_col:

        if st.session_state.query_results.empty:
            st.write(st.session_state.error_message, unsafe_allow_html=True)
            st.markdown("""<style>div [data-testid=stImage]{text-align: center;display: block;
                        margin-left: auto;margin-right: auto;width: 100%;}</style>""", unsafe_allow_html=True)
        else:
            st.write(text["result"], unsafe_allow_html=True)
            st.dataframe(st.session_state.query_results, use_container_width=True)

