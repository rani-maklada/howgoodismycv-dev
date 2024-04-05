from django.contrib import admin
from .models import UploadedDocument, AnalysisResult
from django.utils.html import format_html
import json

@admin.register(UploadedDocument)
class UploadedDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'document')
    search_fields = ('user__username', 'position')


@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('uploaded_document', 'overall_score', 'skills_score', 'edu_score', 'exp_score', 'summarize', 'suggestions', 'grammarcheck', 'upgraded_pdf', 'display_missingskills', 'display_googleimages')
    search_fields = ('uploaded_document__document_name', 'summarize', 'suggestions', 'grammarcheck') 
    list_filter = ('uploaded_document__user', 'overall_score')  # Assuming `uploaded_document` has a `user` field for filtering
    ordering = ('-overall_score',)  # Order by overall_score descending by default

    def display_missingskills(self, obj):
        """Creates a simplified representation of the missing skills for the admin list view."""
        return self._display_json_field(obj.missingskills)
    display_missingskills.short_description = "Missing Skills"

    def display_googleimages(self, obj):
        """Displays google images links as a list."""
        return self._display_json_field(obj.googleimages, is_url=True)
    display_googleimages.short_description = "Google Images"

    def get_queryset(self, request):
        # Customize the queryset if necessary, for example, to optimize queries
        qs = super().get_queryset(request)
        # You can prefetch related objects to reduce the number of database queries
        qs = qs.select_related('uploaded_document')
        return qs

    def _display_json_field(self, json_field, is_url=False):
        """Utility function to display JSON fields."""
        if json_field:
            try:
                data = json.loads(json_field)
                if is_url:
                    # Format URLs as clickable links
                    return format_html('<br>'.join([f'<a href="{url}" target="_blank">{url}</a>' for url in data]))
                else:
                    # Assuming data is a list of dictionaries, format appropriately
                    formatted_data = []
                    for item in data:
                        if isinstance(item, dict):
                            # Here you can adjust how you want to display each dictionary
                            # For example, if each skill has 'name' and 'level' keys:
                            # formatted_item = f"{item.get('name', 'Unknown')} (Level: {item.get('level', 'N/A')})"
                            # Adjust the above line to match your dictionary structure
                            formatted_item = ', '.join([f"{key}: {value}" for key, value in item.items()])
                            formatted_data.append(formatted_item)
                        else:
                            # If it's not a dictionary, just convert to string
                            formatted_data.append(str(item))
                    return format_html('<br>'.join(formatted_data))
            except json.JSONDecodeError:
                return "Invalid JSON"
        return "N/A"
