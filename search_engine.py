import os
import json
import re
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import MultifieldParser
from whoosh.analysis import StemmingAnalyzer

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
                    data = json.load(file)
                    for question_data in data["questions_and_answers"]:
                        question_text = question_data["question"]
                        answer_text = "\n".join(question_data["answers"])
                        image_id = data.get("image_id")
                        options = question_data.get("options", "")
                        writer.add_document(
                            question=question_text,
                            answer=answer_text,
                            image=image_id,
                            options=options,
                        )
            except Exception as e:
                print(f"Failed to process file {json_file_path}: {e}")

    writer.commit()
    print("Indexing completed successfully.")


def extract_correct_answer(answer_text):
    # Use regular expression to find the portion with "- [x]"
    match = re.search(r"- \[x\].*", answer_text)
    if match:
        return match.group()
    return None


def search_index(query_str, index_dir):
    try:
        ix = open_dir(index_dir)
        with ix.searcher() as searcher:
            parser = MultifieldParser(["question", "options"], schema=ix.schema)
            query = parser.parse(query_str)
            results = searcher.search(query, limit=None)
            print(f"Search for '{query_str}' returned {len(results)} results.")
            return [
                {
                    "question": result["question"],
                    "correct_answer": extract_correct_answer(result["answer"]),
                    "image": result.get("image"),
                }
                for result in results
            ]
    except Exception as e:
        print("An error occurred during the search.")
        return []


if __name__ == "__main__":
    json_files_directory = r"C:\Users\Harminder Nijjar\Desktop\blog\kb-blog-portfolio-mkdocs-master\scripts\linkedin-skill-assessments-quizzes\json_output"  # Replace with your JSON files directory path
    index_dir = "index"  # Replace with your index directory path

    create_search_index(json_files_directory, index_dir)

    original_string = "Why would you use a virtual environment?"  # Replace with your actual search term
    # Remove the special characters from the original string
    query_string = re.sub(r"[^a-zA-Z0-9\s]", "", original_string)
    query_string = query_string.lower()
    query_string = query_string.strip()
    search_results = search_index(query_string, index_dir)

    if search_results:
        for result in search_results:
            print(f"Question: {result['question']}")
            # Remove the "- [x]" portion from the answer
            print(f"Correct answer: {result['correct_answer'].replace('- [x] ', '')}")
            if result.get("image"):
                print(f"Image: {result['image']}")
            print("\n")
        print(f"Search for '{original_string}' completed successfully.")
        print(f"Found {len(search_results)} results.")
    else:
        print("No results found.")
