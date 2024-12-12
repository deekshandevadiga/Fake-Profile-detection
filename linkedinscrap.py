import requests

# Proxycurl API configuration
API_URL = "https://nubela.co/proxycurl/api/v2/linkedin"
API_KEY = "WLmbm4NRxD3HJ-G3JgB00g"  # Replace with your actual Proxycurl API key
PROFILE_URL = "https://www.linkedin.com/in/krishnarajav"  # Replace with the LinkedIn profile URL

# Function to fetch data using Proxycurl API
def fetch_linkedin_data(api_key, profile_url):
    headers = {"Authorization": f"Bearer {api_key}"}
    params = {"url": profile_url, "use_cache": "if-present"}
    response = requests.get(API_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}, {response.text}")
        return None

# Function to extract projects, certificates, and experience
def extract_details(data):
    # Extract projects
    projects = []
    if "accomplishment_projects" in data:
        for project in data["accomplishment_projects"]:
            projects.append({
                "title": project.get("title", "Not Provided"),
                "description": project.get("description", "Not Provided"),
                "start_date": project.get("starts_at", "Not Provided"),
                "url": project.get("url", "Not Provided")
            })
    
    # Extract certificates
    certificates = []
    if "certifications" in data:
        for cert in data["certifications"]:
            certificates.append({
                "name": cert.get("name", "Not Provided"),
                "authority": cert.get("authority", "Not Provided"),
                "start_date": cert.get("starts_at", "Not Provided"),
                "url": cert.get("url", "Not Provided")
            })
    
    # Extract experience
    experience = []
    if "experiences" in data:
        for exp in data["experiences"]:
            experience.append({
                "title": exp.get("title", "Not Provided"),
                "company": exp.get("company", "Not Provided"),
                "description": exp.get("description", "Not Provided"),
                "start_date": exp.get("starts_at", "Not Provided"),
                "end_date": exp.get("ends_at", "Not Provided"),
                "location": exp.get("location", "Not Provided")
            })
    
    return {
        "projects": projects,
        "certificates": certificates,
        "experience": experience
    }

# Main execution
if __name__ == "__main__":
    print("Fetching LinkedIn Data...")
    linkedin_data = fetch_linkedin_data(API_KEY, PROFILE_URL)

    if linkedin_data:
        print("\nExtracting Details...")
        extracted_details = extract_details(linkedin_data)
        
        # Print projects
        print("\nProjects:")
        for project in extracted_details["projects"]:
            print(f"Title: {project['title']}")
            print(f"Description: {project['description']}")
            print(f"Start Date: {project['start_date']}")
            print(f"URL: {project['url']}\n")
        
        # Print certificates
        print("\nCertificates:")
        for cert in extracted_details["certificates"]:
            print(f"Name: {cert['name']}")
            print(f"Authority: {cert['authority']}")
            print(f"Start Date: {cert['start_date']}")
            print(f"URL: {cert['url']}\n")
        
        # Print experience
        print("\nExperience:")
        for exp in extracted_details["experience"]:
            print(f"Title: {exp['title']}")
            print(f"Company: {exp['company']}")
            print(f"Description: {exp['description']}")
            print(f"Start Date: {exp['start_date']}")
            print(f"End Date: {exp['end_date']}")
            print(f"Location: {exp['location']}\n")
    else:
        print("Failed to fetch LinkedIn data.")
