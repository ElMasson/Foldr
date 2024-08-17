def extract_key_info(document_index):
    query = """
    Extrais le nom du concours ou de la subvention et l'organisme responsable de cette subvention.
    Réponds uniquement avec ces informations au format 'Nom du concours/subvention: [nom], Organisme: [organisme]'.
    """
    result = document_index.as_query_engine().query(query)
    return result.response