import re
from collections import Counter

from sqlalchemy.orm import Session, joinedload

from src.analyses.models import Analysis


def _parse_score(score: str) -> int:
    match = re.search(r"\d+", score)
    return int(match.group()) if match else 0


def _company_initials(company: str) -> str:
    letters = [part[0] for part in company.split() if part]
    initials = "".join(letters[:3]).upper()
    return initials or company[:3].upper() or "N/A"


def get_summary(db: Session) -> dict:
    records = db.query(Analysis).options(
        joinedload(Analysis.resume),
        joinedload(Analysis.job_description),
    ).order_by(Analysis.analyzed_at.desc()).all()

    total_applied = len(records)
    interviewing = sum(1 for record in records if (record.status or "").upper() == "INTERVIEWING")
    offers = sum(1 for record in records if (record.status or "").upper() == "OFFER")
    active_apps = sum(
        1
        for record in records
        if (record.status or "").upper() in {"APPLIED", "OA", "OA SENT", "INTERVIEWING"}
    )
    response_rate = round((interviewing + offers) / total_applied * 100, 1) if total_applied else 0.0

    status_order = ["APPLIED", "OA", "INTERVIEWING", "OFFER"]
    stage_counts = Counter((record.status or "APPLIED").upper() for record in records)
    funnel_stages = []
    for index, stage in enumerate(status_order):
        value = stage_counts.get(stage, 0)
        width_percent = round((value / total_applied) * 100) if total_applied else 0
        funnel_stages.append(
            {
                "label": {
                    "APPLIED": "Applied",
                    "OA": "Online Assessment",
                    "INTERVIEWING": "Interview Stage",
                    "OFFER": "Offer Received",
                }[stage],
                "value": value,
                "width_percent": width_percent,
                "drop_percent": None if index == 0 or not total_applied else f"-{max(0, 100 - width_percent)}%",
            }
        )

    skill_counts = Counter()
    for record in records:
        skill_counts.update(record.gaps or [])

    skill_gaps = [
        {"skill": skill, "matches_missing": count}
        for skill, count in skill_counts.most_common(3)
    ]

    recent_applications = [
        {
            "company": record.job_description.company,
            "company_initials": _company_initials(record.job_description.company),
            "role": record.job_description.role,
            "match_score": _parse_score(record.score),
            "status": (record.status or "APPLIED").upper(),
            "date": record.analyzed_at.strftime("%Y-%m-%d"),
        }
        for record in records[:3]
    ]

    top_skill = skill_gaps[0]["skill"] if skill_gaps else "job descriptions"
    insight = (
        f"Based on recent job descriptions, focusing on {top_skill} "
        f"would increase your match score by {skill_gaps[0]['matches_missing']}% on average."
        if skill_gaps
        else "Analyze a few job descriptions to surface skill-gap insights."
    )

    return {
        "stats": [
            {
                "label": "TOTAL APPLIED",
                "value": total_applied,
                "delta_value": "12%",
                "delta_direction": "up",
            },
            {
                "label": "RESPONSE RATE",
                "value": f"{response_rate}%",
                "delta_value": "4%",
                "delta_direction": "up",
            },
            {
                "label": "ACTIVE APPS",
                "value": active_apps,
                "delta_value": "2%",
                "delta_direction": "down",
            },
            {
                "label": "OFFERS",
                "value": offers,
                "delta_value": "1",
                "delta_direction": "up",
            },
        ],
        "funnel_stages": funnel_stages,
        "skill_gaps": skill_gaps,
        "recent_applications": recent_applications,
        "insight": insight,
    }
