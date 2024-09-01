from query_functions import *

# FRONTEND
N_QUERIES = 15
queries = {strings[f"label{x}"]: x for x in range(1, N_QUERIES)}

st.write(strings["website_name"], unsafe_allow_html=True)

query_tab, readme_tab = st.tabs(["Run Query", "About"])

with readme_tab:
    for i in range(1, N_QUERIES):
        label = strings[f"label{i}"]
        explanation = strings[f"explanation{i}"]
        labels, explanations = st.columns([1, 2])
        with labels:
            st.markdown(f"**{label}:**", unsafe_allow_html=True)
        with explanations:
            st.markdown(f"<div style='border-left: 1px solid gray; padding-left: 10px;'>{explanation}</div>",
                        unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

    st.write('')
    st.write(strings["ack"])

with query_tab:

    query_col, space, results_col = st.columns([0.35, 0.05, 0.60])
    with query_col:

        with st.container():
            query_selection = st.selectbox(label=strings["query_select_label"],
                                           options=queries.keys(),
                                           on_change=lambda: results_col.empty(),
                                           key="query_selection")
            result, graph, error = run_query(queries[st.session_state.query_selection])
            with results_col:
                if graph:
                    st.pyplot(graph)

                if result is not None and not result.empty:
                    st.table(result)
                    st.download_button(label="Download data as CSV", data=result.to_csv(index=False).encode(),
                                       file_name="data.csv", mime="text/csv")
                else:
                    if error is not None:
                        st.write(error)


