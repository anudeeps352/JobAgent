import os
import re
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def analyze(jd, resume):
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        system="""You are a resume screener. Given a JD and resume, output exactly in this format:

COMPANY: company name extracted from JD or "Unknown" if not found
ROLE: job title extracted from JD
MATCH: Strong / Partial / Weak
SCORE: X/10 core requirements met
GAPS: bullet list of missing or weak required skills
SUGGESTIONS: 2-3 specific edits to strengthen this resume for this role

Be direct. No preamble.""",
        messages=[
            {
                "role": "user",
                "content": f"JD:\n{jd}\n\nRESUME:\n{resume}"
            }
        ]
    )

    if response.stop_reason == "max_tokens":
        print("WARNING: response was cut off, increase max_tokens")

    print(f"Input tokens:  {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
    print(f"Total tokens:  {response.usage.input_tokens + response.usage.output_tokens}")
    print("-" * 40)

    return parse_response(response.content[0].text)


def parse_response(text):
    def extract(label):
        match = re.search(rf'^{label}:\s*(.+)$', text, re.MULTILINE)
        return match.group(1).strip() if match else "Unknown"

    return {
        "company":       extract("COMPANY"),
        "role":          extract("ROLE"),
        "match":         extract("MATCH"),
        "score":         extract("SCORE"),
        "full_analysis": text
    }