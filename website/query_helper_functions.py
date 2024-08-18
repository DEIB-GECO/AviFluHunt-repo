import streamlit as st
import yaml

query_folder = 'resources/html_frames'
with open('website/resources/text.yaml', 'r') as file:
    text = yaml.safe_load(file)


def display_query_1(db):

    st.write(text["query_one_explanation"], unsafe_allow_html=True)

    name_serotype, name_segment = st.columns(2)
    if 'query_1_serotype' not in st.session_state:
        st.session_state.query_1_serotype = "H5N1"
    if 'query_1_segment' not in st.session_state:
        st.session_state.query_1_segment = "HA"
    if 'query_1_mutations' not in st.session_state:
        st.session_state.query_1_mutations = set()

    def get_mutations():
        query = ("SELECT mutation_name "
                 "FROM Mutation "
                 "WHERE serotype_name = :serotype_name "
                 "AND annotation_name = :annotation_name")
        params = {
            'serotype_name': st.session_state.query_1_serotype,
            'annotation_name': st.session_state.query_1_segment
        }
        st.session_state.query_1_mutations = db.query(query, params=params)

    with name_serotype:

        def update_serotype():
            st.session_state.query_1_serotype = st.session_state.query_input_1a
            get_mutations()

        serotypes = db.query("SELECT name FROM Serotype ")
        st.selectbox(label=text["query_one_param_a_label"],
                     key='query_input_1a', options=serotypes, on_change=update_serotype)

    with name_segment:

        def update_segment():
            st.session_state.query_1_segment = st.session_state.query_input_1b
            get_mutations()

        segments = db.query("SELECT annotation_name FROM Annotation ")
        st.selectbox(label=text["query_one_param_b_label"],
                     key='query_input_1b', options=segments, on_change=update_segment)

    mutation_input = st.selectbox(label=text["query_one_param_c_label"],
                                  options=st.session_state.query_1_mutations)

    query_sql = ("SELECT effect_full AS Effect, host AS Host, drug AS Drug FROM Effect e "
                 "WHERE e.effect_id in "
                 "(SELECT pem.effect_id "
                 "FROM MutationsMarkers mtm "
                 "JOIN Marker m ON mtm.marker_id = m.marker_id "
                 "JOIN PaperAndEffectOfMarker pem ON m.marker_id = pem.marker_id "
                 "JOIN Mutation mut ON mut.mutation_id = mtm.mutation_id "
                 "WHERE mut.mutation_name = :mutation_name)")
    query_inputs = {}

    st.write(text["query_one_examples"], unsafe_allow_html=True)
    query_inputs["mutation_name"] = mutation_input
    return query_sql, query_inputs


def display_query_2(db):

    st.write(text["query_two_explanation"], unsafe_allow_html=True)

    query_sql = ("SELECT m.mutation_name AS 'Mutation Name', "
                 "total_count AS Instances, human_count AS 'Human Hosts', "
                 "human_count * 100.0 / total_count AS Percentage "
                 "FROM MutationCounts mc "
                 "JOIN Mutation m ON m.mutation_id = mc.mutation_id "
                 "WHERE :min <= human_count * 100.0 / total_count AND human_count * 100.0 / total_count <= :max "
                 "ORDER BY human_count * 100.0 / total_count DESC LIMIT :limit ;")
    query_inputs = {}

    min_input = st.number_input(text["query_two_param_a_label"], step=1, min_value=0, max_value=100)
    max_input = st.number_input(text["query_two_param_b_label"], step=1, min_value=0, max_value=100, value=100)
    limit_input = st.number_input(text["query_two_param_c_label"], step=1, min_value=0, value=100)

    query_inputs["min"] = int(min_input) if min_input < max_input else 0
    query_inputs["max"] = int(max_input) if min_input < max_input else 100
    query_inputs["limit"] = int(limit_input)

    return query_sql, query_inputs


def display_query_3(db):

    st.write(text["query_three_explanation"], unsafe_allow_html=True)

    query_sql = ("SELECT ref as Reference, alt AS Alternate, COUNT(*) AS 'N. Instances' "
                 "FROM Mutation "
                 "GROUP BY alt, ref "
                 "ORDER BY COUNT(*) DESC;")
    query_inputs = {}
    return query_sql, query_inputs


def display_query_4(db):

    st.write(text["query_four_explanation"], unsafe_allow_html=True)

    query_sql = ("SELECT ref as Reference, alt AS Alternate, COUNT(*) AS 'N. Instances' "
                 "FROM Mutation "
                 "WHERE annotation_name LIKE :annotation_name "
                 "GROUP BY alt, ref, annotation_name "
                 "ORDER BY COUNT(*) DESC")
    query_inputs = {}

    segments = db.query("SELECT annotation_name FROM Annotation ")
    annotation_name_input = st.selectbox(label=text["query_four_param_a_label"], options=segments)
    query_inputs["annotation_name"] = annotation_name_input

    return query_sql, query_inputs


def display_query_5(db):

    query_sql = ("SELECT m.mutation_name, m.mutation_id, sm.reference_id, COUNT(*) AS count, "
                 "COUNT(*) / (SELECT COUNT(DISTINCT sm.segment_id) FROM SegmentMutations "
                 "WHERE reference_id = sm.reference_id) as percentage "
                 "FROM SegmentMutations sm "
                 "JOIN Mutation m ON sm.mutation_id = m.mutation_id "
                 "GROUP BY sm.mutation_id, sm.reference_id "
                 "ORDER BY count DESC")
    query_inputs = {}
    st.write(text["query_five"])
    return query_sql, query_inputs


def display_query_6(db):

    st.write(text["query_six_explanation"], unsafe_allow_html=True)

    name_serotype, name_segment = st.columns(2)
    if 'query_6_serotype' not in st.session_state:
        st.session_state.query_6_serotype = "H5N1"
    if 'query_6_segment' not in st.session_state:
        st.session_state.query_6_segment = "HA"
    if 'query_6_mutations' not in st.session_state:
        st.session_state.query_6_mutations = set()

    def get_mutations():
        query = ("SELECT mutation_name "
                 "FROM Mutation "
                 "WHERE serotype_name = :serotype_name "
                 "AND annotation_name = :annotation_name")
        params = {
            'serotype_name': st.session_state.query_6_serotype,
            'annotation_name': st.session_state.query_6_segment
        }
        st.session_state.query_6_mutations = db.query(query, params=params)

    with name_serotype:

        def update_serotype():
            st.session_state.query_6_serotype = st.session_state.query_input_6a
            get_mutations()

        serotypes = db.query("SELECT name FROM Serotype ")
        st.selectbox(label=text["query_six_param_a_label"],
                     key='query_input_6a', options=serotypes, on_change=update_serotype)

    with name_segment:

        def update_segment():
            st.session_state.query_6_segment = st.session_state.query_input_6b
            get_mutations()

        segments = db.query("SELECT annotation_name FROM Annotation ")
        st.selectbox(label=text["query_six_param_b_label"],
                     key='query_input_6b', options=segments, on_change=update_segment)

    mutation_input = st.selectbox(label=text["query_six_param_c_label"],
                                  options=st.session_state.query_6_mutations)

    query_sql = ("SELECT marker_id AS Marker FROM MutationsMarkers mtm "
                 "JOIN Mutation mut ON mtm.mutation_id = mut.mutation_id "
                 "WHERE mut.mutation_name = :mutation_name ")
    query_inputs = {"mutation_name": mutation_input}
    st.write(text["query_six_examples"], unsafe_allow_html=True)
    return query_sql, query_inputs


def display_query_7(db):
    st.write(text["query_seven_label"])
    query_input_7 = st.text_input("Mutation Group: ")

    # Step 1: Process the input string into a list of mutation names
    input_list = query_input_7.split(", ")

    # Step 2: Create a dictionary where each mutation name is both the key and the value
    query_inputs = {mut.replace(":", ""): mut for mut in input_list}

    # Step 3: Create a string with the correct named placeholders
    placeholders = "(" + ", ".join([f":{mut.replace(":", "")}" for mut in input_list]) + ")"

    # Step 4: Formulate the SQL query with the named placeholders
    query_sql = ("WITH mutation_group AS "
                 "(SELECT mutation_id "
                 "FROM Mutation "
                 f"WHERE mutation_name IN {placeholders}) "
                 "SELECT marker_id "
                 "FROM MutationsMarkers "
                 "GROUP BY marker_id "
                 "HAVING COUNT(*) = (SELECT COUNT(*) FROM mutation_group) "
                 "AND COUNT(CASE WHEN mutation_id IN (SELECT mutation_id FROM mutation_group) THEN 1 END) "
                 "= (SELECT COUNT(*) FROM mutation_group);")

    # Return the SQL query and the dictionary of parameters
    return query_sql, query_inputs


def display_query_8(db):

    st.write(text["query_eight_explanation"], unsafe_allow_html=True)

    query_sql = ("SELECT mutation_name AS Mutation "
                 "FROM Mutation "
                 "WHERE position >= :start_pos AND position <= :end_pos "
                 "ORDER BY position")
    query_inputs = {}

    start_input = st.number_input(text["query_eight_param_a_label"], step=1)
    query_inputs["start_pos"] = start_input
    end_input = st.number_input(text["query_eight_param_b_label"], step=1)
    query_inputs["end_pos"] = end_input

    return query_sql, query_inputs


def display_query_9(db):

    st.write(text["query_nine_explanation"], unsafe_allow_html=True)

    query_sql = ("SELECT effect_full as Effect "
                 "FROM Effect "
                 "WHERE effect_type LIKE :type")
    query_inputs = {}

    type_input = st.text_input(text["query_nine_param_a_label"])
    query_inputs["type"] = f"%{type_input}%"
    st.write(text["query_nine_examples"], unsafe_allow_html=True)

    return query_sql, query_inputs


def display_query_10(db):

    st.write(text["query_ten_explanation"], unsafe_allow_html=True)

    query_sql = ("SELECT DISTINCT mut.mutation_name AS Mutation "
                 "FROM Mutation mut "
                 "JOIN MutationsMarkers mtm ON mtm.mutation_id = mut.mutation_id "
                 "JOIN PaperAndEffectOfMarker pem ON mtm.marker_id = pem.marker_id "
                 "JOIN Effect e ON pem.effect_id = e.effect_id "
                 "WHERE e.effect_type LIKE :type")
    query_inputs = {}

    type_input = st.text_input(text["query_ten_param_a_label"])
    query_inputs["type"] = f"%{type_input}%"
    st.write(text["query_ten_examples"], unsafe_allow_html=True)

    return query_sql, query_inputs


"""def display_query_1(db):
    
    query_sql = ("SELECT DISTINCT seg.epi_virus_name "
                 "FROM Segment seg "
                 "JOIN SegmentMutations sm ON seg.segment_id = sm.segment_id "
                 "JOIN Mutation mut ON sm.mutation_id = mut.mutation_id "
                 "JOIN MutationsMarkers mtm ON mut.mutation_id = mtm.mutation_id "
                 "JOIN PaperAndEffectOfMarker pem ON mtm.marker_id = pem.marker_id "
                 "JOIN Effect e ON pem.effect_id = e.effect_id "
                 "WHERE e.effect_full = :effect_full")
    query_inputs = {}
    
    st.write(text["query_one"])
    
    effect_types = db.query(
        sql="SELECT DISTINCT effect_full FROM Effect"
    )

    query_input_1 = st.selectbox("Effect Type", effect_types)
    query_inputs["effect_full"] = query_input_1

    return query_sql, query_inputs"""
