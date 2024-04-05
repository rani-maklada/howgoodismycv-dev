import requests
from django.conf import settings
import os

def query_pdf_for_information(document_path, query, delete_after=True):
    query = "Extract and structure the information from the following resume into JSON format"
    api_key = settings.CHATPDF_API_KEY
    
    headers = {'x-api-key': api_key, "Content-Type": "application/json"}
    upload_endpoint = 'https://api.chatpdf.com/v1/sources/add-file'
    chat_endpoint = 'https://api.chatpdf.com/v1/chats/message'
    delete_endpoint = 'https://api.chatpdf.com/v1/sources/delete'

    # Upload PDF
    try:
        with open(document_path, 'rb') as file:
            files = {'file': (os.path.basename(document_path), file, 'application/pdf')}
            response = requests.post(upload_endpoint, headers={'x-api-key': api_key}, files=files)
            response.raise_for_status()  # This will raise an error for non-200 responses
            source_id = response.json()['sourceId']
    except requests.exceptions.RequestException as e:
        return f"Error uploading PDF: {str(e)}"

    # Chat with PDF
    chat_data = {
        "sourceId": source_id,
        "messages": [
            {"role": "user", "content": query}
        ]
    }
    try:
        response = requests.post(chat_endpoint, headers=headers, json=chat_data)
        response.raise_for_status()  # This will raise an error for non-200 responses
        chat_content = response.json()['content']
    except requests.exceptions.RequestException as e:
        return f"Error chatting with PDF: {str(e)}"

    # Delete PDF (optional)
    if delete_after:
        delete_data = {"sources": [source_id]}
        try:
            response = requests.post(delete_endpoint, headers=headers, json=delete_data)
            response.raise_for_status()  # This will raise an error for non-200 responses
        except requests.exceptions.RequestException as e:
            print(f"Warning: Failed to delete PDF: {str(e)}")

    return chat_content, source_id