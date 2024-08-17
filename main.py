import streamlit as st
from user_interface.sidebar_config import sidebar_config
from user_interface.display_results import display_results
from document_processing.process_document import process_document
from document_processing.extract_questions import extract_questions, summarize_questions
from answer_generation.generate_answers import generate_answers
from answer_generation.generate_subvention_answers import generate_subvention_answers
from web_search.search_google import get_subvention_context
from user_interface.utils import run_analysis, save_project

st.set_page_config(page_title="FOLDR : Optimisez vos demandes, multipliez vos chances de financement", layout="wide")

project_name, subvention_path, user_path, analyze_button = sidebar_config()

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False

if analyze_button or st.session_state.analysis_complete:
    if not st.session_state.analysis_complete:
        summary_questions, key_info, subvention_context, expert_advice, subv_responses = run_analysis(
            project_name, subvention_path, user_path,
            process_document, extract_questions, summarize_questions,
            generate_answers, generate_subvention_answers, get_subvention_context
        )
        st.session_state.summary_questions = summary_questions
        st.session_state.key_info = key_info
        st.session_state.subvention_context = subvention_context
        st.session_state.expert_advice = expert_advice
        st.session_state.subv_responses = subv_responses
        st.session_state.analysis_complete = True
        save_project(project_name)
    else:
        summary_questions = st.session_state.summary_questions
        key_info = st.session_state.key_info
        subvention_context = st.session_state.subvention_context
        expert_advice = st.session_state.expert_advice
        subv_responses = st.session_state.subv_responses

    display_results(project_name, summary_questions, key_info, subvention_context, expert_advice, subv_responses)
else:
    st.title("Bienvenue dans FOLDR : Optimisez vos demandes, multipliez vos chances de financement")
    st.subheader("L'IA au service de vos financements")
    st.write("Veuillez configurer votre projet dans le panneau de gauche et cliquer sur 'Analyser' pour commencer.")