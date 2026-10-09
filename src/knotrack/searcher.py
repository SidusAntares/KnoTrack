"""Apply the caller's result limit to the documents a search returns.

A thin layer over Database.search_scan_docs: the database decides what matches and in which
order, and this module only caps how many of those results are handed back.
"""

from .database import Database

def search_documents(query: str,db: Database, limit: int = 20):
    """
    Search for documents in the database that match the given query.

    Args:
        query (str): The search query.
        db (Database): The database instance to search in.
        limit (int, optional): The maximum number of results to return. Defaults to 20.

    Returns:
        list: The best matching results, each a (ScanDoc, snippet) pair, in ranking order.
    """
    results = db.search_scan_docs(query)
    return results[:limit]
