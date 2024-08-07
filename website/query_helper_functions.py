import streamlit as st
import yaml

query_folder = "D:\Desktop\Polimi\Tesi\TesiWebsite\websitename\\resources\\html_frames\\"
with open('D:\Desktop\Polimi\Tesi\TesiWebsite\websitename\\resources\\text.yaml', 'r') as file:
    text = yaml.safe_load(file)


def display_query_1(db):
    
    query_sql = ("SELECT DISTINCT seg.epi_virus_name "
                 "FROM Segment seg "
                 "JOIN SegmentMutations sm ON seg.segment_id = sm.segment_id "
                 "JOIN Mutation mut ON sm.mutation_id = mut.mutation_id "
                 "JOIN MutationsToMarker mtm ON mut.mutation_id = mtm.mutation_id "
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

    return query_sql, query_inputs
