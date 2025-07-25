import streamlit as st
import requests
from urllib.parse import quote_plus
from duckduckgo_search import DDGS
import urllib.parse
import json
import http.client
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from newsapi import NewsApiClient
from datetime import datetime, timedelta
import urllib.request
import os
import base64
import logging
from datetime import datetime, timedelta
from pydantic.v1 import SecretStr


# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Streamlit page configuration
st.set_page_config(
    page_title="CareerBoost",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Load API keys
try:
    serp_api_key = "ee95ed0a8446fceec3ecd384ea0a933510f9acdd8ac5a3c4603d010ec55abdc8"
    rapidapi_key = "a378123bcamshc85fa897953dd13p1553f3jsn114ef9689f7a"
    google_api_key = os.getenv("AIzaSyCqLfDYMipOqYBtuZxOSR9cd9SvfSs5I40")
    gnews_api_key = "bee57c5681438c2f6f61e325c995923f"
    newsapi_key = "83c98424915f4ba6bed7e23a53edfb31" 
except KeyError as e:
    st.error(f"Missing API key: {e}. Please configure it in secrets.toml.")
    st.stop()

# Custom CSS
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 5px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stTextInput>div>input, .stTextArea textarea {
        border-radius: 5px;
        padding: 10px;
    }
    .stSelectbox>div>div {
        border-radius: 5px;
    }
    .header {
        text-align: center;
        margin-bottom: 20px;
    }
    .caption {
        text-align: center;
        color: #666;
        font-style: italic;
    }
    .logo {
        display: block;
        margin: 0 auto;
        width: 150px;
    }

    .card {
        background-color: #2d3748;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        color: #ffffff !important;
    }
    .card h4 {
        color: #ffffff !important;
        margin-bottom: 10px;
    }
    .card p {
        color: #e2e8f0 !important;
        margin: 5px 0;
    }
    .card a {
        color: #63b3ed !important;
        text-decoration: none;
    }
    .card a:hover {
        color: #90cdf4 !important;
    }

    [data-testid="stSidebar"],
    .st-emotion-cache-6qob1r {
        background-color: #1a1a1a !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] .stCaption {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div > select {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stRadio > div > label > div {
        background-color: #2a2a2a !important;
        border: 1px solid #555555 !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background-color: #333333 !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
        border-radius: 5px !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #444444 !important;
        border-color: #777777 !important;
    }
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
        border: 1px solid #555555 !important;
        border-radius: 5px !important;
    }
    [data-testid="stSidebar"] .stSlider > div > div {
        background-color: #555555 !important;
    }
    [data-testid="stSidebar"] .stSlider > div > div > div {
        background-color: #ffffff !important;
    }
    [data-testid="stSidebar"] .st-emotion-cache-1vzeuhh path {
        fill: #ffffff !important;
    }
    [data-testid="stSidebar"] .stCaption {
        color: #a0aec0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("CareerBoost")
st.sidebar.markdown("""
**Your AI-powered career assistant**  
*Smart tools for job search, CV optimization, and interview success.*
""")
page = st.sidebar.selectbox(
    "Choose a section",
    ["Home", "Job Finding", "CV Maker", "Interview Preparation", "Career Insights", "About"]
)
st.sidebar.markdown("""
### ✨ Key Features:
- **AI-Powered Job Matching**  
- **ATS-Friendly CV Builder**  
- **Personalized Interview Prep**  
- **Real-Time Career Insights**  
""")

st.sidebar.caption("v2.1.0 | Last updated: April 2024")




# Home page
if page == "Home":
    st.markdown("""
    <style>
    .header {
        background: linear-gradient(135deg, #2c3e50, #4a6491);
        padding: 20px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    .feature-card {
        background-color: #2d3748;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        border-left: 4px solid #4a6491;
        transition: transform 0.3s;
        color: #f7fafc;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        background-color: #3c4a5e;
    }
    .stats-container {
        display: flex;
        justify-content: space-around;
        text-align: center;
        margin: 30px 0;
    }
    .stat-item {
        background: #2d3748;
        padding: 15px;
        border-radius: 8px;
        width: 23%;
        color: #f7fafc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .testimonial {
        font-style: italic;
        background: #2d3748;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #4a6491;
        margin: 15px 0;
        color: #f7fafc;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    body {
        color: #f7fafc;
        background-color: #1a202c;
    }
    .stApp {
        background-color: #1a202c;
    }
    .caption {
        color: #a0aec0;
        font-size: 1.1em;
        margin-bottom: 20px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #f7fafc !important;
    }
    p {
        color: #e2e8f0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="header"><h1>🚀 CareerBoost</h1></div>', unsafe_allow_html=True)
    st.markdown('<div class="caption">Your one-stop platform for job hunting, CV creation, and career insights</div>',
                unsafe_allow_html=True)

    logo_path = "logo.ico"
    if os.path.exists(logo_path):
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with open(logo_path, "rb") as f:
                logo_bytes = f.read()
                st.markdown(
                    f'<div style="text-align: center;"><img src="data:image/x-icon;base64,{base64.b64encode(logo_bytes).decode()}" width="150"></div>',
                    unsafe_allow_html=True
                )
    else:
        st.warning("Logo file (logo.png) not found. Please upload it to the project directory.")

    st.markdown("""
    ## Welcome to Your Career Transformation

    CareerBoost is your **AI-powered career companion** designed to help you navigate every step of your professional 
    journey with confidence. Whether you're looking for your dream job, optimizing your resume, or preparing for 
    interviews, we've got you covered with smart, personalized tools.
    
    **About the Creator**: This app was built by Yuvraj Rajput, a passionate developer dedicated to helping professionals succeed. Check out my portfolio at [My Portfolio](https://your-portfolio-link.com) to learn more about my work!
    """)

    
    st.markdown("""
    <div class="stats-container">
        <div class="stat-item">
            <h3>250K+</h3>
            <p>Professionals Helped</p>
        </div>
        <div class="stat-item">
            <h3>3x</h3>
            <p>Faster Job Placement</p>
        </div>
        <div class="stat-item">
            <h3>40%</h3>
            <p>More Interviews</p>
        </div>
        <div class="stat-item">
            <h3>95%</h3>
            <p>User Satisfaction</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("## ✨ How CareerBoost Helps You Succeed")

    features = [
        {
            "title": "Smart Job Matching",
            "desc": "Our AI scans thousands of listings to find the perfect matches for your skills and aspirations.",
            "icon": "🔍"
        },
        {
            "title": "ATS-Optimized CV Builder",
            "desc": "Create resumes that beat applicant tracking systems with our intelligent templates.",
            "icon": "📄"
        },
        {
            "title": "AI Interview Coach",
            "desc": "Practice with realistic mock interviews and get instant feedback on your responses.",
            "icon": "💬"
        },
        {
            "title": "Career Navigator",
            "desc": "Get personalized career path recommendations based on your profile and goals.",
            "icon": "🧭"
        }
    ]

    for feature in features:
        st.markdown(f"""
        <div class="feature-card">
            <h3>{feature['icon']} {feature['title']}</h3>
            <p>{feature['desc']}</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    ## Ready to Boost Your Career?
    Get started today by selecting one of the options from the sidebar:
    """)

# Job Finding Section
elif page == "Job Finding":
    st.title("🔍 Job Finding")
    st.markdown("Search for job opportunities tailored to your preferences.")


    def build_google_search_link(title, company):
        query = f"{title} {company} apply job"
        return f"https://www.google.com/search?q={quote_plus(query)}"


    def search_serp(query, location, experience='fresher', job_category='full-time', num_results=10):
        fresher_keywords = ["fresher", "entry level", "junior", "graduate"]
        # Add fresher keywords to query if experience is fresher
        if experience.lower() == "fresher":
            query = f"{query} fresher OR entry level OR junior OR graduate"
        params = {
            "engine": "google_jobs",
            "q": f"{query} {job_category}",
            "location": location,
            "experience": experience,
            "api_key": serp_api_key
        }
        try:
            response = requests.get("https://serpapi.com/search", params=params)
            response.raise_for_status()
            data = response.json()
            jobs = data.get("jobs_results", [])[:num_results]
            results = []
            for job in jobs:
                title = job.get('title', 'N/A')
                description = job.get('description', '')
                # Filter for fresher jobs
                if experience.lower() == "fresher":
                    if not any(k in title.lower() or k in description.lower() for k in fresher_keywords):
                        continue
                result = {
                    "title": title,
                    "company": job.get('company_name', 'N/A'),
                    "location": job.get('location', 'N/A'),
                    "posted": job.get('detected_extensions', {}).get('posted_at', 'N/A'),
                    "description": description[:200] + "...",
                    "apply_link": job.get("job_google_link") or build_google_search_link(job.get('title', ''), job.get('company_name', 'Unknown')),
                    "source": "SerpAPI",
                    "category": job_category
                }
                results.append(result)
            return results
        except requests.exceptions.RequestException as e:
            return [{"error": f"SerpAPI error: {str(e)}"}]


    def duckduckgo_job_search(query: str, job_category: str) -> list:
        fresher_keywords = ["fresher", "entry level", "junior", "graduate"]
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(f"{query} {job_category}", max_results=20)]
            formatted_results = []
            for result in results:
                title = result.get('title', 'N/A')
                description = result.get('body', 'No description available')
                # Filter for fresher jobs
                if any(k in title.lower() or k in description.lower() for k in fresher_keywords):
                    formatted_results.append({
                        "title": title,
                        "company": 'N/A',
                        "location": 'N/A',
                        "apply_link": result.get('href', '#'),
                        "description": description[:200] + "...",
                        "posted": None,
                        "source": "DuckDuckGo",
                        "category": job_category
                    })
            return formatted_results
        except Exception as e:
            return [{"error": f"DuckDuckGo error: {str(e)}"}]


    def job_search(field, location, experience, job_category='full-time'):
        # Add fresher keywords if experience is fresher
        fresher_keywords = "fresher OR entry level OR junior OR graduate"
        if experience.lower() == "fresher":
            query = f"find {field} {fresher_keywords} job in {location}"
        else:
            query = f"find {field} job in {location} for {experience}"
        return duckduckgo_job_search(query, job_category)


    def rapid_job_searcher(job: str, location: str, pages: int = 1, country: str = "us") -> list:
        fresher_keywords = ["fresher", "entry level", "junior", "graduate"]
        conn = http.client.HTTPSConnection("jsearch.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': str(rapidapi_key),
            'x-rapidapi-host': "jsearch.p.rapidapi.com"
        }
        try:
            query = urllib.parse.quote(f"{job} jobs in {location} fresher OR entry level OR junior OR graduate")
            conn.request("GET", f"/search?query={query}&page=1&num_pages={pages}&country={country}&date_posted=all",
                         headers=headers)
            res = conn.getresponse()
            data = res.read()
            results = []
            try:
                data_json = json.loads(data.decode("utf-8"))
            except json.JSONDecodeError as e:
                return [{"error": f"JSON parse error: {str(e)}"}]
            for job in data_json.get('data', []):
                if not isinstance(job, dict):
                    continue
                title = job.get('job_title', 'N/A')
                description = job.get('job_description', '')
                # Filter for fresher jobs
                if not any(k in title.lower() or k in description.lower() for k in fresher_keywords):
                    continue
                city = job.get('job_city', '')
                state = job.get('job_state', '')
                location_parts = [part for part in [city, state] if part]
                results.append({
                    "title": title,
                    "company": job.get('employer_name', 'N/A'),
                    "location": ", ".join(location_parts) if location_parts else "N/A",
                    "posted": job.get('job_posted_at_datetime_utc', 'N/A'),
                    "description": description[:200] + "...",
                    "apply_link": job.get('job_apply_link', '#'),
                    "source": "RapidAPI",
                    "category": None
                })
            return results if results else [{"error": "No fresher jobs found."}]
        except Exception as e:
            return [{"error": f"RapidAPI request failed: {str(e)}"}]


    job_categories = ['full-time', 'part-time', 'intern', 'contract', 'temporary']
    experience_levels = ['fresher', 'experienced', 'senior']

    with st.form("job_search_form"):
        col1, col2 = st.columns(2)
        with col1:
            job = st.text_input("Job Title (e.g., Software Engineer)", "Software Engineer")
            location = st.text_input("Location (e.g., Kochi)", "Kochi")
        with col2:
            experience = st.selectbox("Experience Level", experience_levels)
            category = st.selectbox("Job Category", job_categories)
        submit = st.form_submit_button("Search Jobs")

    if submit:
        with st.spinner("Searching for jobs..."):
            rapid_results = rapid_job_searcher(job, location)
            safe_experience = experience if experience is not None else ""
            safe_category = category if category is not None else ""
            ddg_results = job_search(job, location, safe_experience, safe_category)
            serp_results = search_serp(job, location, safe_experience, safe_category)
            all_results = {'RapidAPI': rapid_results,'DuckDuckGo': ddg_results,'SerpAPI': serp_results}

            for source, results in all_results.items():
                st.subheader(f"Jobs Tailored for You")
                if results and not any("error" in r for r in results):
                    for result in results:
                        with st.container():
                            st.markdown(f"""
                            <div class="card">
                                <h4>{result.get('title', 'N/A')}</h4>
                                <p><strong>Company:</strong> {result.get('company', 'N/A')}</p>
                                <p><strong>Location:</strong> {result.get('location', 'N/A')}</p>
                                <p><strong>Posted:</strong> {result.get('posted', 'N/A')}</p>
                                <p><strong>Description:</strong> {result.get('description', 'No description available')}</p>
                                <a href="{result.get('apply_link', '#')}" target="_blank">Apply Now</a>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    error_msg = results[0].get("error", "No results found.") if results else "No results found."
                    st.error(error_msg)


# CV Maker Section
if page == "CV Maker":  # Assuming 'page' is defined elsewhere; use 'if' instead of 'elif' for standalone testing
    st.title("📝 CV Maker")
    st.markdown("Create a professional, ATS-friendly CV tailored to your job role.")

    # Initialize LLM
    # AIzaSyCqLfDYMipOqYBtuZxOSR9cd9SvfSs5I40
    from pydantic.v1 import SecretStr

    cv_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        api_key=SecretStr("AIzaSyCqLfDYMipOqYBtuZxOSR9cd9SvfSs5I40"),
        temperature=0.1,
        max_output_tokens=2048
    )

    # CV Prompt Template 
    cv_prompt = PromptTemplate(
        input_variables=["job_field", "experience_level", "years_experience", "key_skills", "education"],
        template="""
        You are an expert CV writer with deep knowledge of ATS-friendly formatting and industry-specific requirements. 
        Create a professional, concise, and tailored CV for a {job_field} position based on the following user details:

        - Experience: {experience_level} ({years_experience} years)
        - Skills: {key_skills}
        - Education: {education}

        Structure:
        === Contact ===
        - Name: John Doe  
        - Email: yuvrajrajput@gmail.com  
        - Phone: +91-9624870800 
        - LinkedIn: https://github.com/yuvrajrajput
        - Portfolio/GitHub: https://huggingface.co/yuvrajrajput0002

        == Professional Summary ==  
        - 3-4 sentences highlighting expertise in {job_field}, key achievements, and career goals.  
        - Use action verbs (e.g., "Led," "Optimized," "Developed") and quantifiable results.  

        == Projects == 
        - Project Name | [GitHub/Live Link]  
          • Technologies used: {key_skills}  
          • Key outcome: [Measurable result]  

        === Skills ===
        - 6-10 relevant skills including {key_skills}

        === Experience ===
        [2-3 roles based on {experience_level}]
        - Title @ Company (Years)
          • Metric-driven achievements
          • Action-oriented responsibilities

        === Education ===
        {education}  
        - Degree Name, University Name | Year  
          • Relevant coursework: [Course 1], [Course 2]  
          • Thesis/Project: [If applicable]

        === Certifications ===
        - [Relevant certifications]

        Guidelines:
        1. Use action verbs and metrics
        2. Match seniority to {experience_level}
        3. ATS-optimized plain text format
        4. Field-specific keywords
        """
    )

    def generate_cv(job_field: str, experience_level: str, years_experience: str, key_skills: str,
                    education: str) -> str:
        try:
            job_field = job_field.strip()
            experience_level = experience_level.strip()
            years_experience = years_experience.strip()
            key_skills = key_skills.strip()
            education = education.strip()

            print(f"Inputs: job_field={job_field}, experience_level={experience_level}, "
                  f"years_experience={years_experience}, key_skills={key_skills}, education={education}")

            prompt = cv_prompt.format(
                job_field=job_field,
                experience_level=experience_level,
                years_experience=years_experience,
                key_skills=key_skills,
                education=education,
            )
            response = cv_llm.invoke(prompt)
            content = response.content
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                return "\n".join(str(item) for item in content)
            elif isinstance(content, dict):
                return json.dumps(content, indent=2)
            else:
                return str(content)
        except Exception as e:
            print(f"Error details: {str(e)}")  
            return f"Error generating CV: {str(e)}"

    # def generate_cv_pdf(cv_content: str) -> BytesIO:
    #     try:
    #         # Initialize BytesIO buffer
    #         buffer = BytesIO()
    
    #         # Create a SimpleDocTemplate for the PDF
    #         doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    #         # Define styles
    #         styles = getSampleStyleSheet()
    #         heading_style = ParagraphStyle(
    #             name='Heading',
    #             fontSize=14,
    #             leading=16,
    #             spaceAfter=12,
    #             fontName='Helvetica-Bold'
    #         )
    #         body_style = ParagraphStyle(
    #             name='Body',
    #             fontSize=11,
    #             leading=14,
    #             spaceAfter=8,
    #             fontName='Helvetica'
    #         )
    #         bullet_style = ParagraphStyle(
    #             name='Bullet',
    #             fontSize=11,
    #             leading=14,
    #             leftIndent=20,
    #             bulletIndent=10,
    #             spaceAfter=8,
    #             fontName='Helvetica'
    #         )
    
    #         # Initialize flowables list
    #         flowables = []
    
    #         # Validate cv_content
    #         if not cv_content or not isinstance(cv_content, str):
    #             logger.error("Invalid or empty cv_content provided")
    #             raise ValueError("CV content is empty or invalid")
    
    #         # Split content into sections
    #         sections = cv_content.split('===')
    #         logger.debug(f"Number of sections: {len(sections)}")
    #         logger.debug(f"Sections: {sections}")
    
    #         # Process sections
    #         for i in range(0, len(sections), 2):
    #             if i + 1 >= len(sections):
    #                 logger.warning("Incomplete section pair detected, stopping processing")
    #                 break
    
    #             title = sections[i].strip()
    #             content = sections[i + 1].strip().split('\n')
    #             logger.debug(f"Processing section: {title}")
    
    #             # Add section title
    #             flowables.append(Paragraph(title, heading_style))
    #             flowables.append(Spacer(1, 6))
    
    #             # Process section content
    #             if title in ["Skills", "Certifications"]:
    #                 # Handle bullet points for Skills and Certifications
    #                 bullet_items = []
    #                 for line in content:
    #                     if line.strip():
    #                         # Sanitize text to avoid encoding issues
    #                         sanitized_line = line.strip().encode('ascii', 'ignore').decode('ascii')
    #                         bullet_items.append(ListItem(Paragraph(sanitized_line, bullet_style)))
    #                 if bullet_items:
    #                     flowables.append(ListFlowable(bullet_items, bulletType='bullet', start='circle'))
    #                 else:
    #                     logger.warning(f"No valid bullet items for section: {title}")
    #             else:
    #                 # Handle regular paragraphs
    #                 for line in content:
    #                     if line.strip():
    #                         # Sanitize text to avoid encoding issues
    #                         sanitized_line = line.strip().encode('ascii', 'ignore').decode('ascii')
    #                         flowables.append(Paragraph(sanitized_line, body_style))
    
    #             flowables.append(Spacer(1, 12))
    
    #         # Build the PDF
    #         logger.debug("Building PDF with flowables")
    #         doc.build(flowables)
    
    #         # Ensure buffer is ready to be read
    #         buffer.seek(0)
    #         logger.debug("PDF generation completed successfully")
    
    #         return buffer

    #     except Exception as e:
    #         logger.error(f"Error generating PDF: {str(e)}")
    #         raise Exception(f"Failed to generate PDF: {str(e)}")

    with st.form("cv_form"):
        col1, col2 = st.columns(2)
        with col1:
            job_field = st.text_input("Job Field (e.g., Software Engineer)", "Software Engineer")
            experience_level = st.selectbox("Experience Level", ["Fresher", "Experienced", "Senior"])
            years_experience = st.text_input("Years of Experience (e.g., 2)", "2")
        with col2:
            key_skills = st.text_area("Key Skills (comma-separated, e.g., Python, SQL)", "Python, SQL, JavaScript")
            education = st.text_area("Education (e.g., B.Tech in CS, XYZ University, 2020)",
                                    "B.Tech in CS, XYZ University, 2020")
        submit = st.form_submit_button("Generate CV")

        if submit and not education.strip():
            st.error("Education field cannot be empty.")
            st.stop()

    if submit:
        with st.spinner("Generating CV..."):
            safe_experience_level = experience_level if experience_level is not None else ""
            cv_content = generate_cv(job_field, safe_experience_level, years_experience, key_skills, education)
            st.session_state['last_cv'] = cv_content
            if not cv_content.startswith("Error"):
                st.success("CV generated successfully!")
                st.markdown("### Generated CV")
                st.text_area("CV Content", cv_content, height=400)
                st.download_button(
                    label="Download CV (Text)",
                    data=cv_content,
                    file_name="John_Doe_CV.txt",
                    mime="text/plain"
                )
                # pdf_buffer = generate_cv_pdf(cv_content)
                # st.download_button(
                #     label="Download CV (PDF)",
                #     data=pdf_buffer,
                #     file_name="John_Doe_CV.pdf",
                #     mime="application/pdf"
                # )
            else:
                st.error(cv_content)

# Interview Preparation Section
elif page == "Interview Preparation":
    st.title("🎤 Interview Preparation")
    st.markdown("Prepare for your next interview with tailored questions and answers.")

    # Use Streamlit secrets or environment variable for API key to avoid hardcoding
    import os

    api_key = st.secrets.get("GOOGLE_API_KEY", None) or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        st.error("Google API key not found. Please set it in Streamlit secrets or as an environment variable.")
        st.stop()

    # Ensure api_key is passed as SecretStr if required by ChatGoogleGenerativeAI
    from pydantic.v1 import SecretStr

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=SecretStr(api_key) if api_key else None)


    def duckduckgo_search(query: str) -> str:
        try:
            with DDGS() as ddgs:
                results = [r for r in ddgs.text(query, max_results=5)]
            return json.dumps(results, indent=2)
        except Exception as e:
            return f"Error in DuckDuckGo search: {str(e)}"


    def interview_preparer(job_field: str) -> str:
        try:
            if not job_field or not isinstance(job_field, str):
                return "Error: Invalid job field provided."
            search_queries = [
                f"{job_field} interview questions 2022-2025",
                f"site:reddit.com {job_field} interview questions",
                f"site:quora.com {job_field} interview questions"
            ]
            search_results = []
            for query in search_queries:
                try:
                    result = duckduckgo_search(query)
                    if not result.startswith("Error"):
                        search_results.append(json.loads(result))
                except Exception as e:
                    search_results.append({"source": query, "error": str(e)})
            combined_results = json.dumps(search_results, indent=2)
            interview_prompt = PromptTemplate(
                input_variables=["job_field", "search_results"],
                template="""
                You are an interview preparation expert. Generate exactly 15 interview questions with detailed, professional answers for {job_field}. Do NOT provide links or references to external resources; focus on self-contained questions and answers.
                Requirements:
                - Include 6 technical questions, 5 behavioral questions, and 4 situational questions.
                - Incorporate trends and frequently asked questions from 2022-2025.
                - Use the search results for context to inform answers, but do not include raw search data or URLs in the output: {search_results}.
                - Format as plain text with question numbers, type (Technical/Behavioral/Situational), questions, and answers.
                Example:
                1. Technical: [Question]
                Answer: [Detailed answer]
                """
            )
            response = llm.invoke(interview_prompt.format(job_field=job_field, search_results=combined_results))
            content = response.content
            if isinstance(content, str):
                return content
            elif isinstance(content, list):
                return "\n".join(str(item) for item in content)
            elif isinstance(content, dict):
                return json.dumps(content, indent=2)
            else:
                return str(content)
        except Exception as e:
            return f"Error generating interview questions: {str(e)}"


    with st.form("interview_form"):
        job_field = st.text_input("Job Field (e.g., Software Engineer)", "Software Engineer")
        submit = st.form_submit_button("Generate Questions")

    if submit:
        with st.spinner("Generating interview questions..."):
            questions = interview_preparer(job_field)
            st.session_state['last_questions'] = questions
            if not questions.startswith("Error"):
                st.success("Interview questions generated successfully!")
                st.markdown("### Interview Questions")
                st.text_area("Questions and Answers", questions, height=400)
                st.download_button(
                    label="Download Questions&Answer",
                    data=questions,
                    file_name="Interview_Questions.txt",
                    mime="text/plain"
                )
            else:
                st.error(questions)

# Career Insights Section
elif page == "Career Insights":
    st.title("📰 Career Insights")
    st.markdown("Stay updated with the latest job market trends and company hiring news.")

    newsapi = NewsApiClient(api_key=newsapi_key)


    def get_gnews_articles():
        url = f"https://gnews.io/api/v4/search?q=job%20market%20OR%20employment%20OR%20hiring%20OR%20recruitment%20OR%20careers%20OR%20job%20opportunities%20India%20OR%20tech%20OR%20IT%20OR%20technology&lang=en&country=in&max=10&apikey={gnews_api_key}"
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode("utf-8"))
                if "articles" in data:
                    return [
                        {
                            "title": article["title"],
                            "description": article.get("description", "No description available"),
                            "source": article["source"]["name"],
                            "published_at": article["publishedAt"],
                            "url": article["url"]
                        }
                        for article in data["articles"]
                    ]
                return []
        except Exception as e:
            st.error(f"Failed to fetch GNews: {e}")
            return []


    def get_indian_job_news():
        try:
            days_back=7
            current_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            if not isinstance(days_back, int):
                raise ValueError("Invalid date format for from_param")
            job_news = newsapi.get_everything(
                q='(jobs OR hiring OR recruitment OR employment OR "job market") AND (India OR Indian)',
                language='en',
                sort_by='publishedAt',
                from_param= start_date,
                to= current_date,
                page_size=10
            )
            return [
                {
                    "title": article["title"],
                    "description": article.get("description", "No description available"),
                    "source": article["source"]["name"],
                    "published_at": article["publishedAt"],
                    "url": article["url"]
                }
                for article in job_news.get("articles", [])
            ]
        except Exception as e:
            st.error(f"Unexpected error fetching job news: {str(e)}")
            return []


    def get_indian_tech_news():
        try:
            days_back=7
            current_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            domains = 'economictimes.indiatimes.com,livemint.com,indiatoday.in'
            tech_news = newsapi.get_everything(
                q='(tech OR IT OR technology OR startup) AND (India OR Indian)',
                domains=domains,
                language='en',
                sort_by='relevancy',
                from_param= start_date,
                to= current_date,
                page_size=10
            )
            return [
                {
                    "title": article["title"],
                    "description": article.get("description", "No description available"),
                    "source": article["source"]["name"],
                    "published_at": article.get("publishedAt", "N/A"),
                    "url": article["url"]
                }
                for article in tech_news.get("articles", [])
            ]
        except Exception as e:
            st.error(f"Unexpected error fetching tech news: {str(e)}")
            return []


    def get_company_hiring_news():
        companies = ['Meta', 'Microsoft', 'Google', 'Apple', 'Amazon']
        company_news = []
        try:
            days_back=7
            current_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            for company in companies:
                news = newsapi.get_everything(
                    q=f'{company} AND (hiring OR recruitment OR jobs)',
                    language='en',
                    from_param= start_date,
                    to= current_date,
                    page_size=3
                )
                company_articles = [
                    {
                        "title": article["title"],
                        "description": article.get("description", "No description available"),
                        "source": article["source"]["name"],
                        "published_at": article.get("publishedAt", "N/A"),
                        "url": article["url"],
                        "company": company
                    }
                    for article in news.get("articles", [])
                ]
                company_news.extend(company_articles)
            return company_news
        except Exception as e:
            st.error(f"Unexpected error fetching company news: {str(e)}")
            return []


    with st.spinner("Fetching news..."):
        gnews_articles = get_gnews_articles()
        job_news = get_indian_job_news()
        tech_news = get_indian_tech_news()
        company_news = get_company_hiring_news()

    # Job Market News Section 
    st.markdown('<h2 class="section-header">Job Market News</h2>', unsafe_allow_html=True)
    if gnews_articles or job_news:
        st.markdown('<div class="grid-container">', unsafe_allow_html=True)
        for article in gnews_articles:
            st.markdown(f"""
            <div class="article-card">
                <h3>{article['title']}</h3>
                <p class="meta">Source: {article['source']} | Published: {article['published_at']}</p>
                <p class="description">{article['description']}</p>
                <a href="{article['url']}" target="_blank">Read more</a>
            </div>
            """, unsafe_allow_html=True)
        for article in job_news:
            st.markdown(f"""
            <div class="article-card">
                <h3>{article['title']}</h3>
                <p class="meta">Source: {article['source']} | Published: {article['published_at']}</p>
                <p class="description">{article['description']}</p>
                <a href="{article['url']}" target="_blank">Read more</a>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="no-news">No job market news available at the moment. Please try again later.</p>',
                    unsafe_allow_html=True)

    # Company Hiring News Section
    st.markdown('<h2 class="section-header">Company Hiring News</h2>', unsafe_allow_html=True)
    if company_news:
        st.markdown('<div class="grid-container">', unsafe_allow_html=True)
        for article in company_news:
            st.markdown(f"""
            <div class="article-card">
                <h3>{article['title']}</h3>
                <p class="meta">Company: {article['company']} | Source: {article['source']} | Published: {article['published_at']}</p>
                <p class="description">{article['description']}</p>
                <a href="{article['url']}" target="_blank">Read more</a>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="no-news">No company hiring news available at the moment. Please try again later.</p>',
                    unsafe_allow_html=True)

    # Tech Industry News Section
    st.markdown('<h2 class="section-header">Tech Industry News</h2>', unsafe_allow_html=True)
    if tech_news:
        st.markdown('<div class="grid-container">', unsafe_allow_html=True)
        for article in tech_news:
            st.markdown(f"""
            <div class="article-card">
                <h3>{article['title']}</h3>
                <p class="meta">Source: {article['source']} | Published: {article['published_at']}</p>
                <p class="description">{article['description']}</p>
                <a href="{article['url']}" target="_blank">Read more</a>
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="no-news">No tech industry news available at the moment. Please try again later.</p>',
                    unsafe_allow_html=True)


# About Section
elif page == "About":
    st.title("ℹ️ About CareerBoost")
    logo_path = "logo.ico"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_bytes = f.read()
            st.markdown(
                f'<img src="data:image/x-icon;base64,{base64.b64encode(logo_bytes).decode()}" width="150">',
                unsafe_allow_html=True
            )
    else:
        st.warning("Logo file (logo.png) not found. Please upload it to the project directory.")
    st.markdown("""
    **CareerBoost** is here to make your job search easier, smarter, and more successful! 
    Powered by AI and designed with you in mind, our platform helps you find jobs, build standout CVs, ace interviews, 
    and stay updated on career trends—all in one place.
    """)

    # Features Section
    st.markdown('<h2 class="section-header">What We Offer</h2>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - **🔍 Job Finding**  
          Discover job opportunities across top platforms with personalized filters.  
        - **📝 CV Maker**  
          Create professional, ATS-friendly CVs tailored to your dream role.
        """)
    with col2:
        st.markdown("""
        - **🎤 Interview Prep**  
          Practice with customized questions and expert answers to boost your confidence.  
        - **📰 Career Insights**  
          Stay ahead with the latest job market trends and industry news.
        """)

    # Mission Section
    st.markdown('<h2 class="section-header">Our Mission</h2>', unsafe_allow_html=True)
    st.markdown("""
    At CareerBoost, we believe everyone deserves a shot at their dream career. 
    Whether you're just starting out, switching paths, or aiming for the top, 
    we’re here to provide the tools and support you need to succeed. 
    Our goal is to make career growth accessible, inclusive, and stress-free.
    """)

    # Contact Section
    st.markdown('<h2 class="section-header">Get In Touch</h2>', unsafe_allow_html=True)
    st.markdown("""
    We’d love to hear from you! Whether you have questions, feedback, or just want to chat, 
    reach out to us anytime.
    """)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        - 📧 **Email**: [yuvrajrajputgh24@gmail.com](mailto:yuvrajrajputgh24@gmail.com)  
        - 💼 **Hugging Face**: [CareerBoost Hugging Face](https://huggingface.co/yuvrajrajput0002)
        """)
    with col2:
        st.markdown("""
        - 🌐 **Website**: [www.careerboost.ai](https://omnicipher.onrender.com)  
        - ⌨️ **GitHub**: [CareerBoost GitHub](https://github.com/yuvrajrajput)
        """)

    # Call-to-Action
    st.markdown("Start Your Career Journey Now!")