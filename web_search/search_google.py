#web_search/search_google.py

import os
import requests
from config.config import GOOGLE_API_KEY, GOOGLE_CSE_ID


def search_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={query}"
    response = requests.get(url)
    if response.status_code == 200:
        result = response.json()
        return result.get('items', [])
    else:
        print(f"An error occurred: {response.status_code}")
        return []


def get_subvention_context(document_index):
    from .utils import extract_key_info
    from .process_search_results import process_search_results, expert_analysis

    key_info = extract_key_info(document_index)
    search_query = f"{key_info} informations concours subvention"
    search_results = search_google(search_query)
    context_summary = process_search_results(search_results, key_info)
    expert_advice = expert_analysis(context_summary)
    return key_info, search_results, context_summary, expert_advice