from pathlib import Path 
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
from pydantic import BaseModel
import os
import json
import time

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

my_api_key=os.getenv("GROQ_API_KEY")


if not my_api_key:
    raise ValueError("PLEASE SHARE YPOYT API")

client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"



def read_resume(file_path):
    file_path=Path(file_path)

    if file_path.suffix.lower() == ".pdf":
        reader=PdfReader(file_path)

        text=""
        for page in reader.pages:
            text+=page.extract_text() or ""
        return text
    elif file_path.suffix.lower() == ".docx":
        document=Document(file_path)

        text=""
        for paragraph in document.paragraphs:
            text+= paragraph.text + "\n"

        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text+=cell.text + "\n"
        

        return text
    else:
        raise ValueError("only .pdf and .docx is allowed will enter valid format")


# resume_path = input("Enter the resume file path: ")
# resume_text = read_resume(resume_path)







# class pars(BaseModel):
#     candidate_no:int
#     age:int
#     experience:int
#     skills:str
#     total_skills:int
#     Fail_Pass:int
#     summary:str


# schema=pars.model_json_schema()
# response_format={
#     "type":"json_object"
# }

# jobD="""
# details:skills required will be java,javascript,node,react,docker,web development, frontend, backend. experience>1 year. plus point if they have some interships, experince:related to tech side. age: between 20-35.  fail/pass: in percentage. and key points or summary in less than 300 words about overall skills
# """
job_description="""
Description
Do you want to solve real customer problems through innovative technology? Do you enjoy working on scalable services in a collaborative team environment? Do you want to see your code directly impact millions of customers worldwide?

At Amazon, we hire the best minds in technology to innovate and build on behalf of our customers. Customer obsession is part of our company DNA, which has made us one of the world's most beloved brands.

Our Software Development Engineers (SDEs) use modern technology to solve complex problems while seeing their work's impact first-hand. The challenges SDEs solve at Amazon are meaningful and influence millions of customers, sellers, and products globally. We seek individuals passionate about creating new products, features, and services while managing ambiguity in an environment where development cycles are measured in weeks, not years.

At Amazon, we believe in ownership at every level. As an SDE-I, you'll own the entire lifecycle of your code - from design through deployment and ongoing operations. This ownership mindset, combined with our commitment to operational excellence, ensures we deliver the highest quality solutions for our customers.

We're looking for curious minds who think big and want to define tomorrow's technology. At Amazon, you'll grow into the high-impact engineer you know you can be, supported by a culture of learning and mentorship. Every day brings exciting new challenges and opportunities for personal growth.
Key job responsibilities
• Collaborate and communicate effectively with experienced cross-disciplinary Amazonians to design, build, and operate innovative products and services that delight our customers, while participating in technical discussions to drive solutions forward.
• Design and develop scalable solutions using cloud-native architectures and microservices in a large distributed computing environment.
• Participate in code reviews and contribute to technical documentation.
• Build and maintain resilient distributed systems that are scalable, fault-tolerant, and cost-effective.
• Leverage and contribute to the development of GenAI and AI-powered tools to enhance development productivity while staying current with emerging technologies.
• Write clean, maintainable code following best practices and design patterns.
• Work in an agile environment practicing CI/CD principles while participating in operational responsibilities including on-call duties.
• Demonstrate operational excellence through monitoring, troubleshooting, and resolving production issues.
Basic Qualifications
- Experience with at least one general-purpose programming language such as Java, Python, C++, C#, Go, Rust, or TypeScript
- Experience with data structure implementation, basic algorithm development, and/or object-oriented design principles
- Currently has, or is in the process of obtaining a bachelor’s degree in Computer Science, Computer Engineering, Data Science, Information Systems, or related STEM fields
- Must be 18 years of age of older
Preferred Qualifications
- Experience from previous technical internship(s) or demonstrated project experience
- Experience with one or more of the following: AI tools for development productivity, Cloud platforms (preferably AWS), Database systems (SQL and NoSQL), Contributing to open-source projects, Version control systems, Debugging and troubleshooting complex systems
- Demonstrated ability to learn and adapt to new technologies quickly
- Basic understanding of software development lifecycle (SDLC)
- Strong problem-solving and analytical skills
- Excellent written and verbal communication skills
"""
class JobD(BaseModel):
    role:str
    required_skills:list[str]
    preferred_skills:list[str]
    minimum_experince: float | None
    education_requirements: list[str]
    responsibilities:list[str]

JobD_schema=JobD.model_json_schema()

system_prompt=f"""
You are an expert HR assistant.

Your job is to analyze job descriptions and extract
structured information from them.

Return ONLY valid JSON matching this schema:

{JobD_schema}
IMPORTANT:
Do NOT return the schema itself.
Do NOT return fields like "properties", "title" or "type".
Fill the schema with actual information extracted from the job description.

If minimum experience is not mentioned, return null.
If information for a list is missing, return an empty list.
Do not invent information.
"""


role="user"
user_prompt = f"""
Analyze the following job description:

{job_description}
"""
 

message_user={
    "role":role,
    "content":user_prompt
}

message_system={
    "role":"system",
    "content":system_prompt
}

response_format={
    "type":"json_object"
}

messages=[message_system,message_user]

response=client.chat.completions.create(model=model, messages=messages,response_format=response_format)
print("############################################################################################")
answer=response.choices[0].message.content
raw_json=answer
# print(answer) 

# converting json into readable json form 

job_data=json.loads(raw_json)
job=JobD(**job_data)

print(job.minimum_experince)
print(job.education_requirements)

# parse real data

class MatchResult(BaseModel):
    score:float
    details:dict

class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skills_used: list[str] = []

class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    total_experience_years: float |  None = None
    skills: list[str] = []
    experiences: list[Experience] = []
    projects: list[str] =[]
    certifications: list[str]=[]

resume_schema=Resume.model_json_schema()

def final_score(job,resume):
    match_schema=MatchResult.model_json_schema()
    prompt=f"""
    you are a HR recuriter.
    compare the candidate'd resume with the JD.
    JD:
    {job.model_dump_json(indent=2)}
    Return JSON matching this schema :

    CANDIDATE RESUME:
    {resume.model_dump_json(indent=2)}
    Return JSON matching this schema:

    {match_schema}
    
    give me 
    Candidate name,matching skills, missing important skills, whether exp requiemnt is not,Ovrall match percentage from 0 to 100
    a short final verdict
    keep response concise and easy to read
    """
    message={
        "role":"user",
        "content":prompt
    }
    messages=[message]
    response_format={
        "type":"json_object"
    }

    response=client.chat.completions.create(model=model, messages=messages,response_format=response_format)
    data=json.loads(response.choices[0].message.content)
    return MatchResult(**data)

def parse_resume(resume_text):
    system_prompt=f"""
    You are an expert resume parser.
    Extract information from the resume based on its meaning,
    not only based on exact section headings.
    Different resumes may use different headings.

    For example: -experience,Professional experience,work istory, employment, internships
    they may all contain relavent experience.
    Read only the valid JSON matching this schema:{resume_schema}
   IMPORTNAT RULES:
   DONOT invent information
   if value is no available, return null.
   if list has no information, return an empty list.
   include internships inside experience
   Extract skill mentioned across the entir resume.
"""
    user_prompt = f"""
    Parse the following resume:

    {resume_text}
    """

    message_system={
        "role":"system",
        "content":system_prompt
    }
    message_user={
        "role":"user",
        "content":user_prompt
    }
    messages=[message_system,message_user]
    response_format={
        "type":"json_object"
    }
    response=client.chat.completions.create(model=model,messages=messages, response_format=response_format)
    raw_output=response.choices[0].message.content
    data=json.loads(raw_output)
    resume=Resume(**data)
    return resume



resume_folder=Path("Resume")
all_results=[]
for file_path in resume_folder.iterdir():
    if file_path.suffix.lower() not in [".pdf",".docx"]:
        continue
    print("\nProcessing:",file_path.name)
    resume_text=read_resume(file_path)
    parsed_resume=parse_resume(resume_text)
    time.sleep(5)
    result=final_score(job,parsed_resume)
    time.sleep(5)
    print("Score", result.score)
    all_results.append({
        "name":parsed_resume.name,
        "score":result.score,
        "details":result.details
    })
all_results.sort(
    key=lambda candidate: candidate["score"],
    reverse=True
)
top_2 = all_results[:2]
worst_2 = all_results[-2:]


print("TOP 2 CANDIDATES")
for candidate in top_2:

    print(
        candidate["name"],
        "-",
        candidate["score"],
        "%"
    )

    print(candidate["details"])

print("LOWEST 2 CANDIDATES")
for candidate in worst_2:

    print(
        candidate["name"],
        "-",
        candidate["score"],
        "%"
    )
    print(candidate["details"])