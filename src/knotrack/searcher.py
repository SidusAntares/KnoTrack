from knotrack import Database

def search_documents(query: str,db: Database, limit: int = 20):
    """
    Search for documents in the database that match the given query.

    Args:
        query (str): The search query.
        db (Database): The database instance to search in.
        limit (int, optional): The maximum number of results to return. Defaults to 20.

    Returns:
        list: A list of ScanDoc instances that match the search query.
    """
    results = db.search_scan_docs(query)
    return results[:limit]