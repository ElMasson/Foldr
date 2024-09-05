#main.py

import streamlit as st
from user_interface.sidebar_config import sidebar_config
from user_interface.display_results import display_results
from document_processing.process_document import process_document
from document_processing.extract_questions import extract_questions, summarize_questions
from web_search.search_google import get_subvention_context
from user_interface.utils import save_project


st.set_page_config(page_title="FOLDR : Optimisez vos demandes, multipliez vos chances de financement", layout="wide")

project_name, subvention_path, user_path, analyze_button = sidebar_config()

# Initialize session state variables
if 'user_path' not in st.session_state:
    st.session_state.user_path = None
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'questions_reviewed' not in st.session_state:
    st.session_state.questions_reviewed = False
if 'responses_generated' not in st.session_state:
    st.session_state.responses_generated = False
if 'critiques_generated' not in st.session_state:
    st.session_state.critiques_generated = False

# Update user_path in session_state
st.session_state.user_path = user_path

if analyze_button or st.session_state.analysis_complete:
    if not st.session_state.analysis_complete:
        @st.cache_data
        def perform_analysis(subvention_path, user_path):
            subv_index = process_document(subvention_path, "gpt-4o-mini")
            extracted_questions = extract_questions(subv_index.as_query_engine(), "gpt-4o-mini")
            key_info, search_results, subvention_context, expert_advice = get_subvention_context(subv_index)
            summary_questions = summarize_questions(extracted_questions, subvention_context, "gpt-4o-mini")
            return extracted_questions, summary_questions, subvention_context, expert_advice


        extracted_questions, summary_questions, subvention_context, expert_advice = perform_analysis(subvention_path,
                                                                                                     user_path)

        st.session_state.extracted_questions = extracted_questions
        st.session_state.summary_questions = summary_questions
        st.session_state.subvention_context = subvention_context
        st.session_state.expert_advice = expert_advice
        st.session_state.analysis_complete = True
        save_project(project_name)

    display_results(project_name)

else:
    st.title("Bienvenue dans FOLDR : Optimisez vos demandes, multipliez vos chances de financement")
    st.subheader("L'IA au service de vos financements")
    st.write("Veuillez configurer votre projet dans le panneau de gauche et cliquer sur 'Analyser' pour commencer.")