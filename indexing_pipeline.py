import os
import json
import whoosh
from whoosh.fields import TEXT, ID, Schema
from whoosh.index import create_in

# Define the directory where your processed JSON files are located
json_files_directory = r"C:\Users\Harminder Nijjar\Desktop\blog\kb-blog-portfolio-mkdocs-master\scripts\linkedin-skill-assessments-quizzes\json_output"

# Define the directory where you want to create the Whoosh index
index_directory = r"C:\Users\Harminder Nijjar\Desktop\blog\kb-blog-portfolio-mkdocs-master\scripts\linkedin-skill-assessments-quizzes\index"

# Create the schema for the Whoosh index
schema = Schema(
    markdown_file=ID(stored=True),
    question=TEXT(stored=True),
    answers=TEXT(stored=True),
)

# Create the index directory if it doesn't exist
os.makedirs(index_directory, exist_ok=True)

# Create the Whoosh index
index = create_in(index_directory, schema)

# Open the index writer
writer = index.writer()

# Iterate through JSON files and add documents to the index
for json_file_name in os.listdir(json_files_directory):
    if json_file_name.endswith(".json"):
        json_file_path = os.path.join(json_files_directory, json_file_name)
        with open(json_file_path, "r", encoding="utf-8") as json_file:
            json_data = json.load(json_file)
            # Extract 'question' and 'answers' from the JSON file
            question = json_data.get("question", "")
            answers = json_data.get("answers", [])
            # Combine 'question' and 'answers' into a single field for searching
            content = f"{question} {' '.join(answers)}"
            writer.add_document(
                markdown_file=json_file_name,
                question=content,
                answers=answers,  # Use the extracted 'answers' or an empty list if not present
            )

# Commit changes to the index
writer.commit()

print("Indexing completed.")
