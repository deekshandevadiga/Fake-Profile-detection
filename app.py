import os
import re
import streamlit as st
from docx import Document
from PyPDF2 import PdfReader
from fuzzywuzzy import fuzz
import requests
from PIL import Image
from pytesseract import image_to_string
from pdf2image import convert_from_path
from pytesseract import pytesseract

# Configure Tesseract OCR Path
pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Proxycurl API configuration
PROXYCURL_API_KEY = "H-MXFXrrlnP7ZKbrbOTnOw"  # Replace with your API key
PROXYCURL_ENDPOINT = "https://nubela.co/proxycurl/api/v2/linkedin"

# Helper Functions
def preprocess_text(text):
    text = ''.join(c for c in text if ord(c) < 128)  # Remove non-ASCII characters
    text = text.replace('\n', ' ').replace('\r', ' ')  # Replace line breaks with spaces
    return re.sub(r'\s+', ' ', text).strip()  # Remove extra spaces

def process_resume_and_linkedin(filepath):
    resume_data = extract_resume_data(filepath)

    if not resume_data.get("linkedin_url"):
        st.error(f"No LinkedIn URL found in resume: {filepath}")
        return 0

    linkedin_data = fetch_linkedin_data(resume_data.get("linkedin_url"))

    if linkedin_data:
        score = calculate_similarity(resume_data, linkedin_data)
    else:
        st.error(f"Could not retrieve LinkedIn data for URL: {resume_data.get('linkedin_url')}")
        score = 0

    return score

def extract_resume_data(filepath):
    ext = filepath.split('.')[-1].lower()
    if ext == 'pdf':
        text = extract_text_from_pdf(filepath)
    elif ext == 'docx':
        text = extract_text_from_word(filepath)
    else:
        text = ""

    linkedin_url = extract_linkedin_url(text)
    email = extract_email(text)
    education = extract_education(text)
    experience = extract_experience(text)

    return {
        "linkedin_url": linkedin_url,
        "email": email,
        "education": education,
        "experience": experience,
    }

def extract_text_from_pdf(filepath):
    try:
        reader = PdfReader(filepath)
        text = ' '.join([page.extract_text() for page in reader.pages if page.extract_text()])
        if not text.strip():
            st.warning("PDF text extraction failed. Attempting OCR...")
            images = convert_from_path(filepath, poppler_path=r"C:\path\to\poppler\bin")  # Update poppler path
            text = ' '.join([image_to_string(image) for image in images])
        return text
    except Exception as e:
        st.error(f"Error reading PDF ({filepath}): {e}")
        return ""

def extract_text_from_word(filepath):
    try:
        doc = Document(filepath)
        text = ' '.join([para.text for para in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error reading Word document ({filepath}): {e}")
        return ""

def extract_linkedin_url(text):
    try:
        normalized_text = preprocess_text(text)
        match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+', normalized_text)
        if match:
            linkedin_url = match.group().strip()
            if not linkedin_url.startswith("http"):
                linkedin_url = "https://" + linkedin_url
            st.success(f"LinkedIn URL Found: {linkedin_url}")
            return linkedin_url
        else:
            st.warning("No LinkedIn URL found.")
            return None
    except Exception as e:
        st.error(f"Error extracting LinkedIn URL: {e}")
        return None

def extract_email(text):
    match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
    return match.group() if match else None

def extract_education(text):
    return re.findall(r'(B\.?Tech|M\.?Tech|B\.?E|M\.?E|Bachelor|Master|Ph\.?D)', text, re.I)

def extract_experience(text):
    return re.findall(r'(Intern|Experience|Project|Developer)', text, re.I)

def fetch_linkedin_data(linkedin_url):
    try:
        headers = {"Authorization": f"Bearer {PROXYCURL_API_KEY}"}
        params = {"linkedin_profile_url": linkedin_url, "extra": "include"}
        response = requests.get(PROXYCURL_ENDPOINT, headers=headers, params=params)
        response.raise_for_status()
        linkedin_data = response.json()
        return {
            "education": linkedin_data.get("education", []),
            "experience": linkedin_data.get("experiences", []),
        }
    except Exception as e:
        st.error(f"Error fetching LinkedIn data ({linkedin_url}): {e}")
        return None

def calculate_similarity(resume_data, linkedin_data):
    resume_education = ' '.join(map(str, resume_data.get("education", []))).lower()
    linkedin_education = ' '.join(map(str, [edu.get("field_of_study", "") for edu in linkedin_data.get("education", [])])).lower()

    resume_experience = ' '.join(map(str, resume_data.get("experience", []))).lower()
    linkedin_experience = ' '.join(map(str, [exp.get("title", "") for exp in linkedin_data.get("experience", [])])).lower()

    education_score = fuzz.ratio(resume_education, linkedin_education)
    experience_score = fuzz.ratio(resume_experience, linkedin_experience)

    st.write(f"Education Score: {education_score}")
    st.write(f"Experience Score: {experience_score}")

    return (education_score + experience_score) // 2

# Main Streamlit Code
st.title("Fake Profile Detection")
st.write("Upload resumes in PDF or DOCX format, and the app will analyze them.")

uploaded_files = st.file_uploader("Upload Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True)
results = {}

if uploaded_files:
    for file in uploaded_files:
        # Save uploaded file to a temporary directory
        file_path = os.path.join("uploads", file.name)
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(file.read())

        # Process the uploaded file
        score = process_resume_and_linkedin(file_path)
        results[file.name] = score

        # Display results
        if score < 20:
            os.remove(file_path)  # Remove low-score files
            st.warning(f"Low-score file deleted: {file.name}")

    st.write("Results:")
    st.json(results)
