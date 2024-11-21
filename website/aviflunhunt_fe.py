from fluhunter_web_helpers import *
from pygwalker.api.streamlit import StreamlitRenderer


def build_top_bar(global_config):
    st.write(global_config.text_resources["website_name"], unsafe_allow_html=True)


def build_global_container(global_config):

    with st.container(key="global_container"):
        build_global_filters_overlay_container()
        build_query_bar(global_config.queries.keys())


def build_global_filters_overlay_container():
    with st.container(key="global_filters_overlay_container"):
        if st.button("TEST GLOBAL FILTERS"):
            filters_overlay_container()


@st.dialog("global_settings")
def filters_overlay_container():
    with st.container(key="global_filters_overlay"):
        st.markdown("Hello World 👋")


def build_query_bar(query_types):
    with st.container(key="query_type_selector"):
        for query_type in query_types:
            if st.button(query_type):
                st.session_state.current_query_type = query_type


def build_main_page(global_config):

    with st.container(key="main_page"):
        selected_query_index = build_query_selector(global_config)
        build_query_input_form(selected_query_index, global_config)
        build_results_container(selected_query_index)


def build_query_selector(global_config):

    options = {
        global_config.text_resources[f"label{query_index}"]: query_index
        for query_index in global_config.queries[st.session_state.current_query_type]
    }

    with st.container(key="query_selector"):
        return options[st.selectbox(
            label=global_config.text_resources["query_select_label"],
            options=options,
            on_change=lambda: None,
            # #key=f"query_selection{st.session_state.current_query_type}",
            label_visibility="collapsed")]


def build_query_input_form(query_selection, global_config):

    with st.container(key="query_inputs_container"):
        with st.form(f"query_inputs_{query_selection}"):
            st.write(global_config.text_resources["query_inputs_label"], unsafe_allow_html=True)
            query, params = get_query_and_params(query_selection, global_config.database_connection)
            if st.form_submit_button("Submit"):
                run_query(global_config.database_connection, query, params)


def get_query_and_params(selected_query_index, db):
    query_data = query_mapping[selected_query_index]
    query = query_data['query']
    params = query_data['params_func'](db)
    query = replace_query_placeholders(selected_query_index, query, params)
    return query, params


def build_results_container(selected_query_index):
    with (st.container(key="results_container")):
        graph_tab, table_tab, explore_tab = st.tabs(["Graph"] + ["Tabular"] + ["Explore Data"])
        with graph_tab:
            build_graph_tab()
        with table_tab:
            build_table_tab(selected_query_index)
        with explore_tab:
            build_explore_tab(selected_query_index)


def build_graph_tab():
    with st.container(key="graph_tab"):
        pass


def build_table_tab(selected_query_index):
    with st.container(key="table_tab"):
        build_table_settings(selected_query_index)
        build_table()


def build_table_settings(selected_query_index):
    with st.container(key="table_settings"):

        col_order, col_strategy = st.columns([1, 1])
        col_order.selectbox('Order by', set_default_table_order(selected_query_index, st.session_state.result.columns),
                            key='order_column', on_change=lambda: order_table(st.session_state.result))
        col_strategy.selectbox('Strategy', ['Descending', 'Ascending'], key='order_ascending',
                               on_change=lambda: order_table(st.session_state.result))


def build_table():
    with st.container(key="table_container"):
        if st.session_state.result is not None and not st.session_state.result.empty:
            st.download_button(label="Download data as CSV", data=st.session_state.result.to_csv(index=False).encode(),
                               file_name="data.csv", mime="text/csv")
            st.table(st.session_state.result.reset_index(drop=True))


def build_explore_tab(selected_query_index):
    with st.container(key="explore_tab"):
        if st.session_state.result is not None and not st.session_state.result.empty:
            query_pyg_config_file = get_pygwalker_default_config(selected_query_index)

            def get_pyg_renderer() -> "StreamlitRenderer":
                return StreamlitRenderer(st.session_state.result, appearance="dark",
                                         spec_io_mode="r", spec=query_pyg_config_file)

            renderer = get_pyg_renderer()
            renderer.explorer()
