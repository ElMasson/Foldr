#user_interface/display_results.py

import streamlit as st
from .utils import load_responses, save_responses
from response_critique.openai_critique import critique_responses
from answer_generation.generate_answers import generate_answers
from document_processing.process_document import process_document
from advanced_response_generation.generate_advanced_response import generate_advanced_response
from web_search.search_google import get_subvention_context
from advanced_response_generation.pdf_generator import generate_pdf_report


def questions_to_string(questions):
    if isinstance(questions, list):
        return "\n".join(questions)
    return questions

def initialize_session_state():
    if 'summary_advanced_responses' not in st.session_state:
        st.session_state.summary_advanced_responses = {}
    if 'all_advanced_responses' not in st.session_state:
        st.session_state.all_advanced_responses = {}

def string_to_questions(string):
    return [q.strip() for q in string.split("\n") if q.strip()]


def display_results(project_name):
    st.title(f"Résultats pour le projet : {project_name}")

    # Stockage du nom du projet dans session_state avec une clé différente
    st.session_state.current_project_name = project_name

    # Carrousel pour afficher les différentes étapes
    etape = st.selectbox("Étape",
                         ["Contexte et Analyse", "Validation des Questions", "Réponses Préliminaires", "Critiques",
                          "Réponses Avancées"])

    if etape == "Contexte et Analyse":
        afficher_contexte_et_analyse()
    elif etape == "Validation des Questions":
        afficher_validation_questions()
    elif etape == "Réponses Préliminaires":
        afficher_reponses_preliminaires()
    elif etape == "Critiques":
        afficher_critiques()
    elif etape == "Réponses Avancées":
        afficher_reponses_avancees()

    # Boutons de sauvegarde et de génération de rapport PDF
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sauvegarder le projet"):
            sauvegarder_etat_projet()
    with col2:
        if st.button("Générer rapport PDF"):
            generer_rapport_pdf()


def afficher_contexte_et_analyse():
    st.header("Contexte de la subvention et Analyse d'expert")

    if 'subvention_context' not in st.session_state or 'expert_advice' not in st.session_state:
        if st.button("Rechercher des informations en ligne"):
            with st.spinner("Recherche d'informations en cours..."):
                key_info, search_results, subvention_context, expert_advice = get_subvention_context(
                    st.session_state.subv_index)
                st.session_state.subvention_context = subvention_context
                st.session_state.expert_advice = expert_advice

    if 'subvention_context' in st.session_state and 'expert_advice' in st.session_state:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Contexte de la subvention")
            st.markdown(st.session_state.subvention_context)
        with col2:
            st.subheader("Analyse d'expert")
            st.markdown(st.session_state.expert_advice)


def afficher_validation_questions():
    st.header("Validation des Questions")

    col1, col2 = st.columns(2)
    with col1:
        st.write("Questions résumées")
        summary_questions = st.text_area(
            "Modifiez les questions résumées ici",
            value=questions_to_string(st.session_state.summary_questions),
            height=300
        )
    with col2:
        st.write("Toutes les questions")
        all_questions = st.text_area(
            "Modifiez toutes les questions ici",
            value=questions_to_string(st.session_state.extracted_questions),
            height=300
        )

    if st.button("Valider les questions"):
        st.session_state.summary_questions = string_to_questions(summary_questions)
        st.session_state.extracted_questions = string_to_questions(all_questions)
        st.session_state.questions_reviewed = True
        st.success("Questions mises à jour avec succès!")

        if st.session_state.user_path:
            generer_reponses_initiales()


def afficher_reponses_preliminaires():
    st.header("Réponses Préliminaires")

    if not st.session_state.get('responses_generated', False):
        st.warning("Les réponses préliminaires n'ont pas encore été générées. Veuillez d'abord valider les questions.")
        return

    # Affichage des réponses aux questions résumées
    st.subheader("Réponses aux questions résumées")
    for idx, (question, response) in enumerate(st.session_state.summary_responses.items(), start=1):
        st.write(f"Question résumée {idx}: {question}")
        new_response = st.text_area(f"Réponse résumée {idx}", value=response['text'], key=f"summary_response_{idx}")
        st.session_state.summary_responses[question]['text'] = new_response

    # Affichage des réponses à toutes les questions
    st.subheader("Réponses à toutes les questions")
    for idx, (question, response) in enumerate(st.session_state.all_responses.items(), start=1):
        st.write(f"Question complète {idx}: {question}")
        new_response = st.text_area(f"Réponse complète {idx}", value=response['text'], key=f"all_response_{idx}")
        st.session_state.all_responses[question]['text'] = new_response


def afficher_critiques():
    st.header("Critiques")

    if st.button("Générer les critiques"):
        generer_critiques()

    if st.session_state.get('critiques_generated', False):
        # Affichage des critiques pour les questions résumées
        st.subheader("Critiques pour les questions résumées")
        for question, critique in st.session_state.summary_critiques.items():
            st.markdown(f"**Question:** {question}\n\n**Critique:**\n{critique}")

        # Affichage des critiques pour toutes les questions
        st.subheader("Critiques pour toutes les questions")
        for question, critique in st.session_state.all_critiques.items():
            st.markdown(f"**Question:** {question}\n\n**Critique:**\n{critique}")


def afficher_reponses_avancees():
    st.header("Réponses Avancées")

    if st.button("Générer des réponses avancées"):
        generer_reponses_avancees()

    if st.session_state.get('advanced_responses_generated', False):
        afficher_reponses('all')


def afficher_reponses(question_type):
    st.subheader(f"Réponses avancées pour toutes les questions")
    for idx, (question, response_data) in enumerate(st.session_state.all_advanced_responses.items()):
        st.write(f"Question : {question}")
        st.markdown(response_data['text'])

        with st.expander("Voir les détails de la recherche"):
            st.subheader("Nouvelles questions générées")
            for new_q in response_data['new_questions']:
                st.write(f"- {new_q}")

            st.subheader("Recherches supplémentaires")
            for new_q, research in response_data['additional_research'].items():
                st.write(f"Question : {new_q}")
                st.write(f"Résultat de la recherche : {research}")

def generer_reponses_initiales():
    with st.spinner("Génération des réponses initiales en cours..."):
        user_index = process_document(st.session_state.user_path, "gpt-4o-mini")

        # Génération des réponses pour les questions résumées
        summary_responses = generate_answers(st.session_state.summary_questions, user_index.as_query_engine())
        st.session_state.summary_responses = {q: {'text': r} for q, r in summary_responses.items()}

        # Génération des réponses pour toutes les questions
        all_responses = generate_answers(st.session_state.extracted_questions, user_index.as_query_engine())
        st.session_state.all_responses = {q: {'text': r} for q, r in all_responses.items()}

        st.session_state.responses_generated = True
    st.success("Réponses initiales générées pour les questions résumées et complètes!")


def generer_critiques():
    with st.spinner("Génération des critiques en cours..."):
        st.session_state.summary_critiques = critique_responses(
            st.session_state.summary_questions,
            {q: r['text'] for q, r in st.session_state.summary_responses.items()},
            st.session_state.subvention_context,
            st.session_state.expert_advice,
            st.session_state.current_project_name  # Utilisez current_project_name ici
        )
        st.session_state.all_critiques = critique_responses(
            st.session_state.extracted_questions,
            {q: r['text'] for q, r in st.session_state.all_responses.items()},
            st.session_state.subvention_context,
            st.session_state.expert_advice,
            st.session_state.current_project_name  # Utilisez current_project_name ici
        )
        st.session_state.critiques_generated = True
    st.success("Toutes les critiques ont été générées avec succès!")


def generer_reponses_avancees():
    with st.spinner("Génération des réponses avancées en cours..."):
        st.session_state.all_advanced_responses = {}
        total_questions = len(st.session_state.all_responses)
        progress_bar = st.progress(0)

        for idx, (question, response_data) in enumerate(st.session_state.all_responses.items()):
            critique = st.session_state.all_critiques.get(question, "")
            st.text(f"Génération de la réponse avancée pour : {question[:50]}...")
            try:
                advanced_response = generate_advanced_response(
                    question,
                    critique,
                    st.session_state.subvention_context,
                    response_data['text'],
                    st.session_state.user_path
                )
                st.session_state.all_advanced_responses[question] = advanced_response
            except Exception as e:
                error_message = f"Erreur lors de la génération de la réponse avancée pour la question : {question}.\n"
                error_message += f"Type d'erreur : {type(e).__name__}\n"
                error_message += f"Description : {str(e)}\n"
                error_message += "Veuillez vérifier l'encodage du fichier et vous assurer qu'il est lisible."
                st.error(error_message)

            progress_bar.progress((idx + 1) / total_questions)

        st.session_state.advanced_responses_generated = True
    st.success(
        "Processus de génération des réponses avancées terminé. Veuillez vérifier les résultats et les messages d'erreur éventuels.")


def sauvegarder_etat_projet():
    save_responses(st.session_state.current_project_name, {
        "summary_responses": st.session_state.summary_responses,
        "all_responses": st.session_state.all_responses,
        "summary_critiques": st.session_state.get("summary_critiques", {}),
        "all_critiques": st.session_state.get("all_critiques", {}),
        "summary_advanced_responses": st.session_state.get("summary_advanced_responses", {}),
        "all_advanced_responses": st.session_state.get("all_advanced_responses", {})
    })
    st.success("Projet sauvegardé avec succès!")


def generer_rapport_pdf():
    with st.spinner("Génération du rapport PDF en cours..."):
        try:
            pdf_path = generate_pdf_report(st.session_state.current_project_name, st.session_state)
            st.success(f"Rapport PDF généré avec succès! Vous pouvez le télécharger ici: {pdf_path}")

            # Ajouter un bouton de téléchargement
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="Télécharger le rapport PDF",
                    data=pdf_file,
                    file_name=f"{st.session_state.current_project_name}_rapport.pdf",
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Une erreur est survenue lors de la génération du PDF: {str(e)}")