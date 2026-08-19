from pydantic import BaseModel


class DashboardStat(BaseModel):
    label: str
    value: str | int
    delta_value: str
    delta_direction: str


class FunnelStage(BaseModel):
    label: str
    value: int
    width_percent: int
    drop_percent: str | None = None


class SkillGapItem(BaseModel):
    skill: str
    matches_missing: int


class RecentApplicationItem(BaseModel):
    company: str
    company_initials: str
    role: str
    match_score: int
    status: str
    date: str


class DashboardSummary(BaseModel):
    stats: list[DashboardStat]
    funnel_stages: list[FunnelStage]
    skill_gaps: list[SkillGapItem]
    recent_applications: list[RecentApplicationItem]
    insight: str
