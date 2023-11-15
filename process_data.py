import os
import json
import markdown2
import re

# Get the markdown files directory

cloned_repository_directory = r"C:\Users\Harminder Nijjar\Desktop\blog\kb-blog-portfolio-mkdocs-master\scripts\linkedin-skill-assessments-quizzes"

# Create a folder to store the JSON files

output_folder = os.path.join(cloned_repository_directory, "json_output")

# Create the output folder if it doesn't exist

os.makedirs(output_folder, exist_ok=True)

# Create a list to store data for each MD file

data_for_each_md = []

# Iterate through the Markdown files (\*.md) in the current directory and its subdirectories

for root, dirs, files in os.walk(cloned_repository_directory):
    for name in files:
        if name.endswith(".md"): # Construct the full path to the Markdown file
            md_file_path = os.path.join(root, name)

            # Read the Markdown file
            with open(md_file_path, "r", encoding="utf-8") as md_file:
                md_content = md_file.read()

            # Split the content into sections for each question and answer
            sections = re.split(r"####\s+Q\d+\.", md_content)

            # Remove the first empty section
            sections.pop(0)

            # Create a list to store questions and answers for this MD file
            questions_and_answers = []

            # Iterate through sections and extract questions and answers
            for section in sections:
                # Split the section into lines
                lines = section.strip().split("\n")

                # Extract the question
                question = lines[0].strip()

                # Extract the answers
                answers = [line.strip() for line in lines[1:] if line.strip()]

                # Create a dictionary for this question and answers
                qa_dict = {"question": question, "answers": answers}

                # Append to the list of questions and answers
                questions_and_answers.append(qa_dict)

            # Create a dictionary for this MD file
            md_data = {
                "markdown_file": name,
                "questions_and_answers": questions_and_answers,
            }

            # Append to the list of data for each MD file
            data_for_each_md.append(md_data)

# Save JSON files in the output folder

for md_data in data_for_each_md:
    json_file_name = os.path.splitext(md_data["markdown_file"])[0] + ".json"
    json_file_path = os.path.join(output_folder, json_file_name)
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(md_data, json_file, indent=4)

print(f"JSON files created for each MD file in the '{output_folder}' folder.")