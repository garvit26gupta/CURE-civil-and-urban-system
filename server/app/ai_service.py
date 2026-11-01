import os
from google import genai
from google.genai import types
from app.models import GrievanceReport, AgentDecision, Grievance
from app.tools import evaluate_severity_index, match_municipal_department, draft_civic_dispatch

def get_api_key() -> str:
    key = os.getenv("GEMINI_API_KEY", "")
    if not key or key == "replace_me":
        return ""
    return key

def extract_grievance(text: str = "", file_bytes: bytes = None, mime_type: str = None) -> GrievanceReport:
    """
    Extracts structured civic grievances from raw text or uploaded media files using Gemini.
    """
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError("Gemini API key not configured. Use demo data or set GEMINI_API_KEY.")

    client = genai.Client(api_key=api_key)
    model_id = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    # Build contents payload for multimodal or text input
    contents = []
    if text:
        contents.append(text)
    
    if file_bytes and mime_type:
        contents.append(
            types.Part.from_bytes(
                data=file_bytes,
                mime_type=mime_type
            )
        )

    if not contents:
        return GrievanceReport(grievances=[], notes=["No input content provided for extraction."])

    system_prompt = (
        "You are an expert civic infrastructure triage assistant. "
        "Extract localized civic issues (e.g., potholes, water leaks, downed wires) strictly from the provided evidence. "
        "Map categories strictly to one of: 'Roads & Bridges', 'Water & Sanitation', 'Public Safety', 'Pollution & Environment', 'Power & Grid', 'Other'. "
        "Classify severity as 'Low', 'Medium', 'High', or 'Critical'. "
        "If dates or locations are unclear, set them to null and add an explanatory note."
    )

    # Call Gemini with structured JSON output enforced by Pydantic schema
    response = client.models.generate_content(
        model=model_id,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_json_schema=GrievanceReport.model_json_schema(),
            temperature=0.1
        )
    )

    # Parse JSON response back into validated Pydantic model
    return GrievanceReport.model_validate_json(response.text)

def choose_next_step(
    goal: str,
    findings: list[dict],
    tool_results: list[dict],
    available_tools: list[str]
) -> AgentDecision:
    """
    Agent planner. Uses the robust deterministic offline planner 
    (or can be extended with Gemini tool-calling logic).
    """
    api_key = get_api_key()
    
    # Deterministic offline planner fallback logic (ensures 100% reliable local execution)
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