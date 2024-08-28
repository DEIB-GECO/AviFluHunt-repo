from query_functions import *

st.set_page_config(layout="wide")

# USEFUL FUNCTIONS
# TODO

# BACKEND
db = st.connection(name="thesis", type="sql", url="sqlite:///website/data/thesis.db")

# FRONTEND
st.write(strings["website_name"], unsafe_allow_html=True)


query_tab, readme_tab = st.tabs(["Run Query", "About"])

with readme_tab:
    st.write('')
    st.write(strings["ack"])

with query_tab:

    query_col, space, results_col = st.columns([0.35, 0.05, 0.60])
    with query_col:

        with st.container():
            query_selection = st.selectbox(label=strings["query_select_label"], options=[x for x in range(1, 10)])
            result = run_query(db, query_selection)
            with results_col:
                st.dataframe(result, hide_index=True)


