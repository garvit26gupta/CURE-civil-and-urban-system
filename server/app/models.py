from typing import Literal, Optional
from datetime import date
from pydantic import BaseModel, Field

CivicCategory = Literal[
    "Roads & Bridges",
    "Water & Sanitation",
    "Public Safety",
    "Pollution & Environment",
    "Power & Grid",
    "Other"
]

SeverityLevel = Literal["Low", "Medium", "High", "Critical"]

class Grievance(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    date: Optional[str] = None
    category: CivicCategory = "Other"
    severity: SeverityLevel = "Medium"
    location: Optional[str] = None
    raw_line: Optional[str] = None

class GrievanceReport(BaseModel):
    grievances: list[Grievance]
    notes: list[str] = Field(default_factory=list)

class AuditRequest(BaseModel):
    grievances: list[Grievance]
    goal: str

class ApprovalRequest(BaseModel):
    decision: Literal["approve", "reject"]
    reason: Optional[str] = None

class AgentDecision(BaseModel):
    tool_name: Literal[
        "evaluate_severity_index",
        "match_municipal_department",
        "draft_civic_dispatch",
        "finish"
    ]
    arguments: dict = Field(default_factory=dict)
    message: str

class AuditSession(BaseModel):
    session_id: str
    status: Literal["analyzing", "awaiting_approval", "executing", "done", "failed"]
    goal: str
    findings: list[dict] = Field(default_factory=list)
    pending_action: Optional[dict] = None
    audit_log: list[dict] = Field(default_factory=list)
    summary: str = ""
    steps: int = 0
