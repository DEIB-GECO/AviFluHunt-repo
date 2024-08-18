import pandas
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
    text["query_two"]: display_query_2,
    text["query_three"]: display_query_3,
    text["query_four"]: display_query_4,
    text["query_five"]: display_query_5,
    text["query_six"]: display_query_6,
    text["query_seven"]: display_query_7,
    text["query_eight"]: display_query_8,
    text["query_nine"]: display_query_9,
    text["query_ten"]: display_query_10,
    text["query_eleven"]: display_query_11,
}

st.markdown(
    """
    <div id="div"></div>
    <script>
        alert("Hello World!");
    </script>
    """,
    unsafe_allow_html=True,)
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
        st.write("TODO", unsafe_allow_html=True)
    else:
        st.dataframe(st.session_state.query_results, use_container_width=True)
