from service import embedding, more_like_this
import streamlit as st
import toml
import utils as ut
from streamlit_extras.stylable_container import stylable_container
import random
import pandas as pd
import uuid

# Load the TOML configuration
config = toml.load('.streamlit/config.toml')
primary_color = config['theme']['primaryColor']
primary_button = config['theme']['primaryButton']
secondary_button = config['theme']['secondaryButton']

# Custom styles for recommendations
container_style = """
    [data-testid="stSlider"] {
        display: flex;
        justify-content: center;
        width: 50%;
    }

    .rec {
        background-color: white;
        height: 165px;
        overflow-y: auto !important;
        background: linear-gradient(to bottom, transparent, white 90%);
        border: 1px solid rgb(240,240,242);
        z-index: 0;
    }

    .rec > p {
        margin: 10px;
    }

    .rec > a {
        margin: 10px;
    }

    .rec > div {
        padding-left: 5px;
    }

    .rec:after {
        content: '⇩';
        position: absolute;
        bottom: 5px;
        right: 10px;
        pointer-events: none;
    }

    .title {
        font-weight: bold;
        color: """ + primary_button + """;
        text-align: left;
    }

    .desc {
        margin-bottom: 10px;
        margin-left: 5px;
    }
"""


def show_recommendations():
    if 'state' in st.session_state and st.session_state['state'] is not None and st.session_state['state'] > 0:
        st.markdown(
            """
            <style>
            #welcome-content {
                display: none;
            }

            /* Entfernt den oberen Abstand für den Container */
            .block-container {
                padding-top: 0rem;
                padding-bottom: 0rem;
            }

            /* Entfernt zusätzlichen Abstand vor der Überschrift */
            .stHeader {
                padding-top: 0 !important;
                margin-top: 0 !important;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    # Generate recommendations
    if 'state' in st.session_state and st.session_state['state'] == 1:
        # Ausgewählter Datensatz ohne oberen Abstand
        st.markdown('<div style="margin-top: -2rem;"></div>', unsafe_allow_html=True)
        st.header("Ihr ausgewählter Datensatz:")
        st.subheader(st.session_state['selected_title'])
        st.divider()

        with st.spinner("Empfehlungen generieren"):
            k = 5
            random_number = random.randint(0, 1)
            if random_number == 0:
                st.session_state['recommendations'] = embedding(st.session_state['id'], k+1)
                st.session_state['recommendations2'] = more_like_this(st.session_state['address'], k+1)
                st.session_state['list1'] = 'EMBEDDING'
                st.session_state['list2'] = 'TFIDF'
            else:
                st.session_state['recommendations'] = more_like_this(st.session_state['address'], k+1)
                st.session_state['recommendations2'] = embedding(st.session_state['id'], k+1)
                st.session_state['list1'] = 'TFIDF'
                st.session_state['list2'] = 'EMBEDDING'

        st.session_state['state'] = 2

    # Show recommendations and feedback form
    if ('state' in st.session_state and
            st.session_state['state'] == 2 and
            'recommendations' in st.session_state and
            'recommendations2' in st.session_state and
            st.session_state['recommendations'] and
            st.session_state['recommendations2']):

        st.write(
            "Bitte bewerten Sie die beiden Empfehlungslisten, indem Sie für jede Empfehlung angeben, wie relevant sie sind. "
            "Nutzen Sie dazu die Schieberegler, um Ihre Einschätzung von 0 (gar nicht relevant) bis 100 (sehr relevant) auszudrücken. "
            "Abschließend können Sie angeben, welche Liste Ihnen insgesamt besser gefällt, und ein optionales Feedback hinterlassen."
        )

        with st.form(key='recommendation_form'):
            data = []
            row_dict = {}

            with stylable_container(key="recommendations_container", css_styles=container_style):
                # List A
                st.header('Empfehlungen Liste A')
                has_clicked_a = False

                for i, recommendation1 in enumerate(st.session_state['recommendations']):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        slider_value_a = st.slider("", key=f"1{i + 1}{recommendation1['id']}", value=50)
                        if slider_value_a != 50:
                            has_clicked_a = True
                    with col2:
                        st.markdown(ut.print_data(recommendation1), unsafe_allow_html=True)
                    row_dict[f"slider_a_{i + 1}"] = slider_value_a
                    st.write("")

                st.write("Bewerten Sie die gesamte Liste A!")
                selected_a = st.feedback(key="feedback_a", options="stars")
                row_dict["feedback_a"] = selected_a
                row_dict["Methode_1"] = st.session_state['list1']

                st.divider()

                # List B
                st.header('Empfehlungen Liste B')
                has_clicked_b = False

                for i, recommendation2 in enumerate(st.session_state['recommendations2']):
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        slider_value_b = st.slider("", key=f"slider_b_{i + 1}_{recommendation2['id']}", value=50)
                        if slider_value_b != 50:
                            has_clicked_b = True
                    with col2:
                        st.markdown(ut.print_data(recommendation2), unsafe_allow_html=True)
                    row_dict[f"slider_b_{i + 1}"] = slider_value_b
                    st.write("")

                st.write("Bewerten Sie die gesamte Liste B!")
                selected_b = st.feedback(key="feedback_b", options="stars")
                row_dict["feedback_b"] = selected_b
                row_dict["Methode_2"] = st.session_state['list2']

                st.divider()

                better_list = st.radio(
                    "Welche Liste fanden Sie besser?",
                    options=["Liste A", "Liste B"],
                    index=0
                )
                row_dict["better_list"] = better_list

                comment = st.text_area("Kommentar:", "", height=150)
                if comment:
                    row_dict["comment"] = comment

                submit_button = st.form_submit_button(label='Absenden')

                if submit_button:
                    if not has_clicked_a:
                        st.error("Bitte ändere mindestens einen Schieberegler in Liste A.")
                    elif not has_clicked_b:
                        st.error("Bitte ändere mindestens einen Schieberegler in Liste B.")
                    else:
                        data.append(row_dict)
                        df = pd.DataFrame(data)
                        filename = f"{str(uuid.uuid4())[:8]}.csv"
                        df.to_csv(filename, index=False)
                        st.success("Dein Feedback wurde erfolgreich gespeichert!")