import os
import json
import logging
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.qparser import MultifieldParser
from whoosh.analysis import StemmingAnalyzer

# Set up logging

logger = logging.getLogger("IndexingPipeline")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("indexing_pipeline.log", mode="a")
log_format = logging.Formatter(
    "%(asctime)s - %(name)s - [%(levelname)s] [%(pathname)s:%(lineno)d] - %(message)s - "
    "[%(process)d:%(thread)d]"
)
file_handler.setFormatter(log_format)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
logger.addHandler(console_handler)

# Define the schema for the index

schema = Schema(
    question=TEXT(stored=True, analyzer=StemmingAnalyzer()),
    answer=TEXT(stored=True),
    image=ID(stored=True),
    options=TEXT(stored=True),
)


def create_search_index(json_files_directory, index_dir):
    if not os.path.exists(index_dir):
        os.makedirs(index_dir)

    index = create_in(index_dir, schema)
    writer = index.writer()

    for json_filename in os.listdir(json_files_directory):
        json_file_path = os.path.join(json_files_directory, json_filename)
        if json_file_path.endswith(".json"):
            try:
                with open(json_file_path, "r", encoding="utf-8") as file:
                    questions = json.load(file)
                    for question in questions:
                        concatenated_options = " ".join(
                            [opt["option"] for opt in question["options"]]
                        )
                        writer.add_document(
                            question=question["question"],
                            answer=question["answer"],
                            image=question.get("image", ""),
                            options=concatenated_options,
                        )
            except Exception as e:
                logger.error(
                    f"Failed to process file {json_file_path}: {e}", exc_info=True
                )

    writer.commit()
    logger.info("Indexing completed successfully.")


def search_index(query_str, index_dir):
    try:
        ix = open_dir(index_dir)
        with ix.searcher() as searcher:
            parser = MultifieldParser(["question", "options"], schema=ix.schema)
            query = parser.parse(query_str)
            results = searcher.search(query, limit=None)
            logger.info(f"Search for '{query_str}' returned {len(results)} results.")
            return [result.fields() for result in results]
    except Exception as e:
        logger.error("An error occurred during the search.", exc_info=True)
        return []


if __name__ == "__main__":
    json_files_directory = "your json files directory"  # replace with your json files directory
    index_dir = "indexdir"  # replace with your index directory

    create_search_index(json_files_directory, index_dir)

    query_string = "Why would you use a virtual environment?"  # replace with your actual search term
    search_results = search_index(query_string, index_dir)

    if search_results:
        for result in search_results:
            print(f"Question: {result['question']}")
            print(f"Answer: {result['answer']}")
            if result.get("image"):
                print(f"Image: {result['image']}")
            print("\n")
    else:
        print("No results found.")
