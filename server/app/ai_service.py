import os
from app.models import GrievanceReport, AgentDecision, Grievance
from app.tools import evaluate_severity_index, match_municipal_department, draft_civic_dispatch

def get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "")
    if not key or key == "replace_me":
        return ""
    return key

def extract_grievance(text: str = "", file_bytes: bytes = None, mime_type: str = None) -> GrievanceReport:
    """
    AI extraction boundary stub.
    Developer will hand-code Gemini SDK calls here.
    """
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("Gemini API key not configured. Use demo data or set GEMINI_API_KEY.")

    # TODO(manual): call Gemini with structured output
    # Example interface implementation placeholder:
    # client = genai.Client(api_key=api_key)
    # response = client.models.generate_content(...)
    
    raise NotImplementedError("Manual Gemini extraction implementation pending in backend/app/ai_service.py")

def choose_next_step(
    goal: str,
    findings: list[dict],
    tool_results: list[dict],
    available_tools: list[str]
) -> AgentDecision:
    """
    AI agent planner stub.
    Uses deterministic offline fallback planner when API key is unconfigured.
    """
    api_key = get_api_key()
    if not api_key:
        # Deterministic offline planner fallback logic (L8 spec)
        evaluated = False
        matched = False
        drafted = False

        for tr in tool_results:
            name = tr.get("tool_name")
            if name == "evaluate_severity_index":
                evaluated = True
            elif name == "match_municipal_department":
                matched = True
            elif name == "draft_civic_dispatch":
                drafted = True

        if not evaluated:
            return AgentDecision(
                tool_name="evaluate_severity_index",
                arguments={},
                message="Evaluating grievance severity indices to isolate critical issues."
            )
        
        if evaluated and not matched:
            if findings:
                first = findings[0]
                return AgentDecision(
                    tool_name="match_municipal_department",
                    arguments={"category": first["category"], "location": first["location"]},
                    message=f"Matching municipal authority for critical finding: {first['title']}."
                )
            else:
                return AgentDecision(
                    tool_name="finish",
                    arguments={},
                    message="No critical infrastructure hazards identified."
                )
        
        if matched and not drafted:
            if findings:
                first = findings[0]
                # Find matching department from tool results
                dept = "Department of Transportation & Infrastructure"
                for tr in tool_results:
                    if tr.get("tool_name") == "match_municipal_department":
                        dept = tr.get("result", {}).get("assigned_department", dept)
                
                return AgentDecision(
                    tool_name="draft_civic_dispatch",
                    arguments={
                        "title": first["title"],
                        "department": dept,
                        "location": first["location"],
                        "priority_index": first["priority_index"]
                    },
                    message="Drafting official civic dispatch notice for human approval."
                )
        
        return AgentDecision(
            tool_name="finish",
            arguments={},
            message="Agent workflow complete."
        )

    # TODO(manual): LLM planner returning AgentDecision via Gemini SDK
    raise NotImplementedError("Manual Gemini planner implementation pending in backend/app/ai_service.py")
