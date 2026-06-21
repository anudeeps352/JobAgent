import argparse
from extract_and_clean import extract_resume
from llm import analyze
from storage import save, print_history, check_duplicate, compute_jd_hash

def main():
    parser = argparse.ArgumentParser(description="Match a resume to a job description")
    parser.add_argument("--jd",      help="Path to job description text file")
    parser.add_argument("--resume",  help="Path to resume PDF")
    parser.add_argument("--company", help="Override company name if not found in JD")
    parser.add_argument("--history", action="store_true", help="Show past results")
    args = parser.parse_args()

    if args.history:
        print_history()
        return

    if not args.jd or not args.resume:
        print("Error: --jd and --resume are required unless using --history")
        return

    jd = open(args.jd).read()

    # dedup check BEFORE calling LLM
    jd_hash = compute_jd_hash(jd)
    existing = check_duplicate(jd_hash)
    if existing:
        print(f"\n⚠️  You already analyzed this JD on {existing['timestamp']}")
        print(f"Company: {existing['company']} | Role: {existing['role']} | Status: {existing['status']}")
        confirm = input("Analyze again anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Skipped.")
            return

    # only reaches here if new JD or user confirmed
    resume = extract_resume(args.resume)
    analysis = analyze(jd, resume)

    print("\n" + analysis["full_analysis"])

    save(
        jd_text=jd,
        resume_path=args.resume,
        analysis=analysis,
        company_override=args.company
    )

if __name__ == "__main__":
    main()