import streamlit as st
st.set_page_config(layout="wide", page_title="AviFluHunt")
from aviflunhunt_fe import *


class GlobalConfig:
    text_resources = strings  # TODO: deal with other file!
    queries = {
        "Markers Effects": [1, 12, 13, 14],
        "Markers": [9, 7, 6, 15],
        "Markers and Hosts": [5, 2, 3, 4, 8],
        "Mutations": [10, 11]
    }
    database_connection = db


global_config = GlobalConfig()

if not check_auth():
    st.stop()

init_session()

st.markdown(f'<style>{
"""
/* General Styling */

:root {
    --main-color: #09090B;
    --secondary-color: #131313;
    --main-text-color: white;
    --accent-color: #6164F4;
    --border-color: black;
}

@import url("https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap");

* {
    color: white;
    border: 0 !important;
    box-sizing: border-box;
    font-family: Poppins, sans-serif !important;
}

body {
    font-family: Poppins, sans-serif !important;
}

.stApp {
    background-color: var(--main-color);
}

input {
    caret-color: transparent;
}

/* Webkit-based browsers (Chrome, Safari) */
::-webkit-scrollbar {
    width: 10px; /* Width of the scrollbar */
    background: rgba(255, 255, 255, 0); /* Background color of the scrollbar */
}

::-webkit-scrollbar-thumb {
    background: rgba(0, 0, 0, 0); /* Color of the draggable part of the scrollbar */
    border-radius: 10px; /* Rounded corners */
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(0, 0, 0, 0); /* Darker color when hovered */
}

/* Firefox */
* {
    scrollbar-width: thin; /* Make scrollbar thinner */
    scrollbar-color: rgba(0, 0, 0, 0) rgba(255, 255, 255, 0); /* Thumb and background color */
}

.stMainBlockContainer {
    padding: 0;
    font-family: Poppins, sans-serif !important;
}

.stVerticalBlock {
    gap: 0 !important;
}

[data-baseweb="popover"] {
    border-radius: 0;
    border: 2px solid white;
}

[data-baseweb="popover"] div {
    font-weight: bold;
    font-size: 14px !important;
    background-color: var(--main-color);
}

[data-baseweb="popover"] ul {
    border-radius: 5px !important;
}

[data-baseweb="popover"] li {
    background-color: white;
}

[data-baseweb="popover"] li * {
    color: black;
    background-color: transparent;
}

[data-baseweb="popover"] li:hover * {
    color: white;
    background-color: transparent;
}

[data-baseweb="popover"] li:hover {
    color: white;
    background-color: var(--accent-color);
}

[data-baseweb="popover"] [data-baseweb="calendar"] {
    border-radius: 5px;
}

[data-baseweb="popover"] [data-baseweb="calendar"] div {
    background-color: black !important;
    color: white;
}

[data-baseweb="popover"] [data-baseweb="calendar"] * {
    color: white;
}


#avifluhunt {

    margin: 0;
    margin-left: 2vw;
    width: 100% !important;
    padding-bottom: 0.5rem !important;

    color: white;
    font-size: 24px;
    font-weight: bold;
    background-color: transparent;
    font-family: Poppins, sans-serif !important;
}

.st-key-global_container {
    width: 96vw;
    margin: 0 3vw 0 2vw;
    margin-top: .5vh;
    margin-bottom: 1.5vh;
    height: 0 !important;
    padding-left: 73vw;
}

.st-key-global_container > div > div {
    height: 0 !important;
}

.st-key-global_container .stButton {
    width: auto;
}

.st-key-global_container button {
    padding: 0 !important;
    margin-left: 1vw;
}

.st-key-global_container button * {
    min-width: auto;
    text-align: right;
    font-size: 16px;
    font-weight: bold;
    margin-left: auto;
    margin-right: 0;
    padding: 0 !important;
}

.st-key-global_container div {
    width: max-content;
    flex: content !important;
}

.st-key-taxonomy_tree_overlay * {
    color: black;
}

.st-key-taxonomy_tree_overlay label > div:first-of-type {
    min-width: 0 !important;
    background-color: transparent;
    max-width: 0% !important;
    max-height: 0% !important;
}

.st-key-taxonomy_tree_search label > div:first-of-type {
    background-color: transparent;
    max-width: 100% !important;
    max-height: auto !important;
}

.st-key-taxonomy_tree_search {
    margin-bottom: 2vh;
}

.st-key-taxonomy_tree_search .stTextInput > * {
    width: auto;
    float: left !important;
}

.st-key-taxonomy_tree_search .stTextInput > div {
    border: 1px solid black !important; 
}

.st-key-taxonomy_tree_overlay label {
    margin-right: 1vw !important;
    margin-top: 0 !important;
}

.st-key-taxonomy_tree_overlay label:has(input[aria-checked="false"]) p {
    color: blue !important;
}

.st-key-taxonomy_tree_overlay label:has(input[aria-checked="false"]) p::before {
    content: "▶ ";
}

.st-key-taxonomy_tree_overlay label:has(input[aria-checked="true"]) p {
    color: black !important;
    text-decoration: none !important;
}

.st-key-taxonomy_tree_overlay label:has(input[aria-checked="true"]) p::before {
    content: "▼ ";
}

.st-key-isolates_remaining {
    display: inline-block !important;
}

.st-key-isolates_remaining * {
    vertical-align: center !important;
}

.st-key-isolates_remaining > div:nth-child(3) {
    width: 50%;
    float: left !important;
}

.st-key-isolates_remaining > div:nth-child(4) {
    width: 50%;
    float: right !important;
    align: right !important;
}

.st-key-isolates_remaining > div:nth-child(4) button {
    margin-left: 40%;
    width: 10%;
    background-color: var(--accent-color);
}

.st-key-isolates_remaining > div:nth-child(4) button p {
    color: white;
    margin-top: 0 !important;
}

.stDialog [aria-label="dialog"] {
    padding: 1.5%;
    width: 80%;
    height: auto !important;
    background-color: white;
    border-radius: 5px !important;
}

.stDialog span svg * {
    color: white !important;
}

.stDialog label, 
.stDialog p{
    color: black;
    font-weight: bold;
    margin-top: 1vh;
}

.stDialog .stMultiSelect > div {
    padding: 1%;
    border: 1px solid black !important;
    border-radius: 5px !important;
}

.stDialog .stDateInput > div {
    border: 1px solid black !important;
    border-radius: 5px !important;
}

.stDialog .stMultiSelect svg * {
    color: black;
}

.stDialog [aria-label="Close"] {
    visibility: hidden;
}

hr {
    background-color: #777;
}

#isolates_filtered_h4 {
    color: black;
}

.st-key-main_page {
    width: 98vw;
    margin: 4vh 1vw;
    padding: 0 1vw 3vh 1vw !important;
    display: inline-block !important;
    
    background-color: var(--secondary-color);
    border-radius: 10px !important;
}

.st-key-main_page > div:nth-child(3) {
    width: 20%;
    float: left !important;
}

.st-key-main_page > div:nth-child(4) {
    width: 78%;
    margin-left: 1.5%;
    float: left;
}

.st-key-query_type_selector {
    z-index: 10;
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 0;
    margin-top: 2vh;
    margin-bottom: -1vh;
    padding-right: 1vw;
}

.st-key-query_type_selector > .stElementContainer {
    width: auto !important; 
    flex: 0 0 auto; 
}

.st-key-query_type_selector .stButton {
    width: auto !important;
    
    border-radius: 5px !important;
    background-color: transparent;
}

.st-key-query_type_selector .stButton > button {
    padding: 0 !important;
    min-height: 0 !important;
    border: 0;
    border-radius: 0 !important;
}

.st-key-query_type_selector .stButton > button > div > p {
    padding: 0 !important;
    font-weight: bold;
    font-size: 14px !important;
}

.st-key-left_column {
    padding-left: 1vw;
    margin-bottom: 2vh;
    background-color: transparent;
}

.st-key-left_column svg * {
    color: black;
}

.st-key-query_container,
.st-key-results_container {
    width: 100%;
    flex: 1;
}

#query_sel_label {
    font-size: 18px;
}

.st-key-query_selector {
    margin-top: -3vh;
    padding-bottom: 1vh;
    margin-bottom: 1vh;
    margin-left: 1vw !important;
}

.st-key-query_selector * {
    max-width: 94.6vw !important;
}

.st-key-query_selector .stSelectbox {
    margin-top: -0.5vh;
    background-color: white;
    border-radius: 5px !important;
}

svg * {
    color: black;
}

.st-key-query_selector .stSelectbox div {
    height: auto !important;
    white-space: wrap !important;
    font-weight: bold;
    color: black;
    font-size: 14px !important;
}

.st-key-query_inputs_container {
    padding: 0 !important;
    margin-bottom: 2vh;
}

.st-key-global_input_recap {
    background-color: var(--accent-color);
    padding: 7.5% !important; 
    border-radius: 10px;
    box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
    margin-bottom: 1vh;
    max-width: 100%;
    box-sizing: border-box !important; 
    overflow: hidden !important; 
    word-wrap: break-word !important; 
}

.st-key-global_input_recap * {
    max-width: 100%;
    box-sizing: border-box !important; 
    overflow: hidden !important; 
    word-wrap: break-word !important; 
}

.st-key-query_inputs_container svg * {
    color: white;
}

.st-key-query_inputs_container > .stForm {
    padding: 0 !important;
}

#inputs {
    margin-bottom: 1vh;
    font-size: 18px !important;
}

.st-key-query_inputs_container [data-testid="stWidgetLabel"] > div {
    width: 100% !important;
} 

.st-key-query_inputs_container [data-testid="stWidgetLabel"] p {
    font-weight: bold;
    font-size: 13px !important;
}

.st-key-query_inputs_container .stSelectbox > div,
.st-key-query_inputs_container .stMultiSelect > div,
.st-key-query_inputs_container .stNumberInput > div,
.st-key-query_inputs_container .stDateInput > div 
{
    height: auto !important;
    white-space: wrap !important;
    background-color: white;
}

.st-key-query_inputs_container .stSelectbox > div div,
.st-key-query_inputs_container .stMultiSelect > div div,
.st-key-query_inputs_container .stNumberInput > div input,
.st-key-query_inputs_container .stDateInput > div input
{
    height: auto !important;
    color: black;
    font-size: 14px !important;
}

.stMultiSelect span * {
    font-size: 12px;
    font-weight: bold;
}

.stNumberInputContainer {
    background-radius: 0!important;
}

.st-key-query_inputs_container [data-baseweb="tab-list"] {
    margin-top: 2vh;
    margin-bottom: -2vh;
    width: 100% !important;
}

.st-key-query_inputs_container [data-baseweb="tab-list"] > div {
    background-color: white;
}

.st-key-query_inputs_container [data-baseweb="tab-list"] button {
    float: right !important;
    background-color: transparent;
    border-radius: 5px;
    padding: 0 !important;
}

.st-key-query_inputs_container [data-baseweb="tab-list"] button p {
    color: white;
    font-weight: bold;
    font-size: 13px !important;
}

.st-key-query_inputs_container .stFormSubmitButton > button {
    margin-top: 5vh;
    background-color: var(--accent-color);
    border-radius: 0;
    padding: 0vh 2vw;
    width: 100% !important;
}

.st-key-query_inputs_container .stFormSubmitButton > button p {
    color: white;
    font-weight: bold;
    font-size: 14px !important;
}

.st-key-results_container {
    background: white;
    padding: 3vh 2vw 1vh 2vw;
    border-radius: 10px !important;
}

.st-key-results_container [data-testid="stTab"]{
    margin-right: 0.5vw
}

.st-key-results_container [data-testid="stTab"] p {
    font-weight: bold;
    font-size: 14px !important;
    color: var(--main-color);
    text-transform: uppercase;
}

.st-key-results_container [data-baseweb="tab-highlight"] {
    height: 3px;
    background-color: var(--main-color);
}

.stDownloadButton button {
    border: 1px solid black !important;
    margin-bottom: 2vh;
}

.st-key-results_container button p {
    color: black;
}

.st-key-table_settings {
    margin-bottom: 2.5vh;
}

.st-key-table_settings * {
    color: black;
}

.st-key-table_settings .stSelectbox > div,
.st-key-table_settings .stNumberInput > div {
    border-radius: 0.5rem;
    border: 1px solid var(--main-color) !important;
}

[data-baseweb="popover"] div {
    background-color: transparent !important;
}

button:hover > svg * {
    color: white;
}

.stTable, table {
    border-radius: 5px !important;
}

.stTable * {
    color: black;
    border: 0.5px solid rgba(0, 0, 0, 0.3) !important;
}

.stTable div,
.stTable p {
    border: 0 !important;
}

thead * {
    font-weight: bold !important;
    color: white !important;
    text-align: left !important;
    background-color: var(--accent-color);
}

th {
    padding-left: 0.5vw !important;
}

#about_page_html * {
    color: black;
    text-align: justify !important;
}

#about_page_html p {
    font-size: 16px !important;
}

#bottom_about_container {
    display: flex; /* Enables flexbox layout */
    width: 100%; /* Ensure it takes the full width of its parent */
    box-sizing: border-box; /* Include padding and border in width calculations */
}

#bottom_about_container > div {
    flex: 0 0 50%; /* Set each child to take 50% of the parent's width */
    box-sizing: border-box; /* Include padding and border in width calculations */
}

#bottom_about_container > div * {
    padding: 0;
    padding-bottom: 0.5vh;
}

#bottom_about_container > div h6 {
    font-weight: normal;
}

.st-key-add_manual_input_container {
    position: absolute;
    margin-top: 175px;
    z-index: 9999;
}

.st-key-add_manual_input_container label {
    font-size: 13px;
    font-weight: bold;
}
"""
}</style>', unsafe_allow_html=True)

build_top_bar(global_config)
build_global_container(global_config)
build_main_page(global_config)
