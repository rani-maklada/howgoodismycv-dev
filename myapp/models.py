from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
import json

class UploadedDocument(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    document = models.FileField(upload_to='documents/')
    def __str__(self):
        return f"Document: {self.document.name}"


class AnalysisResult(models.Model):
    uploaded_document = models.ForeignKey(UploadedDocument, on_delete=models.CASCADE, related_name='analysis_results')
    overall_score = models.FloatField(default=0)
    skills_score = models.FloatField(default=0)
    edu_score = models.FloatField(default=0)
    exp_score = models.FloatField(default=0)
    summarize = models.TextField(default="")
    suggestions = models.TextField(default="")
    grammarcheck = models.TextField(default="")
    missingskills = models.TextField(default='[]')  # Use a TextField to store the missing skills as a JSON string
    googleimages = models.TextField(default='[]')
    upgraded_pdf = models.FileField(default="", upload_to='upgraded_pdfs/')

    def set_missingskills(self, data):
        self.missingskills = json.dumps(data)  # Serialize the list/dict to a JSON string

    def get_missingskills(self):
        return json.loads(self.missingskills)  # Deserialize the JSON string back into Python list/dict
    
    def set_googleimages(self, urls_list):
        self.googleimages = json.dumps(urls_list)

    def get_googleimages(self):
        try:
            return json.loads(self.googleimages)  # Correct attribute name
        except json.JSONDecodeError:
            return []  # Return an empty list if there's a decoding error
    
    def set_upgraded_pdf(self, file):
        self.upgraded_pdf = file

    def get_upgraded_pdf(self):
        return self.upgraded_pdf

    def __str__(self):
        return f"Analysis Result for {self.uploaded_document.position}"


class Video(models.Model):
    title = models.CharField(max_length=100)
    video = models.FileField(upload_to='videos/')
    description = models.TextField()
    
@receiver(post_delete, sender=UploadedDocument)
def delete_associated_file(sender, instance, **kwargs):
    """Deletes file from filesystem when corresponding `UploadedDocument` object is deleted."""
    instance.document.delete(save=False)