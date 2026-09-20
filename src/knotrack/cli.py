import argparse
from pathlib import Path

from .scanner import scan_doc
from .indexer import index_documents
from .searcher import search_documents
from .database import Database

def main(argv=None):
    parser = argparse.ArgumentParser(description="Knotrack CLI")
    common_parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands")

    common_parser.add_argument("--db",
        type=Path,
        default=Path(".knotrack.db"),
        help="Path to the database file")

    index_parser = subparsers.add_parser("index",
                                        parents=[common_parser],
                                        help="Index documents")
    index_parser.add_argument("paths", nargs="+",
                              type = Path,
                              help="Paths to scan and index")

    search_parser = subparsers.add_parser("search",
                                        parents=[common_parser],
                                        help="Search documents")
    search_parser.add_argument("query",
                               type = str,
                               help="Search query")
    search_parser.add_argument("--limit",
                               type=int,
                               default=20,
                               help="Maximum number of results to return")

    search_parser.set_defaults(func = search_command)
    index_parser.set_defaults(func = index_command)

    args = parser.parse_args(argv)

    if not hasattr(args, 'func'):
        parser.print_help()
        return

    args.func(args)

def index_command(args):
    db = Database(args.db)
    documents = []
    for path in args.paths:
        documents.extend(scan_doc(path))
    index_documents(documents, db)
    db.close()

def search_command(args):
    db = Database(args.db)
    search_results = search_documents(args.query, db, args.limit)
    for result in search_results:
        print(f"Title: {result.title} \n \
            Path: {result.path} \n \
            Size: {result.size} bytes\n")
    db.close()