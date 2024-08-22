import streamlit as st
from .utils import load_responses, save_responses
from response_critique.critique_generator import critique_responses
from answer_generation.generate_answers import generate_answers
from document_processing.process_document import process_document


def questions_to_string(questions):
    if isinstance(questions, list):
        return "\n".join(questions)
    return questions


def string_to_questions(string):
    return [q.strip() for q in string.split("\n") if q.strip()]


def display_results(project_name):
    st.title(f"Résultats pour le projet : {project_name}")

    # Affichage du contexte et de l'analyse d'expert
    with st.expander("Contexte de la subvention et Analyse d'expert", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Contexte de la subvention")
            st.markdown(st.session_state.subvention_context)
        with col2:
            st.subheader("Analyse d'expert")
            st.markdown(st.session_state.expert_advice)

    # Affichage et édition des questions
    st.subheader("Questions identifiées")

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

        # Vérification de la disponibilité de user_path avant le traitement
        if st.session_state.user_path:
            with st.spinner("Génération des réponses en cours..."):
                user_index = process_document(st.session_state.user_path, "gpt-4o-mini")

                # Génération des réponses pour les questions résumées
                summary_responses = generate_answers(st.session_state.summary_questions, user_index.as_query_engine())
                st.session_state.summary_responses = {q: {"text": r, "rating": "Neutre"} for q, r in
                                                      summary_responses.items()}

                # Génération des réponses pour toutes les questions
                all_responses = generate_answers(st.session_state.extracted_questions, user_index.as_query_engine())
                st.session_state.all_responses = {q: {"text": r, "rating": "Neutre"} for q, r in all_responses.items()}

                st.session_state.responses_generated = True
            st.success("Réponses initiales générées pour les questions résumées et complètes!")
        else:
            st.error("Erreur : Le chemin du document utilisateur n'est pas défini. Veuillez réanalyser le projet.")

    if st.session_state.responses_generated:
        # Affichage des réponses aux questions résumées
        st.subheader("Réponses aux questions résumées")
        for idx, (question, response_data) in enumerate(st.session_state.summary_responses.items(), start=1):
            st.write(f"Question résumée {idx}: {question}")
            new_response = st.text_area(f"Réponse résumée {idx}", value=response_data['text'],
                                        key=f"summary_response_{idx}")
            rating = st.radio("Évaluation", ["👍", "👎", "Neutre"], key=f"summary_rating_{idx}",
                              index=["👍", "👎", "Neutre"].index(response_data['rating']))
            st.session_state.summary_responses[question] = {"text": new_response, "rating": rating}

        # Affichage des réponses à toutes les questions
        st.subheader("Réponses à toutes les questions")
        for idx, (question, response_data) in enumerate(st.session_state.all_responses.items(), start=1):
            st.write(f"Question complète {idx}: {question}")
            new_response = st.text_area(f"Réponse complète {idx}", value=response_data['text'],
                                        key=f"all_response_{idx}")
            rating = st.radio("Évaluation", ["👍", "👎", "Neutre"], key=f"all_rating_{idx}",
                              index=["👍", "👎", "Neutre"].index(response_data['rating']))
            st.session_state.all_responses[question] = {"text": new_response, "rating": rating}

        if st.button("Générer les critiques"):
            st.subheader("Génération des critiques en cours...")

            # Création d'espaces réservés pour les critiques
            summary_critique_placeholders = [st.empty() for _ in st.session_state.summary_responses]
            all_critique_placeholders = [st.empty() for _ in st.session_state.all_responses]

            # Fonction pour générer et afficher les critiques
            def generate_and_display_critiques(responses, placeholders, critique_type):
                critiques = {}
                for (question, response_data), placeholder in zip(responses.items(), placeholders):
                    with st.spinner(f"Génération de la critique pour la question {critique_type}..."):
                        critique = critique_responses(
                            [question],
                            {question: response_data["text"]},
                            st.session_state.subvention_context,
                            st.session_state.expert_advice,
                            project_name
                        )
                    critiques[question] = critique[question]
                    placeholder.markdown(
                        f"**{critique_type} - Question:** {question}\n\n**Critique:**\n{critique[question]}")
                return critiques

            # Génération et affichage des critiques pour les questions résumées
            st.write("Critiques pour les questions résumées :")
            st.session_state.summary_critiques = generate_and_display_critiques(
                st.session_state.summary_responses,
                summary_critique_placeholders,
                "Résumé"
            )

            # Génération et affichage des critiques pour toutes les questions
            st.write("Critiques pour toutes les questions :")
            st.session_state.all_critiques = generate_and_display_critiques(
                st.session_state.all_responses,
                all_critique_placeholders,
                "Complète"
            )

            st.session_state.critiques_generated = True
            st.success("Toutes les critiques ont été générées avec succès!")

    # Ajout d'un bouton pour sauvegarder l'état actuel du projet
    if st.button("Sauvegarder le projet"):
        save_responses(project_name, {
            "summary_responses": st.session_state.summary_responses,
            "all_responses": st.session_state.all_responses,
            "summary_critiques": st.session_state.get("summary_critiques", {}),
            "all_critiques": st.session_state.get("all_critiques", {})
        })
        st.success("Projet sauvegardé avec succès!")