from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
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
def dashboard(request, id):
    logger.debug("Accessing dashboard for user: %s with analysis result ID: %s", request.user.username, id)
    
    # Fetch the AnalysisResult object by its ID
    analysis_result = get_object_or_404(AnalysisResult, id=id, uploaded_document__user=request.user)
    
    # Deserialize JSON fields directly from the AnalysisResult object
    missing_skills = json.loads(analysis_result.get_missingskills())
    google_images = json.loads(analysis_result.get_googleimages())
    
    context = {
        'analysis_result': analysis_result,
        'missing_skills_json': json.dumps(missing_skills),
        'google_images_json': json.dumps(google_images),
    }
    return render(request, 'myapp/dashboard.html', context)

@login_required
def upload(request):
    if request.method == 'POST':
        position = request.POST.get('position')
        document = request.FILES.get('document')
        logger.debug("Uploading document: %s for position: %s by user: %s", document.name, position, request.user.username)
        
        if document:
            user_dir = f'{request.user.username}/{position}'
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, user_dir))
            document_name_wiht_ext = fs.save(document.name, document)
            document_name = os.path.splitext(document_name_wiht_ext)[0]
            fs.url(f'{user_dir}/{document_name_wiht_ext}')
            document_path = os.path.join(user_dir, document_name_wiht_ext)
            uploaded_document = UploadedDocument.objects.create(
                user=request.user,
                position=position,
                document=document_path
            )
            
            analysis_result = analyze_and_save_results(document_name, uploaded_document, position, request)
            if analysis_result:
                request.session['analysis_result'] = analysis_result.id
                return redirect('dashboard', id=analysis_result.id)
            else:
                messages.error(request, "An error occurred while analyzing the document. Please try again.")
                return render(request, 'myapp/upload.html', {'position': position})
            
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

        # Assuming results contains all necessary information already
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
        analysis_result.set_googleimages(json.dumps(results["googleimages"]))
        analysis_result.set_missingskills(json.dumps(results["missingskills"]))
        analysis_result.save()
        return analysis_result
    except Exception as e:
        logger.error("Error analyzing document for uploaded_document ID: %s: %s", uploaded_document.id, e)
        return None

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
