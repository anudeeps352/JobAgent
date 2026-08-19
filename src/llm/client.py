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


SECTION_LABELS = ["COMPANY", "ROLE", "MATCH", "SCORE", "GAPS", "SUGGESTIONS"]


def parse_response(text):
    def extract(label):
        match = re.search(rf'^{label}:\s*(.+)$', text, re.MULTILINE)
        return match.group(1).strip() if match else "Unknown"

    def extract_section(label):
        """Grab everything after `label:` up to the next known section label."""
        other_labels = "|".join(l for l in SECTION_LABELS if l != label)
        pattern = rf'^{label}:\s*\n?(.*?)(?=^(?:{other_labels}):|\Z)'
        match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
        return match.group(1).strip() if match else ""

    def split_list_items(raw, item_pattern):
        """Split a section into list items, merging wrapped continuation lines."""
        items: list[str] = []
        current: str | None = None
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            m = re.match(item_pattern, line)
            if m:
                if current is not None:
                    items.append(current.strip())
                current = m.group(1)
            elif current is not None:
                current += " " + line
        if current is not None:
            items.append(current.strip())
        return items

    score_raw = extract("SCORE")
    score = score_raw.split(" ")[0]

    gaps = split_list_items(extract_section("GAPS"), r'^[•\-]\s*(.+)')
    suggestions = split_list_items(extract_section("SUGGESTIONS"), r'^\d+\.\s*(.+)')

    return {
        "company":       extract("COMPANY"),
        "role":          extract("ROLE"),
        "match":         extract("MATCH"),
        "score":         score,
        "gaps":          gaps,
        "suggestions":   suggestions,
        "full_analysis": text,  # kept for debugging / raw display fallback
    }