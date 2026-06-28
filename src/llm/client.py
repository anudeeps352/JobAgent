import re
from anthropic import Anthropic
from src.config import ANTHROPIC_API_KEY, LLM_MODEL, LLM_MAX_TOKENS
from src.llm.prompts import SYSTEM_PROMPT

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def analyze(jd, resume):
    response = client.messages.create(
        model=LLM_MODEL,
        max_tokens=int(LLM_MAX_TOKENS),
        system=SYSTEM_PROMPT,
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