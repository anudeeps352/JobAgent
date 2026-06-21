import argparse
from extract_and_clean import extract_resume
from llm import analyze

def main():
    parser = argparse.ArgumentParser(description="Match a resume to a job description")
    parser.add_argument("--jd", required=True, help="Path to job description text file")
    parser.add_argument("--resume", required=True, help="Path to resume PDF")
    args = parser.parse_args()

    jd = open(args.jd).read()
    resume = extract_resume(args.resume)
    result = analyze(jd, resume)
    print(result)

if __name__ == "__main__":
    main()