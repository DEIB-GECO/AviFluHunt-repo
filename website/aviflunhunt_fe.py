from streamlit_option_menu import option_menu
from fluhunter_web_helpers import *
from pygwalker.api.streamlit import StreamlitRenderer


def build_top_bar(global_config):
    st.write(global_config.text_resources["website_name"], unsafe_allow_html=True)


def build_global_container(global_config):

    with st.container(key="global_container"):
        build_global_filters_overlay_container(global_config)


def build_global_filters_overlay_container(global_config):
    with st.container(key="global_filters_overlay_container"):

        selected = build_settings_menu()

        if selected == "Settings" and st.session_state["menu_selected"]:
            pass#filters_overlay_container(global_config)
        if selected == "About":
            pass# TODO
        else:
            st.session_state["menu_selected"] = True


def build_settings_menu():
    return option_menu(
            menu_title=None,
            options=["Settings", "About"],
            icons=["gear", "info-circle"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "margin": "0", "float": "right",
                              "background-color": "transparent"},
                "nav": {"justify-content": "flex-end"},
                "nav-item": {"flex-basis": "auto!important", "flex-grow": "0!important", "float": "right"},
                "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px",
                             "font-weight": "bold", "color": "white"},
                "nav-link-selected": {"background-color": "transparent", "color": "white"},
            }
        )


@st.dialog("global_settings")
def filters_overlay_container(global_config):
    with st.container(key="global_filters_overlay"):
        st.markdown("Hello World 👋")
        build_location_global_filter(global_config)


def build_location_global_filter(global_config):
    with st.container(key="location_global_filter"):
        regions = {
            "All regions": None,
            "Europe": "Europe",
            "Asia": "Asia"
        }  # global_config.database_connection.query(get_regions())
        region = st.selectbox(
            label="Region",  # TODO: global strings
            options=regions, # TODO UGLY
            key="global_region"
            )
        build_location_state_filter(region)


def build_location_state_filter(region):
    location = st.selectbox(
            label="Location",  # TODO: global strings
            options=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", region],
            on_change=lambda: None,
            # #key=f"query_selection{st.session_state.current_query_type}",
            )


def build_query_bar(query_types):
    with st.container(key="query_type_selector"):
        query_type = build_query_type_menu([*query_types])
        if query_type:
            st.session_state.current_query_type = query_type


def build_query_type_menu(query_types):
    return option_menu(
            menu_title=None,
            options=query_types,
            icons=["file-earmark-richtext-fill", "", "funnel", "arrow-left-right"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
            styles={
                "container": {"padding": "0!important", "margin": "0", "float": "right",
                              "background-color": "transparent"},
                "nav": {"justify-content": "flex-end"},
                "nav-item": {"flex-basis": "auto!important", "flex-grow": "0!important", "float": "right"},
                "nav-link": {"font-size": "14px", "text-align": "left", "margin": "0px",
                             "font-weight": "bold", "color": "white"},
                "nav-link-selected": {"background-color": "white", "color": "black"},
            }
        )


def build_main_page(global_config):

    with st.container(key="main_page"):
        build_query_bar(global_config.queries.keys())
        selected_query_index = build_query_selector(global_config)
        build_left_column(global_config, selected_query_index)
        build_results_container(selected_query_index)


def build_left_column(global_config, selected_query_index):
    with st.container(key="left_column"):
        build_query_input_form(selected_query_index, global_config)
        #return selected_query_index


def build_query_selector(global_config):

    options = {
        global_config.text_resources[f"label{query_index}"]: query_index
        for query_index in global_config.queries[st.session_state.current_query_type]
    }

    with st.container(key="query_selector"):
        st.html("<h3 id='query_sel_label'>Query</h3>")
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
        table_tab, graph_tab, explore_tab = st.tabs(["Tabular"] + ["Graph"] + ["Explore Data"])
        with table_tab:
            build_table_tab(selected_query_index)
        with graph_tab:
            build_graph_tab()
        with explore_tab:
            build_explore_tab(selected_query_index)


def build_graph_tab():
    with st.container(key="graph_tab"):
        pass


def build_table_tab(selected_query_index):
    with st.container(key="table_tab"):
        batch_size, current_page = build_table_settings(selected_query_index)
        build_table(batch_size, current_page)
        build_download_button()


def build_table_settings(selected_query_index):
    with st.container(key="table_settings"):

        col_order, col_strategy, res_per_page_col, current_page_col = st.columns([1, 1, 1, 1])

        col_order.selectbox('Order by', set_default_table_order(selected_query_index, st.session_state.result.columns),
                            key='order_column', on_change=lambda: order_table(st.session_state.result))

        col_strategy.selectbox('Strategy', ['Descending', 'Ascending'], key='order_ascending',
                               on_change=lambda: order_table(st.session_state.result))
        with res_per_page_col:
            batch_size = st.selectbox("Page Size", options=[10, 25, 50])

        with current_page_col:
            total_pages = max(int(len(st.session_state.result) / batch_size) + 1, 1)
            current_page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)

        return batch_size, current_page


def build_table(batch_size, current_page):
    with st.container(key="table_container"):
        if st.session_state.result is not None and not st.session_state.result.empty:
            pagination = st.container()
            pages = split_frame(st.session_state.result, batch_size)
            pagination.table(pages[current_page - 1])


def build_download_button():
    with st.container(key="download_button"):
        st.download_button(label="Download data as CSV", data=st.session_state.result.to_csv(index=False).encode(),
                           file_name="data.csv", mime="text/csv")


def build_explore_tab(selected_query_index):
    with st.container(key="explore_tab"):
        if st.session_state.result is not None and not st.session_state.result.empty:
            query_pyg_config_file = get_pygwalker_default_config(selected_query_index)

            def get_pyg_renderer() -> "StreamlitRenderer":
                return StreamlitRenderer(st.session_state.result, appearance="dark",
                                         spec_io_mode="r", spec=query_pyg_config_file)

            renderer = get_pyg_renderer()
            renderer.explorer()
