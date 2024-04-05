from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

def save(username, document, position):
    # Define the directory path for the current user and position
    user_dir = f'{username}\{position}'
    fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, user_dir))

    # Save the document in the defined directory
    filename = fs.save(document.name, document)
    fs.url(f'{user_dir}/{filename}')
    document_path = os.path.join(user_dir, filename)