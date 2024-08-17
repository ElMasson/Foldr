import streamlit as st
import os
import json
import time


def get_previous_projects():
    if os.path.exists("output/projects.json"):
        with open("output/projects.json", "r") as f:
            return json.load(f)
    return []


def save_project(project_name):
    projects = get_previous_projects()
    if project_name not in projects:
        projects.append(project_name)
        with open("output/projects.json", "w") as f:
            json.dump(projects, f)


def get_previous_files(file_type):
    files = [f for f in os.listdir("files") if f.endswith((".docx", ".pdf"))]
    return [f for f in files if (file_type == "subvention" and f.startswith("subvention_")) or
            (file_type == "user" and f.startswith("user_"))]


def save_uploaded_file(uploaded_file, file_type):
    if uploaded_file is not None:
        file_name = f"{file_type}_{uploaded_file.name}"
        file_path = os.path.join("files", file_name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return file_path
    return None


def get_project_files(project_name):
    project_file = f"output/{project_name}/project_files.json"
    if os.path.exists(project_file):
        with open(project_file, "r") as f:
            return json.load(f)
    return {"subvention": None, "user": None}


def save_project_files(project_name, subvention_path, user_path):
    project_file = f"output/{project_name}/project_files.json"
    os.makedirs(os.path.dirname(project_file), exist_ok=True)
    with open(project_file, "w") as f:
        json.dump({"subvention": subvention_path, "user": user_path}, f)


def load_responses(project_name, response_type="summary"):
    responses_file = f"output/{project_name}/{response_type}_responses.json"
    if os.path.exists(responses_file):
        with open(responses_file, "r") as f:
            return json.load(f)
    return {}


def save_responses(project_name, responses, response_type="summary"):
    responses_file = f"output/{project_name}/{response_type}_responses.json"
    with open(responses_file, "w") as f:
        json.dump(responses, f)


def run_analysis(project_name, subvention_path, user_path, process_document, extract_questions, summarize_questions,
                 generate_answers, generate_subvention_answers, get_subvention_context):
    progress_bar = st.progress(0)
    status_area = st.empty()

    def update_progress(progress, message):
        progress = max(0, min(100, progress))
        progress_bar.progress(progress / 100)
        status_area.info(message)
        time.sleep(0.1)

    update_progress(0, "Démarrage de l'analyse...")

    update_progress(10, "Analyse du document de subvention...")
    subv_index = process_document(subvention_path, "gpt-4o-mini")
    update_progress(15, "Extraction des éléments clés du document de subvention...")

    update_progress(20, "Recherche d'informations complémentaires sur Internet...")
    key_info, search_results, subvention_context, expert_advice = get_subvention_context(subv_index)

    update_progress(30, "Extraction des questions du document de subvention...")
    subv_questions_response = extract_questions(subv_index.as_query_engine(), "mistral-large-latest")
    subv_questions = subv_questions_response.response.split('\n')
    update_progress(35, "Résumé des questions principales...")
    summary_questions = summarize_questions(subv_questions, "mistral-large-latest")

    update_progress(40, "Analyse du document utilisateur...")
    user_index = process_document(user_path, "gpt-4o-mini")
    update_progress(50, "Extraction des éléments clés du document utilisateur...")

    update_progress(60, "Génération des réponses basées sur le document utilisateur...")
    generate_answers(summary_questions.split('\n'), user_index.as_query_engine(),
                     f"output/{project_name}/sumr_responses")

    update_progress(70, "Génération des réponses pour toutes les questions du dossier de subvention...")
    subv_responses = generate_subvention_answers(subv_questions, user_index.as_query_engine(),
                                                 f"output/{project_name}/subv_responses", update_progress)

    update_progress(100, "Analyse terminée !")
    time.sleep(1)
    progress_bar.empty()
    status_area.empty()

    st.sidebar.success("Analyse terminée avec succès !")
    return summary_questions, key_info, subvention_context, expert_advice, subv_responses