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
    --main-bg-color: #09090B;
    --secondary-bg-color: white;
    --main-text-color: white;
    --accent-color: rgb(160, 204, 197);
    --border-color: black;
}

@import url("https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800;1,900&display=swap");

* {
    color: white;
    box-sizing: border-box;
    font-family: Poppins, sans-serif !important;
}

body {
    font-family: Poppins, sans-serif !important;
}

.stApp {
    background-color: var(--main-bg-color);
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
    background-color: var(--main-bg-color);
}

[data-baseweb="popover"] li {
    border-bottom: 1px solid white;
}

h1 {

    margin: 0;
    margin-left: 2vh;
    width: 100% !important;
    padding-bottom: 1.5rem !important;

    color: white;
    font-size: 20px;
    font-weight: bold;
    background-color: transparent;
    font-family: Poppins, sans-serif !important;
}

.st-key-global_container {
    width: 98vw;
    margin: 0 1vw;
    display: inline-block !important;
    border-bottom: 1.5px solid white;
}

.st-key-global_container > div:nth-child(1) {
    width: 50%;
    float: left !important;
}

.st-key-global_container > div:nth-child(2) {
    width: 50%;
    float: left;
}

.st-key-global_filters_overlay_container {
    height: auto !important;
    background-color: purple;
}

.st-key-query_type_selector {
    display: flex;
    flex-direction: row; 
    justify-content: flex-end;
    flex-wrap: wrap;
    gap: 0;
}

.st-key-query_type_selector > .stElementContainer {
    width: auto !important; 
    flex: 0 0 auto; 
}

.st-key-query_type_selector .stButton {
    width: auto !important;
    border: 1px solid white;
}

.st-key-query_type_selector .stButton > button {
    border-radius: 0 !important;
}

.st-key-query_type_selector .stButton > button > div > p {
    font-weight: bold;
    font-size: 14px !important;
}

.st-key-main_page {
    width: 98vw;
    margin: 2.5vh 1vw;
    display: inline-block !important;
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

.st-key-query_container,
.st-key-results_container {
    width: 100%;                    /* Ensure containers span the full width of their wrappers */
    flex: 1;                        /* Allow them to grow within their allocated space */
}

.st-key-query_selector {
    padding-bottom: 1vh;
    margin-bottom: 1vh;
}

.st-key-query_selector .stSelectbox {
    width: 50vw !important;
    border: 2px solid white;
}

.st-key-query_selector .stSelectbox div {
    font-weight: bold;
    font-size: 14px !important;
}

.st-key-query_inputs_container {
    border: 1px solid white;
}

.st-key-results_container {
}

"""
}</style>', unsafe_allow_html=True)

build_top_bar(global_config)
build_global_container(global_config)
build_main_page(global_config)



