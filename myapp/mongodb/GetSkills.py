import requests
import json
import os
from django.conf import settings

def get_data_from_collection(collection_name):
    url = settings.MONGODB_ENDPOINT
    api_key = settings.MONGODB_API_KEY

    payload = json.dumps({
        "collection": collection_name,
        "database": "Skills",
        "dataSource": "howgoodismycv-db",
        "filter": {}
    })
    
    headers = {
      'Content-Type': 'application/json',
      'Access-Control-Request-Headers': '*',
      'api-key': api_key,
    }
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        data = response.json()
        # Assuming the data is in 'documents' part of the response. Adjust based on actual response structure
        return data.get('documents', [])
    else:
        print(f"Error fetching data from {collection_name}: {response.status_code}")
        return []

def get_missing_skills(resume, position):
    skills_data = get_data_from_collection(position)
    missing_skills = []
    resume = resume.lower()  # Case-folding resume for case-insensitive comparison
    
    # Iterate through each skill in the fetched data
    for skill_doc in skills_data:
        skill = skill_doc.get('Skill', '').lower()  # Case-folding skill for case-insensitive comparison
        # Check if the skill is not in the resume
        if skill and skill not in resume:
            # Append the skill and its count as a dictionary
            missing_skills.append({'Skill': skill_doc['Skill'], 'Rank': skill_doc['Rank'], 'Count': skill_doc['Count']})

    # Sort the missing skills based on 'Rank'
    sorted_missing_skills = sorted(missing_skills, key=lambda x: x['Rank'])

    # Return the top 20 missing skills
    return sorted_missing_skills[:20]
