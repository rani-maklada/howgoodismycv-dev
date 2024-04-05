import requests
from django.conf import settings
def get_similar_resume_image_url(search_query):
    try:
        
        # Custom Search Engine ID and API Key
        api_key = settings.GOOGLE_API_KEY
        cse_id = settings.GOOGLE_CSE_ID
        # Construct the API URL
        url = f"https://www.googleapis.com/customsearch/v1?q={search_query}&cx={cse_id}&searchType=image&key={api_key}"

        # Make the API request
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code

        # Parsing the response
        results = response.json()
        image_urls = []
        if "items" in results and len(results["items"]) > 0:
            # Iterate over the first 10 items (or fewer if there are less than 10)
            for item in results["items"]:
                # Extract the "link" from each item and add it to the image_urls list
                image_url = item.get("link")
                if image_url:  # Make sure the "link" key exists and has a value
                    image_urls.append(image_url)
            return image_urls
        else:
            return "No results found"

    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return None