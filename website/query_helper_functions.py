import streamlit as st
import yaml

query_folder = 'resources/html_frames'
with open('website/resources/text.yaml', 'r') as file:
    text = yaml.safe_load(file)


def display_query_1(db):

    query_sql = ("SELECT * FROM Effect e "
                 "WHERE e.effect_id in "
                 "(SELECT pem.effect_id "
                 "FROM MutationsMarkers mtm "
                 "JOIN Marker m ON mtm.marker_id = m.marker_id "
                 "JOIN PaperAndEffectOfMarker pem ON m.marker_id = pem.marker_id "
                 "JOIN Mutation mut ON mut.mutation_id = mtm.mutation_id "
                 "WHERE mut.mutation_name = :mutation_name)")
    query_inputs = {}

    st.write(text["query_one"])

    query_input_1 = st.text_input("Mutation Name: ")
    query_inputs["mutation_name"] = query_input_1

    return query_sql, query_inputs


def display_query_2(db):

    query_sql = ("SELECT m.mutation_name, m.mutation_id, total_count, human_count, "
                 "human_count * 100.0 / total_count AS human_percentage "
                 "FROM MutationCounts mc "
                 "JOIN Mutation m ON m.mutation_id = mc.mutation_id "
                 "ORDER BY human_count * 100.0 / total_count DESC;")
    query_inputs = {}

    st.write(text["query_two"])
    return query_sql, query_inputs


def display_query_3(db):

    query_sql = ("SELECT alt, ref, COUNT(*) AS count "
                 "FROM Mutation "
                 "GROUP BY alt, ref "
                 "ORDER BY count DESC;")
    query_inputs = {}
    st.write(text["query_three"])
    return query_sql, query_inputs


def display_query_4(db):

    query_sql = ("SELECT alt, ref, COUNT(*) AS count "
                 "FROM Mutation "
                 "WHERE annotation_name LIKE :annotation_name "
                 "GROUP BY alt, ref, annotation_name "
                 "ORDER BY count DESC")
    query_inputs = {}

    st.write(text["query_four"])

    query_input_4 = st.text_input("Annotation Name: ")
    query_inputs["annotation_name"] = query_input_4

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

    query_sql = ("SELECT marker_id FROM MutationsMarkers mtm "
                 "JOIN Mutation mut ON mtm.mutation_id = mut.mutation_id "
                 "WHERE mut.mutation_name = :mutation_name ")
    query_inputs = {}

    st.write(text["query_six"])

    query_input_6 = st.text_input("Mutation Name: ")
    query_inputs["mutation_name"] = query_input_6

    return query_sql, query_inputs


def display_query_7(db):
    st.write(text["query_seven"])
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

    query_sql = ("SELECT mutation_name "
                 "FROM Mutation "
                 "WHERE position >= :start_pos AND position <= :end_pos")
    query_inputs = {}

    st.write(text["query_eight"])

    query_input_8a = st.number_input("Start Position: ", step=1)
    query_inputs["start_pos"] = query_input_8a
    query_input_8b = st.number_input("End Position: ", step=1)
    query_inputs["end_pos"] = query_input_8b

    return query_sql, query_inputs


def display_query_9(db):

    query_sql = ("SELECT effect_full "
                 "FROM Effect "
                 "WHERE effect_type LIKE :type")
    query_inputs = {}

    st.write(text["query_nine"])

    query_input_9 = st.text_input("Effect Type: ")
    query_inputs["type"] = f"%{query_input_9}%"

    return query_sql, query_inputs


def display_query_10(db):

    query_sql = ("SELECT DISTINCT mut.mutation_name "
                 "FROM Mutation mut "
                 "JOIN MutationsMarkers mtm ON mtm.mutation_id = mut.mutation_id "
                 "JOIN PaperAndEffectOfMarker pem ON mtm.marker_id = pem.marker_id "
                 "JOIN Effect e ON pem.effect_id = e.effect_id "
                 "WHERE e.effect_type LIKE :type")
    query_inputs = {}

    st.write(text["query_ten"])

    query_input_10 = st.text_input("Effect Type: ")
    query_inputs["type"] = f"%{query_input_10}%"

    return query_sql, query_inputs


def display_query_11(db):

    query_sql = ("SELECT * FROM Effect e "
                 "WHERE e.effect_id in "
                 "(SELECT pem.effect_id "
                 "FROM MutationsMarkers mtm "
                 "JOIN PaperAndEffectOfMarker pem ON mtm.marker_id = pem.marker_id "
                 "JOIN Mutation m ON mtm.mutation_id = m.mutation_id "
                 "WHERE m.mutation_name = :mutation_name )")
    query_inputs = {}

    st.write(text["query_eleven"])

    query_input_11 = st.text_input("Mutation Name: ")
    query_inputs["mutation_name"] = query_input_11

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
