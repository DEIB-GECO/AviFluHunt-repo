from aviflunhunt_fe import *

# CONFIG
st.set_page_config(layout="wide", page_title="AviFluHunt")
db = st.connection(name="fluhunt", type="sql", url="sqlite:///website/data/fluhunt.db")


class GlobalConfig:
    text_resources = strings  # TODO: deal with other file!
    queries = {
        "Markers Effects": [1, 12, 13, 14],
        "Markers": [9, 7, 6, 15],
        "Markers with Filters": [5, 2, 3, 4, 8],
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

.st-emotion-cache-1jicfl2 {
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

[data-baseweb="popover"] li {
    border-bottom: 1px solid white;
}

h1 {

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
    margin-top: 2.5vh;
    margin-bottom: 1.5vh;
    height: 0 !important;
}

.st-key-global_container > div > div {
    height: 0 !important;
}

.st-key-global_filters_overlay_container {
    height: 0 !important;
    align-items: right;
    background-color: green;
}

[aria-label="dialog"] {
    width: 80%;
    height: auto !important;
    background-color: green;
}

.st-key-main_page {
    width: 98vw;
    margin: 4vh 1vw;
    padding: 0 1vw 3vh 1vw !important;
    display: inline-block !important;
    
    background-color: var(--secondary-color);
    border-radius: 10px !important;
}

.st-key-main_page > div:nth-child(2) {
    width: 20%;
    float: left !important;
}

.st-key-main_page > div:nth-child(3) {
    width: 78%;
    margin-left: 1.5%;
    float: left;
}

.st-key-query_type_selector {
    display: flex;
    flex-direction: row;
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 0;
    margin-top: 2vh;
    margin-bottom: 2vh;
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
    padding-top: 2vh;
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
    padding-bottom: 1vh;
    margin-bottom: 1vh;
}

.st-key-query_selector .stSelectbox {
    margin-top: -0.5vh;
    max-height: 30vh;
    background-color: white;
}

.st-key-query_selector .stSelectbox div {
    height: auto !important;
    max-height: 30vh;
    white-space: wrap !important;
    font-weight: bold;
    color: black;
    font-size: 14px !important;
}

.st-key-query_inputs_container {
    padding: 0 !important;
    margin-bottom: 2vh;
}

.st-key-query_inputs_container > .stForm {
    padding: 0 !important;
}

#inputs {
    margin-bottom: 4vh;
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
.st-key-query_inputs_container .stNumberInput > div 
{
    height: auto !important;
    max-height: 30vh;
    white-space: wrap !important;
    background-color: white;
}

.st-key-query_inputs_container .stSelectbox > div div,
.st-key-query_inputs_container .stMultiSelect > div div,
.st-key-query_inputs_container .stNumberInput > div input
{
    height: auto !important;
    color: black;
    font-size: 14px !important;
}

.st-key-query_inputs_container button {
    margin-top: 2.5vh;
    float: right !important;
    background-color: white;
    border-radius: 0; 
    font-size: 14px !important;
}

.st-key-query_inputs_container button p {
    font-size: 14px !important;
}

.st-key-query_inputs_container button div {
    padding: 0 1vw;
    width: 100% !important;
}

.st-key-query_inputs_container button p {
    color: black;
    font-weight: bold;
}

.st-key-results_container {
background: white;
    min-height: 70vh !important;
    padding: 0 1vw;
    border-radius: 10px !important;
    border: 2px solid var(--accent-color);
}

.st-key-results_container [data-testid="stTab"]{
    margin-right: 0.5vw;
}

.st-key-results_container [data-testid="stTab"] p {
    font-weight: bold;
    font-size: 14px !important;
    color: var(--accent-color);
    text-transform: uppercase;
}

.st-key-results_container [data-baseweb="tab-highlight"] {
    height: 3px;
    background-color: var(--accent-color);
}

"""
}</style>', unsafe_allow_html=True)

build_top_bar(global_config)
build_global_container(global_config)
build_main_page(global_config)
