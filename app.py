import streamlit as st
import toml
import recommendations
import utils as ut
from service import search, search_by_id, get_doc
import json

# Page configuration
st.set_page_config(
    page_title="Empfehlungsstudie",
    page_icon="🔎"
)

# Load the TOML configuration
config = toml.load('.streamlit/config.toml')
primary_color = config['theme']['primaryColor']
primary_button = config['theme']['primaryButton']
secondary_button = config['theme']['secondaryButton']

# Initialize session states
states = ['recommendations', 'recommendations2', 'dataset', 'slider_val', 'checkbox_val',
          'id', 'datasets', 'list1', 'list2', 'state', 'address', 'selected_title']

for state in states:
    if state not in st.session_state:
        st.session_state[state] = None

# Custom CSS
st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"] {{
        background-color: rgb(240, 240, 242);
        width: 25%;
        float: left;
    }}

    [data-testid="stAppViewBlockContainer"] {{
        margin: 0 auto;
    }}

    .item > a {{
        color: "#004D18";
        font-weight: bold;
    }}

    .tag {{
        display: inline-block;
        background-color: rgb(240, 240, 242);
        color: black;
        padding: 5px;
        margin: 2px;
        margin-bottom: 10px;
        border-radius: 3px;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] {{
        background-color: white;
        max-height: 400px !important;
        overflow-y: auto !important;
        box-shadow: 2.5px 2.5px 5px rgba(0, 0, 0, 0.2);
    }}

    [data-testid="stExpander"] > details {{
        border: none !important;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] > details > summary {{
        height: 120px;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] > details > summary > span > div > p {{
        font-size: 1rem;
        font-weight: bold;
        color: "#004D18";
        margin-bottom: 1em;
        text-align: left;
    }}

    [data-testid="stSidebar"] [data-testid="stExpander"] > details > summary > span > div > p:hover {{
        text-decoration: underline;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Welcome content
if 'state' not in st.session_state or st.session_state['state'] is None:
    st.markdown("""
            <style>
            .block-container {
                padding-top: 0rem;
                padding-bottom: 0rem;
            }
            </style>
        """, unsafe_allow_html=True)
    with st.container():
        st.image("images/umfrage.jpg", width=400)
        st.title("Willkommen zur Studie!")

        st.markdown("""
        In dieser Studie untersuchen wir, wie gut verschiedene Empfehlungssysteme bei der Auswahl von Datensätzen zum Thema Umweltschutz funktionieren.

        **Ablauf der Studie**
        1. **Suchbegriff eingeben**
           * Gib in das Suchfeld links einen Begriff ein (z. B. „Plastikmüll").
           * Klicke auf **„Suchen"**, um eine Liste von passenden Datensätzen zu erhalten.
        """)

        st.image("images/screen_1.png", width=350)

        st.markdown("""
        2. **Einen Datensatz auswählen**
           * Durchsuche die angezeigten Datensätze.
           * Klicke auf **„Mehr"**, um mit diesem Datensatz fortzufahren.
        """)
        st.image("images/mehr.jpg", width=350)

# Sidebar
with st.sidebar:
    st.title('Datensatz suchen')

    user_input = st.text_input("Suchbegriff eingeben")
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("Clear", type="secondary"):
            for state in states:
                st.session_state[state] = None
            st.rerun()

    with col2:
        if st.button("Suchen", type="primary"):
            st.session_state['datasets'] = []
            results = search(user_input, 5)
            for (score, address) in results.hits:
                doc = get_doc(address)
                id = doc['id'][0]
                item_data = {
                    "id": id,
                    "title": doc['title'][0],
                }
                umthes_list = [tag['Umthes'] for tag in json.loads(doc['umthes'][0]) if 'Umthes' in tag]
                item_data['umthes'] = umthes_list
                if doc['bounding_boxes']:
                    item_data['bounding_boxes'] = json.loads(doc['bounding_boxes'][0])
                item_data['source_url'] = doc['source_url'][0]
                item_data['description'] = doc['description'][0]
                item_data['address'] = address
                st.session_state['datasets'].append(item_data)

    # Show search results and "Mehr" buttons
    if 'datasets' in st.session_state and st.session_state['datasets']:
        for item in st.session_state['datasets']:
            with st.expander(item['title']):
                st.markdown(f"[Link zur Quelle]({item['source_url']})")
                st.markdown(item['description'])
                st.markdown(ut.prepare_tags(item['umthes']), unsafe_allow_html=True)

            if st.button('Mehr', key=item["id"], type="secondary"):
                st.session_state['id'] = item['id']
                st.session_state['dataset'] = item
                st.session_state['state'] = 1
                st.session_state['address'] = item['address']
                st.session_state['selected_title'] = item['title']
                st.rerun()
            st.divider()

# Show recommendations
recommendations.show_recommendations()