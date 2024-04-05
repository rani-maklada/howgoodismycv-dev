from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from .models import UploadedDocument, AnalysisResult, Video
from django.contrib import messages
from django.conf import settings
from .forms import SignUpForm
from .parsing import pdf_parser
from .APIs import chatGPT, googleApis
from .mongodb import GetSkills
from django.contrib import messages
import os
import logging
import json

# Configure logging
logger = logging.getLogger(__name__)

def base(request):
    logger.debug("Redirecting from base to home.")
    return redirect('home')

def home(request):
    video = Video.objects.all()
    logger.debug("Rendering home page.")
    return render(request, 'myapp/home.html', {"video":video})

def contact(request):
    logger.debug("Rendering contact page.")
    return render(request, 'myapp/contact.html')

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    logger.debug("Accessing dashboard for user: %s", request.user.username)
    # Fetch the most recent UploadedDocument for the current user
    last_uploaded_document = UploadedDocument.objects.filter(user=request.user).order_by('-id').first()

    # Initialize analysis_result as None in case there are no uploaded documents/analysis results
    analysis_result = None
    missing_skills_json = "[]"  # Initialize with an empty list in JSON format
    google_images_json = '[]'
    if last_uploaded_document:
        # Try to fetch the corresponding AnalysisResult for the most recent UploadedDocument
        analysis_result = AnalysisResult.objects.filter(uploaded_document=last_uploaded_document).first()
        if analysis_result and analysis_result.missingskills:
            # Convert the missingskills string to JSON format for the JavaScript
            # Ensure the missingskills field contains valid JSON before calling json.loads
            try:
                missing_skills = json.loads(analysis_result.missingskills)
                missing_skills_json = json.dumps(missing_skills)
                google_images = json.loads(analysis_result.googleimages)
                google_images_json = json.dumps(google_images)
            except json.JSONDecodeError as e:
                logger.error("Error decoding JSON from missingskills: %s", e)
                missing_skills_json = "[]"
                google_images_json = '[]'

    # Pass the last uploaded document, its analysis result, and the missing skills JSON to the dashboard template
    context = {
        'last_uploaded_document': last_uploaded_document,
        'analysis_result': analysis_result,
        'missing_skills_json': missing_skills_json,  # Add the missing skills JSON to the context
        'google_images_json': google_images_json,  # Add the google images JSON to the context
    }
    print("google_images_json:",google_images_json)
    return render(request, 'myapp/dashboard.html', context)



@login_required
def upload(request):
    if request.method == 'POST':
        position = request.POST.get('position')
        document = request.FILES.get('document')
        logger.debug("Uploading document: %s for position: %s by user: %s", document.name, position, request.user.username)
        if document:
            # Define the directory path for the current user and position
            user_dir = f'{request.user.username}\{position}'
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, user_dir))

            # Save the document in the defined directory
            document_name = fs.save(document.name, document)
            fs.url(f'{user_dir}/{document_name}')
            document_path = os.path.join(user_dir, document_name)
            # Assuming you have a model to store the upload information
            # Here we save the upload information including the user, position, and document path
            uploaded_document  = UploadedDocument.objects.create(
                user=request.user,
                position=position,
                document=document_path  # Save the relative path
            )
            logger.debug("Document uploaded successfully: %s", document_path)
            document_name = os.path.splitext(document_name)
            print("document_name",document_name[0])
            analyze_and_save_results(document_name[0], uploaded_document, position, request)
            # Redirect to dashboard
            return redirect('dashboard')

    # If GET request or any other condition, render the upload page again
    return render(request, 'myapp/upload.html')

def analyze_document(document_name, document_path, position, username):
    text = pdf_parser.extract_text_from_pdf(document_path)
    json = chatGPT.generate_json(text)
    analysis_result = chatGPT.analyze_resume(json, position)
    analysis_result["upgradedpdf"] = chatGPT.upgrade_resume(json, username, position,document_name)
    analysis_result["missingskills"] = GetSkills.get_missing_skills(text, position)
    analysis_result["googleimages"] = googleApis.get_similar_resume_image_url(position)
    return analysis_result

def analyze_and_save_results(document_name, uploaded_document, position, request):
    document_path = os.path.join(settings.MEDIA_ROOT, str(uploaded_document.document))
    try:
        logger.debug("Analyzing document for uploaded_document ID: %s", uploaded_document.id)
        results = analyze_document(document_name, document_path, position, request.user.username)
        # If analyze_document and result processing succeed:
        analysis_result = AnalysisResult.objects.create(
            uploaded_document=uploaded_document,
            overall_score=results["categories"]["overall"],
            skills_score=results["categories"]["skills"],
            edu_score=results["categories"]["education"],
            exp_score=results["categories"]["experience"],
            summarize=results["summarize"],
            suggestions=results["suggestions"],
            grammarcheck=results["grammarcheck"],
            upgraded_pdf=results["upgradedpdf"],
        )
        analysis_result.set_googleimages(results["googleimages"])
        analysis_result.set_missingskills(results["missingskills"])
        analysis_result.save()
        logger.debug("Analysis results saved successfully for uploaded_document ID: %s", uploaded_document.id)
        return analysis_result
    except Exception as e:
        logger.error("Error analyzing document for uploaded_document ID: %s: %s", uploaded_document.id, e)
        messages.error(request, "An error occurred while analyzing the document. Please try again.")
        return redirect('upload')



def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user:
                login(request, user)
                logger.info("New user registered and logged in: %s", username)
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'myapp/signup.html', {'form': form})
