import streamlit as st
from .utils import load_responses, save_responses


def display_results(project_name, summary_questions, key_info, subvention_context, expert_advice, subv_responses):
    st.title(f"Résultats pour le projet : {project_name}")

    with st.expander("Informations sur la subvention", expanded=True):
        st.subheader("Détails de la subvention")
        st.write(key_info)

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Résumé du contexte")
            st.markdown(subvention_context)

        with col2:
            st.subheader("Analyse d'expert")
            st.markdown(expert_advice)

    with st.expander("Vision synthétique", expanded=True):
        responses = load_responses(project_name)

        for idx, question in enumerate(summary_questions.split('\n'), start=1):
            st.subheader(f"Question {idx}")
            question_text = question.split('. ', 1)[1] if '. ' in question else question
            st.write(question_text)

            response_file = f"output/{project_name}/sumr_responses/response_{idx}.md"
            with open(response_file, "r") as f:
                original_response = f.read().split("### Réponse trouvée dans le document\n\n", 1)[1]

            response_key = f"question_{idx}"
            current_response = responses.get(response_key, {}).get("response", original_response)

            col1, col2 = st.columns([3, 1])
            with col1:
                new_response = st.text_area("Réponse", value=current_response, height=200, key=f"response_{idx}")
            with col2:
                rating = st.radio("Évaluation", ["👍", "👎", "Neutre"], key=f"rating_{idx}", index=2)

            if st.button("Enregistrer les modifications", key=f"save_{idx}"):
                responses[response_key] = {
                    "response": new_response,
                    "rating": rating
                }
                save_responses(project_name, responses)
                st.success("Modifications enregistrées avec succès!")

            st.markdown("---")

    with st.expander("Réponses à toutes les questions du dossier de subvention", expanded=False):
        all_responses = load_responses(project_name, "all_responses")

        for idx, (question, original_response) in enumerate(subv_responses.items(), start=1):
            st.subheader(f"Question {idx}")
            st.write(question)

            response_key = f"all_question_{idx}"
            current_response = all_responses.get(response_key, {}).get("response", original_response)

            col1, col2 = st.columns([3, 1])
            with col1:
                new_response = st.text_area("Réponse", value=current_response, height=200, key=f"all_response_{idx}")
            with col2:
                rating = st.radio("Évaluation", ["👍", "👎", "Neutre"], key=f"all_rating_{idx}", index=2)

            if st.button("Enregistrer les modifications", key=f"all_save_{idx}"):
                all_responses[response_key] = {
                    "response": new_response,
                    "rating": rating
                }
                save_responses(project_name, all_responses, "all_responses")
                st.success("Modifications enregistrées avec succès!")

            st.markdown("---")