from query_functions import *


# USEFUL FUNCTIONS
# TODO

# BACKEND

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
            query_selection = st.selectbox(label=strings["query_select_label"], options=[x for x in range(1, 10)],
                                           on_change=lambda: results_col.empty())
            result, graph = run_query(query_selection)
            with results_col:
                if graph:
                    st.pyplot(graph)
                st.table(result)


