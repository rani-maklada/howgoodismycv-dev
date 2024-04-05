import json
import openai
import re
import os
from tempfile import NamedTemporaryFile
from io import BytesIO
from urllib.parse import urljoin
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from . import resumed
import logging  # Import the logging module
import sys  # Import the sys module
# Basic configuration for logging to terminal
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, format='%(name)s - %(levelname)s - %(message)s')

# configuration for openai
openai.organization = settings.CHATGPT_ORGANIZATION
openai.api_key = settings.CHATGPT_API_KEY

def create_openai_request(content, model="gpt-3.5-turbo"):
    logging.debug(f"Creating OpenAI request with content: {content[:100]}...")  # Log the beginning of a request
    response = openai.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "user",
            "content": f"{content}",
        },
        ],
    )
    logging.debug("OpenAI request completed.")  # Log the completion of a request
    # return response.choices[0].text
    return response.choices[0].message.content

def summarize_resume(text):
    logging.info("Summarizing resume.")  # Log the action
    content = f"Summarize the following resume:\n\n{text}"
    return create_openai_request(content)

def suggestions_resume(text, categories):
    logging.info("Generating suggestions for resume.")  # Log the action
    content = f"""Give suggestions to the following resume.\n
    base your answer on the folowing scores:
    overall score: {categories["overall"]}\n
    skills score: {categories["skills"]}\n
    education score: {categories["education"]}\n
    experience score: {categories["experience"]}\n
    the resume:\n
    {text}"""
    return create_openai_request(content)

def upgrade_resume(text, username, position, document_name):
    # placeholder values
    json_format = read_text_from_file(settings.SCHEMA)
    logging.info("Upgrading resume.")  # Log the action

    # Construct content to be sent for processing
    content = f"""Upgrade the following resume:
    (Please ensure the JSON output is enclosed within triple backticks (```)):
    \n\nResume:\n{text}\n\nSCHEMA:\n{json_format}\n"""
    
    response = create_openai_request(content)
    
    # response extraction process
    resume_data = extract_json(response)

    # Temporary JSON file with manual deletion
    tmp_json_path = None
    tmp_html_path = None
    try:
        with NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as tmp_json:
            write_json_file(tmp_json.name, resume_data)
            tmp_json_path = tmp_json.name  # Store the path for later use

        with NamedTemporaryFile(mode='w+', suffix='.html', delete=False) as tmp_html:
            tmp_html_path = tmp_html.name

        # Rendering the resume
        render_success, message = resumed.render_resume(tmp_json_path, tmp_html_path)
        if not render_success:
            logging.error(f"Failed to render the resume HTML: {message}")
            return None

        with open(tmp_html_path, 'r', encoding='utf-8') as html_file:
            html_content = html_file.read()

        document_content = BytesIO(html_content.encode('utf-8'))
        updated_document_name = f"{document_name}.html"
        user_dir = os.path.join(username, position, "upgraded_pdfs")
        updated_document_path = save_document(user_dir, updated_document_name, document_content)

        logging.debug(f"Document saved at: {updated_document_path}.")

    finally:
        # Cleanup temporary files
        if tmp_json_path and os.path.exists(tmp_json_path):
            os.remove(tmp_json_path)
        if tmp_html_path and os.path.exists(tmp_html_path):
            os.remove(tmp_html_path)

    # Compute the relative path and URL for the updated document
    relative_pdf_path = os.path.relpath(updated_document_path, settings.MEDIA_ROOT)
    upgraded_pdf_url = urljoin(settings.MEDIA_URL, relative_pdf_path.replace('\\', '/'))

    return upgraded_pdf_url

def grammarcheck_resume(text):
    logging.info("Performing grammar check on resume.")  # Log the action
    content = f"Please review this resume content for grammar, punctuation, and overall clarity. Provide suggestions for improvements:\n\n{text}"
    return create_openai_request(content)

def save_document(user_dir, document_name, document_content):
    logging.debug(f"Saving document: {document_name} in user directory: {user_dir}.")  # Log the document saving action
    # Define the directory path for the current user
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, user_dir))

    # Save the document in the defined directory
    filename = fs.save(document_name, document_content)
    fs.url(f'user_dir/{filename}')
    document_path = os.path.join(user_dir, filename)
    return document_path

def extract_json(response):
    logging.debug("Response received for JSON generation.")
    print("response", response)
    json_string_match = re.search(r'```(?:json)?(.*?)```', response, re.DOTALL)
    resume_data = {}
    if json_string_match:
        json_string = json_string_match.group(1).strip()
        try:
            resume_data = json.loads(json_string)
            logging.info("Resume data parsed successfully into JSON.")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON: {e}")
    else:
        logging.warning("No JSON found in the response.")
    return resume_data

def generate_json(text):
    logging.info("Starting JSON generation from resume.")
    json_format = read_text_from_file(settings.SCHEMA)
    content = f"""Extract and structure the information from the following resume into JSON format based on the given schema.
    Please ensure the JSON output is enclosed within triple backticks (```) for clear demarcation:
    \n\nResume:\n{text}\n\nSCHEMA:\n{json_format}\n"""
    return create_openai_request(content)

def extract_rating(response_text):
    matches = re.findall(r"\d+", response_text)
    rating = int(matches[0]) if matches else None
    logging.debug(f"Extracted rating: {rating}")
    return rating

def score_category(text, category, position=""):
    logging.info(f"Scoring category: {category} for position: {position}")
    contents = {
        'overall': "Rate the resume over all from 1 to 100.",
        'skills': "Rate the skills section of the candidate resume from 1 to 100.",
        'education': f"Rate the education section of the candidate resume from 1 to 100 for {position} position",
        'experience': f"Rate the work experience of the candidate resume from 1 to 100 for {position} position."
    }
    response = create_openai_request(f"{contents[category]}\n\n{text}")
    return response

def evaluate_categories(text, position):
    logging.info("Evaluating categories for resume.")
    categories = ['skills', 'education', 'experience']  # Removed 'overall' from initial categories list
    scores = {}
    for category in categories:
        response = score_category(text, category, position)
        # Try the standard pattern first
        pattern_standard = r'(\d+)\s+out\s+of\s+(\d+)'
        matches_standard = re.search(pattern_standard, response)
        if matches_standard:
            score_numerical = (int(matches_standard.group(1)) / int(matches_standard.group(2))) * 100
            scores[category] = score_numerical
        else:
            # Search for any number that is within 0 to 100
            pattern_any_number = r'\b(100|[1-9]?[0-9])\b'
            matches_any_number = re.search(pattern_any_number, response)
            if matches_any_number:
                score_numerical = float(matches_any_number.group(0))
                scores[category] = score_numerical
            else:
                logging.warning(f"No valid score found for category {category} in position {position}.")
                scores[category] = 0  # Default value if no score is found
    
    # Calculate the mean of scores for 'skills', 'education', and 'experience' then assign it to 'overall'
    if scores:  # Ensure there is at least one score to avoid division by zero
        overall_score = sum(scores.values()) / len(scores)
        scores['overall'] = overall_score
    else:
        scores['overall'] = 0  # Default value if no scores were found
    
    logging.debug(f"Evaluated categories with scores: {scores}")
    return scores

def analyze_resume(text, position):
    logging.info(f"Analyzing resume for position: {position}.")
    analysis_result = {}
    analysis_result["categories"] = evaluate_categories(text, position)
    analysis_result["summarize"] = summarize_resume(text)
    analysis_result["suggestions"] = suggestions_resume(text, analysis_result["categories"])
    analysis_result["grammarcheck"] = grammarcheck_resume(text)
    return analysis_result

def read_text_from_file(file_path):
    logging.debug(f"Reading text from file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_json_file(filename, data):
    logging.info(f"Writing data to JSON file: {filename}")
    with open(filename, 'w', encoding="utf-8") as file:
        file.write(json.dumps(data, ensure_ascii=False, indent=4))
