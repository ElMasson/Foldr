#user_interface/sidebar_config.py

import streamlit as st
import os
from .utils import get_previous_projects, get_previous_files, save_uploaded_file, get_project_files, save_project_files


def sidebar_config():
    with st.sidebar:
        st.image("img/foldr_logo.jpeg", width=200)
        st.title("Configuration")

        previous_projects = get_previous_projects()
        project_option = st.selectbox("Sélectionner un projet existant", ["Nouveau projet"] + previous_projects)

        if project_option == "Nouveau projet":
            project_name = st.text_input("Nom du projet (obligatoire)", key="project_name")
            subvention_path = None
            user_path = None
        else:
            project_name = project_option
            project_files = get_project_files(project_name)
            subvention_path = project_files["subvention"]
            user_path = project_files["user"]

        subvention_options = ["Uploader un nouveau fichier"] + get_previous_files("subvention")
        default_subvention_index = subvention_options.index(os.path.basename(subvention_path)) if subvention_path else 0
        subvention_option = st.selectbox("Document de subvention", subvention_options, index=default_subvention_index)

        if subvention_option == "Uploader un nouveau fichier":
            subvention_file = st.file_uploader("Document de subvention (obligatoire)", type=["docx", "pdf"])
            if subvention_file:
                subvention_path = save_uploaded_file(subvention_file, "subvention")
        else:
            subvention_path = os.path.join("files", subvention_option)

        user_options = ["Uploader un nouveau fichier"] + get_previous_files("user")
        default_user_index = user_options.index(os.path.basename(user_path)) if user_path else 0
        user_option = st.selectbox("Document utilisateur", user_options, index=default_user_index)

        if user_option == "Uploader un nouveau fichier":
            user_file = st.file_uploader("Document utilisateur (obligatoire)", type=["pdf"])
            if user_file:
                user_path = save_uploaded_file(user_file, "user")
        else:
            user_path = os.path.join("files", user_option)

        analyze_button = st.button("Analyser", disabled=not (project_name and subvention_path and user_path))

        if project_name and subvention_path and user_path:
            save_project_files(project_name, subvention_path, user_path)

        return project_name, subvention_path, user_path, analyze_button