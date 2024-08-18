import pandas
import streamlit

from query_helper_functions import *
from streamlit.components.v1 import html


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
    text["query_one_label"]: display_query_1,
    text["query_two_label"]: display_query_2,
    text["query_three_label"]: display_query_3,
    text["query_four_label"]: display_query_4,
    text["query_five"]: display_query_5,
    text["query_six_label"]: display_query_6,
    text["query_seven_label"]: display_query_7,
    text["query_eight_label"]: display_query_8,
    text["query_nine_label"]: display_query_9,
    text["query_ten_label"]: display_query_10,
}

with query_col:

    #st.write(text["website_name"], unsafe_allow_html=True)
    #st.write(text["welcome_message"], unsafe_allow_html=True)

    with st.container():

        st.write(text["query_select_label"], unsafe_allow_html=True)
        query_selection = st.selectbox(label=text["query_select_label"], label_visibility="collapsed",
                                       options=display_query_dict.keys(),)
        query_sql, query_inputs = display_query_dict[query_selection](db)
        st.markdown(text["css"], unsafe_allow_html=True)
        st.button(label=text["submit_button"], on_click=run_query, args=[query_sql, query_inputs])

with results_col:
    if st.session_state.query_results.empty:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.write(text["no_result"], unsafe_allow_html=True)
        st.markdown(
            """
            <style>
                div [data-testid=stImage]{
                    text-align: center;
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                    width: 100%;
                }
            </style>
            """, unsafe_allow_html=True
        )
        st.image("https://i.pinimg.com/originals/6d/a8/78/6da878cf7299317b2bd88c7471111626.gif")
    else:
        st.write(text["result"], unsafe_allow_html=True)
        st.dataframe(st.session_state.query_results, use_container_width=True)
