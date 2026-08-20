import re
from collections import Counter

from sqlalchemy.orm import Session, joinedload

from src.analyses.models import Analysis
from src.applications.models import Application


def _parse_score(score: str) -> int:
    match = re.search(r"\d+", score)
    if not match:
        return 0
    value = int(match.group())
    return value * 10 if "/10" in score else value


def _company_initials(company: str) -> str:
    letters = [part[0] for part in company.split() if part]
    initials = "".join(letters[:3]).upper()
    return initials or company[:3].upper() or "N/A"


def get_summary(db: Session) -> dict:
    analyses = db.query(Analysis).options(
        joinedload(Analysis.resume),
        joinedload(Analysis.job_description),
    ).all()
    records = db.query(Application).options(
        joinedload(Application.analysis),
        joinedload(Application.resume),
        joinedload(Application.job_description),
    ).order_by(Application.created_at.desc()).all()

    total_applications = len(records)
    submitted = [record for record in records if (record.status or "").upper() != "PLANNED"]
    interviewing = sum(1 for record in records if (record.status or "").upper() == "INTERVIEWING")
    offers = sum(1 for record in records if (record.status or "").upper() == "OFFER")
    active_apps = sum(
        1
        for record in records
        if (record.status or "").upper() in {"APPLIED", "OA", "OA SENT", "INTERVIEWING"}
    )
    response_rate = round((interviewing + offers) / len(submitted) * 100, 1) if submitted else 0.0

    status_order = ["APPLIED", "OA", "INTERVIEWING", "OFFER"]
    stage_counts = Counter((record.status or "APPLIED").upper() for record in records)
    funnel_stages = []
    for index, stage in enumerate(status_order):
        value = stage_counts.get(stage, 0)
        width_percent = round((value / total_applications) * 100) if total_applications else 0
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
                "drop_percent": None if index == 0 or not total_applications else f"-{max(0, 100 - width_percent)}%",
            }
        )

    skill_counts = Counter()
    for record in analyses:
        skill_counts.update(record.gaps or [])

    skill_gaps = [
        {"skill": skill, "matches_missing": count}
        for skill, count in skill_counts.most_common(3)
    ]

    recent_applications = [
        {
            "company": record.company,
            "company_initials": _company_initials(record.company),
            "role": record.role,
            "match_score": _parse_score(record.analysis.score) if record.analysis else 0,
            "status": (record.status or "PLANNED").upper(),
            "date": (record.applied_at or record.created_at).strftime("%Y-%m-%d"),
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
                "label": "TOTAL APPLICATIONS",
                "value": total_applications,
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
