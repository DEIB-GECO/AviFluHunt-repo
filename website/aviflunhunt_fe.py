import datetime
import io
import taxoniq
import matplotlib

matplotlib.use('Agg')
from streamlit_option_menu import option_menu
from fluhunter_web_helpers import *
from pygwalker.api.streamlit import StreamlitRenderer


def build_top_bar(global_config):
    st.write(global_config.text_resources["website_name"], unsafe_allow_html=True)


def build_global_container(global_config):

    with st.container(key="global_container"):
        build_global_filters_overlay_container(global_config)


def handle_global_button_click(button_name, global_config):
    if button_name == "Settings":
        filters_overlay_container(global_config)
    elif button_name == "About":
        about_overlay_container()
    elif button_name == "Taxonomy Tree":
        taxonomy_tree_overlay_container(global_config)


def build_global_filters_overlay_container(global_config):

    with st.container():
        build_settings_menu(global_config)


def build_settings_menu(global_config):

    tax, settings, about = st.columns([1, 1, 1])

    with tax:
        if st.button("Taxonomy Tree"):
            handle_global_button_click("Taxonomy Tree", global_config)

    with settings:
        if st.button("Global Settings", key="settings_button"):
            handle_global_button_click("Settings", global_config)

    with about:
        if st.button("About", key="about_button"):
            handle_global_button_click("About", global_config)


@st.dialog("Global Settings")
def filters_overlay_container(global_config):
    with st.container(key="global_filters_overlay"):

        left_col, right_col = st.columns(2)

        with left_col:
            build_location_global_filter(global_config)

        with right_col:
            build_date_global_filter(global_config)

        build_isolates_remaining_information(global_config)


def build_location_global_filter(global_config):
    with st.container(key="location_global_filter"):

        st.write("🌍 Location")
        build_location_region_filter(global_config)
        build_location_state_filter(global_config)


def update_g_regions():
    st.session_state["g_regions"] = st.session_state["g_reg_ms"]


def build_location_region_filter(global_config):

    regions = fe_get_regions(global_config.database_connection)['region'].tolist()
    selected_regions = st.multiselect(label="Region", options=regions, default=st.session_state["g_regions"])

    st.session_state.g_regions = selected_regions
    st.session_state.global_regions = {f"{region.replace(" ", "")}": region for region in selected_regions}


def build_location_state_filter(global_config):

    states = get_locations_from_regions(global_config.database_connection,
                                        st.session_state.global_regions)['state'].tolist()
    selected_states = st.multiselect(label="Location", options=states)
    st.session_state.global_states = {f"{re.sub(r'[^a-zA-Z]', '', state)}": state for state in selected_states}


def build_date_global_filter(global_config):
    with st.container(key="date_global_filter"):

        st.write("📅 Timeframe")
        min_year = global_config.database_connection.query(get_min_year)["min_year"].tolist()[0]

        # Set default values if they are not already in session state
        if "global_start_date" not in st.session_state:
            st.session_state.global_start_date = datetime.date(min_year, 1, 1)
        if "global_end_date" not in st.session_state:
            st.session_state.global_end_date = datetime.date.today()

        # Create the date input fields
        start_date = st.date_input('Start Date', st.session_state.global_start_date,
                                   min_value=datetime.date(min_year, 1, 1),
                                   max_value=datetime.date.today())
        end_date = st.date_input('End Date', st.session_state.global_end_date,
                                 min_value=datetime.date(min_year, 1, 1))

        # Store the selected dates in session_state
        st.session_state.global_start_date = start_date
        st.session_state.global_end_date = end_date

        # Store year and month separately
        st.session_state.global_start_year = start_date.year
        st.session_state.global_end_year = end_date.year
        st.session_state.global_start_month = start_date.month
        st.session_state.global_end_month = end_date.month


def build_isolates_remaining_information(global_config):

    st.html(f"<hr>")
    with st.container(key="isolates_remaining"):

        filtered_isolates = fe_get_filtered_isolates_count(global_config.database_connection)["count"].tolist()[0]
        all_isolates = fe_get_all_isolates_count(global_config.database_connection)["count"].tolist()[0]
        st.html(f"<h4 id='isolates_filtered_h4'>Considering {filtered_isolates} isolates out of {all_isolates}</h4>")
        if st.button("Close"):
            st.rerun()


@st.dialog("About")
def about_overlay_container():
    with st.container(key="about_overlay"):
        with open("website/resources/about.html", "r") as about:
            st.html(about.read())


@st.dialog("🦆 Taxonomy Tree Explorer")
def taxonomy_tree_overlay_container(global_config):
    with (st.container(key="taxonomy_tree_overlay")):

        data = [("Aves", 0, -1)] + \
               list(global_config.database_connection.query(get_taxonomy_tree).itertuples(index=False, name=None))

        # Convert list to a dictionary {parent_id: [(name, id)]}
        tree = {}
        for name, node_id, parent_id in data:
            if parent_id not in tree:
                tree[parent_id] = []
            tree[parent_id].append((name, node_id))

        with st.container(key="taxonomy_tree_search"):
            search_tax = st.text_input("Search:")

        def get_all_descendants(node_id, tree):
            descendants = []
            if node_id in tree:
                children = tree[node_id]
                for child_name, child_id in children:
                    descendants.append(child_name)
                    descendants.extend(get_all_descendants(child_id, tree))

            return descendants

        # Recursive function to display tree using expanders
        def display_tree(parent_id=None, indent=0, parent_in_search=False):

            if parent_id not in tree:
                return

            for name, node_id in tree[parent_id]:

                try:
                    ncbi_id = str(taxoniq.Taxon(scientific_name=name).tax_id)
                except:
                    ncbi_id = "unavailable"

                try:
                    common_name = f"({str(taxoniq.Taxon(scientific_name=name).common_name)})"
                except:
                    common_name = ""

                node_descendants = get_all_descendants(node_id, tree)
                node_descendants_ids = [str(taxoniq.Taxon(scientific_name=desc_name).tax_id)
                                        for desc_name in node_descendants]
                node_descendants_cn = []
                for node_descendant_id in node_descendants_ids:
                    try:
                        node_descendants_cn.append(taxoniq.Taxon(tax_id=node_descendant_id).common_name)
                    except:
                        continue

                show_node = (
                    search_tax == "" or parent_in_search or
                    search_tax.lower() in name.lower() or search_tax in ncbi_id or search_tax.lower() in common_name.lower() or
                    any(search_tax.lower() in tax.lower() for tax in node_descendants) or
                    any(search_tax in tax_id for tax_id in node_descendants_ids) or
                    any(search_tax.lower() in tax_child.lower() for tax_child in node_descendants_cn)
                )  # matching children

                if show_node:
                    toggle = st.toggle(f"&nbsp;{'&nbsp;' * indent} {name} {common_name} (ID: {ncbi_id})")
                    if toggle or \
                            ((any(search_tax.lower() in tax.lower() for tax in node_descendants) or
                             any(search_tax in tax_id for tax_id in node_descendants_ids) or
                             any(search_tax.lower() in tax_child.lower() for tax_child in node_descendants_cn)) and
                             search_tax != ""):
                        display_tree(node_id, indent + 8, search_tax.lower() in name.lower() or parent_in_search)

        display_tree(-1)  # Start from the root (None)


def build_query_bar(query_types):
    with st.container(key="query_type_selector"):
        query_type = build_query_type_menu([*query_types])
        if query_type:
            st.session_state.current_query_type = query_type


def reset_result():
    pass
    #st.session_state["result"] = None


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
            },
            on_change=reset_result(),
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
            on_change=reset_result,
            # #key=f"query_selection{st.session_state.current_query_type}",
            label_visibility="collapsed")]


def build_query_input_form(query_selection, global_config):

    with st.container(key="query_inputs_container"):

        if query_selection not in [1, 8, 12, 13, 14]:
            recap_global_filters(global_config)
        else:
            no_global_filters()

        if query_selection == 10:
            build_add_manual_for_10()

        st.write(global_config.text_resources["query_inputs_label"], unsafe_allow_html=True)

        if query_selection in [3, 4, 7]:
            st.write("<br>", unsafe_allow_html=True)
            if st.button("📖 Taxonomy Tree Lookup "):
                handle_global_button_click("Taxonomy Tree", global_config)
            st.write("<br>", unsafe_allow_html=True)

        with st.form(f"query_inputs_{query_selection}"):
            query, params = get_query_and_params(query_selection)
            if st.form_submit_button("Submit"):
                run_query(global_config.database_connection, query_selection, query, params)
                get_result_graph(query_selection)


def build_add_manual_for_10():
    with st.container(key="add_manual_input_container"):
        if 'num_inputs' not in st.session_state:
            st.session_state.num_inputs = 1
        st.number_input("Number of regions:", min_value=0, step=1, key="num_inputs")


def recap_global_filters(global_config):

    global_filters = {
        "global_start_year": st.session_state.global_start_year,
        "global_end_year": st.session_state.global_end_year,
        "global_start_month": st.session_state.global_start_month,
        "global_end_month": st.session_state.global_end_month,
        "regions": st.session_state.global_regions if st.session_state.global_regions else [],
        "states": st.session_state.global_states if st.session_state.global_states else []
    }

    all_regions = fe_get_regions(global_config.database_connection)['region'].tolist()
    try:
        selected_regions = global_filters["regions"].values()
    except AttributeError:
        selected_regions = []
    regions_display = "All" if set(selected_regions) == set(all_regions) else ", ".join(selected_regions)

    with st.container(key="global_input_recap"):

        with st.container(key="global_filters_recap_top"):
            if st.button(global_config.text_resources["global_input_recap_label"]):
                handle_global_button_click("Settings", global_config)

        try:
            date_range = f"From {global_filters['global_start_month']:02d}/{global_filters['global_start_year']} to {global_filters['global_end_month']:02d}/{global_filters['global_end_year']}"
        except TypeError:
            date_range = "Not available"
        st.markdown(f"**📅** {date_range}")

        st.markdown(f"**🌎 Selected Regions:** {regions_display}")

        if global_filters["states"]:
            states_list = ", ".join(global_filters["states"])
            st.markdown(f"**🏛 Selected States:** {states_list}")
        else:
            st.markdown(f"**🏛 Selected States:**")
            st.info("No states selected.")

        st.write('<br>', unsafe_allow_html=True)
        filtered_isolates = fe_get_filtered_isolates_count(global_config.database_connection)["count"].tolist()[0]
        st.markdown(f"**Isolates: {filtered_isolates}**")


def no_global_filters():

    with st.container(key="no_global_filters"):

        st.write("Global settings do not apply to this query (no computation with sequences)", unsafe_allow_html=True)


def get_query_and_params(selected_query_index):
    query_data = query_mapping[selected_query_index]
    query = query_data['query']
    params = query_data['params_func']()
    query = replace_query_placeholders(selected_query_index, query, params)
    return query, params


def build_results_container(selected_query_index):
    with (st.container(key="results_container")):

        if query_mapping[selected_query_index]["plot_params"]:

            table_tab, graph_tab = st.tabs(["Data"] + ["Graph"])
            with table_tab:
                build_table_tab(selected_query_index)
            with graph_tab:
                build_graph_tab()
            #with explore_tab:
                #build_explore_tab(selected_query_index)

        else:
            table_tab = st.tabs(["Data"])[0]
            with table_tab:
                build_table_tab(selected_query_index)


def build_graph_tab():
    with st.container(key="graph_tab"):
        if st.session_state.graph is not None:

            # Save the figure to a BytesIO buffer
            buf = io.BytesIO()
            st.session_state.graph.savefig(buf, format="png")
            buf.seek(0)

            # Add a download button
            st.download_button(
                label="Download Graph as PNG",
                data=buf,
                file_name="graph.png",
                mime="image/png"
            )

            empty1, img_col, empty2 = st.columns([0.025, 0.9, 0.025])
            with img_col:
                st.pyplot(st.session_state.graph)


def build_table_tab(selected_query_index):
    if st.session_state.result is not None:
        if not st.session_state.result.empty:
            with st.container(key="table_tab"):
                batch_size, current_page = build_table_settings(selected_query_index)
                build_download_button()
                build_table(batch_size, current_page - 1)
        else:
            with st.container():
                st.markdown(
                    """
                    <div style="
                        margin-bottom: 20px;
                        padding-bottom: 10px;
                        background-color: #ff4d4d; 
                        color: white; 
                        padding: 16px; 
                        border-radius: 8px; 
                        font-weight: bold;
                        text-align: center;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);">
                        ⚠️ No results found for your query. Please adjust your filters or try again.
                    </div>
                    """,
                    unsafe_allow_html=True
                )


def build_table_settings(selected_query_index):
    with st.container(key="table_settings"):

        col_order, col_strategy, res_per_page_col, current_page_col = st.columns([1, 1, 1, 1])

        col_order.selectbox('Order by', set_default_table_order(selected_query_index, st.session_state.result.columns),
                            key='order_column', on_change=lambda: order_table(st.session_state.result))

        col_strategy.selectbox('Strategy', ['Descending', 'Ascending'], key='order_ascending',
                               on_change=lambda: order_table(st.session_state.result))
        with res_per_page_col:
            batch_size = st.selectbox("Page Size", options=[10, 25, 50, 100])

        with current_page_col:
            total_pages = max(int(len(st.session_state.result) / batch_size) + 1, 1)
            current_page = st.number_input("Page", min_value=1, max_value=total_pages, step=1)

        return batch_size, current_page


def build_table(batch_size, current_page):
    with st.container(key="table_container"):
        if st.session_state.result is not None and not st.session_state.result.empty:
            pagination = st.container()
            pages = split_frame(st.session_state.result, batch_size)
            page_data = pages[current_page]
            start_index = (current_page) * batch_size + 1
            page_data.index = range(start_index, start_index + len(page_data))
            pagination.table(page_data)


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
