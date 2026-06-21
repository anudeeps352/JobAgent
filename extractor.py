import pymupdf as fitz

def raw_extract(path):
    doc = fitz.open(path)
    for i,page in enumerate(doc):
        print(f"\n-- PAGE {i+1} --\n")
        print(page.get_text())
raw_extract("resume.pdf")