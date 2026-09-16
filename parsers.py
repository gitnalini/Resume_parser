from pathlib import Path 
from groq import Groq
from dotenv import load_dotenv
from pypdf import PdfReader
from docx import Document
from pydantic import BaseModel
import os

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


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

        return text
    else:
        raise ValueError("only .pdf and .docx is allowed will enter valid format")


resume_path = input("Enter the resume file path: ")
resume_text = read_resume(resume_path)
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("PLEASE SHARE YPOYT API")

class pars(BaseModel):
    candidate_no:int
    age:int
    experience:int
    skills:str
    total_skills:int
    Fail_Pass:int
    summary:str


schema=pars.model_json_schema()
response_format={
    "type":"json_object"
}

details="skills required will be java,javascript,node,react,docker,web development, frontend, backend. experience>1 year. plus point if they have some interships, experince:related to tech side. age: between 20-35.  fail/pass: in percentage. and key points or summary in less than 300 words about overall skills"
client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"
role="user"
prompt= f"""
Parse this resume according to the given criteria.

RESUME:
{resume_text}
"""

message={
    "role":role,
    "content":prompt
}

message_system={
    "role":"system",
    "content":f"""You are a resume parser where I will share you the word/pdf of the candidates and you will parse the following details and percetage of the overall resume according to the cretrie I am sharing share in a json clean format only{schema}, also check the details {details}"""
}

messages=[message_system,message]

response=client.chat.completions.create(model=model, messages=messages,)
print("############################################################################################")
answer=response.choices[0].message.content
print(answer) 
