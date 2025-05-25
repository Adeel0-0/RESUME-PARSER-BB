# parser.py
import os
import json
from dotenv import load_dotenv
from groq import Groq
from prompts import RESUME_EXTRACTION_PROMPT

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def parse_resume(text: str) -> dict:
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a resume-parsing assistant."},
            {"role": "user", "content": RESUME_EXTRACTION_PROMPT.format(resume=text)}
        ],
        temperature=0.2,
    )
    
    content = response.choices[0].message.content.strip()

    # Try parsing JSON
    try:
        # Find the first { and last } to extract JSON
        json_start = content.find('{')
        json_end = content.rfind('}') + 1
        json_str = content[json_start:json_end]
        return json.loads(json_str)
    except Exception as e:
        return {"error": f"Failed to parse JSON: {e}", "raw_response": content}
