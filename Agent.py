import os
import json
import random
import asyncio
import aiohttp
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.tools import Tool
from duckduckgo_search import DDGS
from tenacity import retry, stop_after_attempt, wait_exponential
from functools import lru_cache
import re
import http.client
import urllib.parse
from pydantic.v1 import SecretStr

# Random User-Agent
def get_random_user_agent():
    """ Various user-agent strings for Windows, macOS, Linux, Mobile devices, Tablets, Consoles, Smart TVs
        This helps avoid being blocked by websites due to repetitive scraping
        List of user agents truncated for brevity"""
    USER_AGENTS = [
    # Windows User Agents
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',

    # macOS User Agents
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0',

    # Linux User Agents
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) HeadlessChrome/91.0.4472.124 Safari/537.36',

    # Mobile User Agents (Android)
    'Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 9; SM-G960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36',

    # Mobile User Agents (iOS)
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/91.0.4472.124 Mobile/15E148 Safari/604.1',  # Chrome on iOS

    # Tablet User Agents
    'Mozilla/5.0 (Linux; Android 10; SM-T860) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; Lenovo TB-X606F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36',
    'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',

    # Gaming Consoles
    'Mozilla/5.0 (PlayStation 4 8.52) AppleWebKit/605.1.15 (KHTML, like Gecko)',
    'Mozilla/5.0 (Nintendo Switch; WifiWebAuthApplet) AppleWebKit/609.4 (KHTML, like Gecko) NF/6.0.2.19.3 NintendoBrowser/5.1.0.22401',

    # Smart TVs
    'Mozilla/5.0 (Web0S; Linux/SmartTV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 WebAppManager',
    'Mozilla/5.0 (SMART-TV; Linux; Tizen 5.5) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/3.0 Chrome/91.0.4472.124 Safari/537.36',

    ]
    return random.choice(USER_AGENTS)

# Load API keys
google_api_key = os.getenv("AIzaSyCqLfDYMipOqYBtuZxOSR9cd9SvfSs5I40")
rapidapi_key = os.getenv("RAPIDAPI_KEY")

if not google_api_key:
    raise ValueError("Google API key not found.")
if not rapidapi_key:
    raise ValueError("RapidAPI key not found.")

# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=SecretStr(google_api_key)
)

# DuckDuckGo search
def duckduckgo_search(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=20)]
        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Error in WebSearch: {str(e)}"}, indent=2)

duckduckgo_tool = Tool(
    name="WebSearch",
    func=duckduckgo_search,
    description="Use this tool to search the web for job listings or interview questionss"
)


# Job finding agent
job_prompt = PromptTemplate(
    input_variables=["input", "chat_history", "tools", "tool_names", "agent_scratchpad"],
    template="""
    You are an advanced job search assistant focused on finding job vacancies worldwide, with a special emphasis on India.
    Your tasks:
    - Find relevant job listings based on the field and location, including job titles, companies, locations, and links.
    - Use the JobScraper tool first to get detailed job listings from job boards like Naukri.com, Shine.com, LinkedIn, and Indeed and other indian job boards.
    - If JobScraper fails or returns no valid jobs, use WebSearch to find job-related information and extract relevant details.
    - Avoid duplicate listings by checking job titles, companies, and locations.
    - Format the output as a numbered list with: Title, Company, Location, Link, Source.
    - If no jobs are found, clearly state so and provide any relevant links from WebSearch.
    - Include all valid job details from JobScraper observations in the final answer.

    Available tools: {tools}
    Tool names: {tool_names}

    User input: {input}
    Chat history: {chat_history}
    Agent scratchpad: {agent_scratchpad}
    """
)

job_memory = ConversationBufferMemory(memory_key="chat_history")
job_agent = initialize_agent(
    tools=[duckduckgo_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=job_memory,
    handle_parsing_errors=True,
    custom_prompt=job_prompt
)


# RapidAPI job searcher
def rapid_job_seacrher(job: str, location: str, pages: int = 1, country: str = "in") -> str:
    conn = http.client.HTTPSConnection("jsearch.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': rapidapi_key,
        'x-rapidapi-host': "jsearch.p.rapidapi.com"
    }
    query = urllib.parse.quote(f"{job} jobs in {location}")
    conn.request("GET", f"/search?query={query}&page=1&num_pages={pages}&country={country}&date_posted=all", headers=headers)
    res = conn.getresponse()
    data = res.read()
    results = []

    try:
        data_json = json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as e:
        return json.dumps({"error": f"Error parsing JSON: {str(e)}"}, indent=2)

    for job in data_json.get('data', []):
        if not isinstance(job, dict):
            continue
        title = job.get('job_title', 'N/A')
        company = job.get('employer_name', 'N/A')
        city = job.get('job_city', '')
        state = job.get('job_state', '')
        location_parts = [part for part in [city, state] if part]
        location = ", ".join(location_parts) if location_parts else "N/A"
        job_url = job.get('job_apply_link', 'N/A')
        results.append({
            "title": title,
            "company": company,
            "location": location,
            "link": job_url,
            "source": "RapidAPI"
        })

    return json.dumps(results if results else {"error": "No jobs found."}, indent=2)

# #Remove common markdown characters from text using regex
# def remove_markdown(text: str) -> str:
#     patterns = [
#         (r'^#+ ?', ''),
#         (r'\*\*(.*?)\*\*', r'\1'),
#         (r'\*(.*?)\*', r'\1'),
#         (r'^- ?', ''),
#         (r'\[([^\]]+)\]\([^\)]+\)', r'\1'),
#         (r'^\s*:\s*', ''),
#         (r'`{1,3}[^`]+`{1,3}', lambda m: m.group(0).replace('`', ''))
#     ]
#     cleaned_text = text
#     for pattern, replacement in patterns:
#         cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.MULTILINE)
#     cleaned_text = re.sub(r'\n\s*\n', '\n', cleaned_text).strip()
#     return cleaned_text

# Interview preparation
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
            You are an interview preparation expert. Generate exactly 10 interview questions with detailed, professional answers for {job_field}. Do NOT provide links or references to external resources; focus on self-contained questions and answers.
            Requirements:
            - Include 4 technical questions, 3 behavioral questions, and 3 situational questions.
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

interview_tool = Tool(
    name="InterviewPreparer",
    func=interview_preparer,
    description="Generate 10 interview questions and answers for a job field (4 technical, 3 behavioral, 3 situational)."
)

interview_prompt = PromptTemplate(
    input_variables=["input", "chat_history", "tools", "tool_names", "agent_scratchpad"],
    template="""
    You are an interview preparation assistant. Your task is to:
    - Extract the job field from the user input (e.g., 'Prepare interview for data science' → job_field='data science').
    - Use the InterviewPreparer tool exactly once to generate 10 interview questions with answers (4 technical, 3 behavioral, 3 situational).
    - Do NOT attempt to create questions manually or simulate the tool's output.
    - If the job field is unclear, return an error message asking for clarification.
    - In the Final Answer, return only the tool's output as plain text, with no additional commentary.

    Follow this strict format:
    Thought: [Your reasoning]
    Action: InterviewPreparer
    Action Input: job_field="[job_field]"
    Observation: [Tool output]
    Final Answer: [Tool output]

    Available tools: {tools}
    Tool names: {tool_names}

    User input: {input}
    Chat history: {chat_history}
    Agent scratchpad: {agent_scratchpad}
    """
)

interview_memory = ConversationBufferMemory(memory_key="chat_history")
interview_agent = initialize_agent(
    tools=[interview_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    memory=interview_memory,
    handle_parsing_errors=True,
    custom_prompt=interview_prompt
)

# CV creator
cv_llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=SecretStr(google_api_key),
    temperature=0.1,
    max_output_tokens=2048
)

cv_prompt = PromptTemplate(
    input_variables=["job_field", "experience"],
    template="""
    You are a professional CV writer. Create a concise, ATS-friendly CV for a {job_field} position based on the following details:
    - User Details: Name: John Doe, Email: john.doe@example.com, Phone: +91-9876543210
    - Experience and skills: {experience}  
    Include sections for Summary, Skills, Experience, and Education. Format as plain text for clarity.
    """
)

def generate_cv(job_field: str, experience: str) -> str:
    try:
        prompt = cv_prompt.format(job_field=job_field, experience=experience)
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
        return f"Error generating CV: {str(e)}"