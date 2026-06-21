import re
import pymupdf

def clean_resume_text(text):
    # remove phone numbers
    text = re.sub(r'[\+\(]?[0-9][0-9\s\-\(\)]{7,}[0-9]', '', text)
    
    # remove emails
    text = re.sub(r'\S+@\S+\.\S+', '', text)
    
    # remove URLs
    text = re.sub(r'(https?://\S+|www\.\S+|[a-zA-Z0-9\-]+\.[a-zA-Z]{2,}/\S+)', '', text)
    
    # remove divider lines (3+ underscores, dashes, or equals)
    text = re.sub(r'[_\-=]{3,}', '', text)
    
    # collapse excess blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # strip whitespace per line
    text = "\n".join(line.strip() for line in text.splitlines())
    
    return text.strip()


def extract_resume(path):
    doc = pymupdf.open(path)
    raw = "\n".join(page.get_text() for page in doc)
    return clean_resume_text(raw)


if __name__ == "__main__":
    text = extract_resume("resume.pdf")
    print(text)