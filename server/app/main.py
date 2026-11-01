import os
import uuid
import datetime
import csv
import io
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.models import (
    Grievance, GrievanceReport, AuditRequest, ApprovalRequest,
    AuditSession, AgentDecision
)
from app.sample_data import sample_grievances
from app import tools
from app import ai_service

app = FastAPI(
    title="CURE - Civil and Urban Repair Engine API",
    version="1.0.0",
    description="Transparent Civic Grievance Triage Agent Backend"
)

# CORS configuration
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
SESSIONS: dict[str, AuditSession] = {}

def get_utc_now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

@app.get("/api/health")
def health_check():
    key = os.getenv("GEMINI_API_KEY", "")
    is_configured = bool(key and key != "replace_me")
    return {
        "status": "ok",
        "gemini_configured": is_configured
    }

@app.get("/api/sample")
def get_sample_data():
    return sample_grievances()

@app.post("/api/extract", response_model=GrievanceReport)
async def extract_grievances(
    text: str = Form(default=""),
    file: UploadFile = File(default=None)
):
    trimmed_text = text.strip()
    if not trimmed_text and (not file or not file.filename):
        raise HTTPException(status_code=400, detail="Provide text description or select a file.")

    file_bytes = None
    mime_type = None

    if file and file.filename:
        content = await file.read()
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Selected file is empty.")
        if len(content) > 12 * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File exceeds maximum 12 MB size limit.")
        
        file_bytes = content
        mime_type = file.content_type or "application/octet-stream"

        # CSV handling fallback
        if file.filename.endswith(".csv") or mime_type == "text/csv":
            try:
                decoded = content.decode("utf-8-sig")
                reader = csv.reader(io.StringIO(decoded))
                csv_lines = [", ".join(row) for row in reader if row]
                trimmed_text = (trimmed_text + "\n" + "\n".join(csv_lines)).strip()
            except Exception as e:
                raise HTTPException(status_code=400, detail="CSV must be UTF-8 encoded.")

    try:
        report = ai_service.extract_grievance(text=trimmed_text, file_bytes=file_bytes, mime_type=mime_type)
        return report
    except RuntimeError as re:
        raise HTTPException(status_code=503, detail=str(re))
    except NotImplementedError:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key not configured. Use demo data or set GEMINI_API_KEY."
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Extraction service error: {str(e)}")

@app.post("/api/audits", response_model=AuditSession)
def create_audit(req: AuditRequest):
    if not req.grievances:
        raise HTTPException(status_code=400, detail="Load grievances before running an audit.")

    session_id = str(uuid.uuid4())
    session = AuditSession(
        session_id=session_id,
        status="analyzing",
        goal=req.goal,
        findings=[],
        pending_action=None,
        audit_log=[],
        summary="",
        steps=0
    )

    session.audit_log.append({
        "time": get_utc_now(),
        "type": "started",
        "message": f"Started civic agent audit session: '{req.goal}'",
        "details": {"grievance_count": len(req.grievances)}
    })

    grievance_dicts = [g.model_dump(mode="json") for g in req.grievances]
    available_tools = ["evaluate_severity_index", "match_municipal_department", "draft_civic_dispatch", "finish"]
    tool_results = []

    # Run bounded loop (max 6 steps)
    while session.steps < 6 and session.status in ["analyzing", "executing"]:
        session.steps += 1
        
        decision = ai_service.choose_next_step(
            goal=session.goal,
            findings=session.findings,
            tool_results=tool_results,
            available_tools=available_tools
        )

        session.audit_log.append({
            "time": get_utc_now(),
            "type": "plan",
            "message": f"Step {session.steps}: {decision.message}",
            "details": {"chosen_tool": decision.tool_name, "arguments": decision.arguments}
        })

        if decision.tool_name == "finish":
            session.status = "done"
            if not session.findings:
                session.summary = "Audit finished. No critical infrastructure hazards were identified."
            else:
                session.summary = f"Audit complete. Processed {len(session.findings)} critical infrastructure hazards."
            session.audit_log.append({
                "time": get_utc_now(),
                "type": "completed",
                "message": session.summary,
                "details": {}
            })
            break

        if decision.tool_name not in available_tools:
            session.status = "failed"
            session.summary = f"Error: Tool '{decision.tool_name}' is not in allowlist."
            session.audit_log.append({
                "time": get_utc_now(),
                "type": "error",
                "message": session.summary,
                "details": {}
            })
            break

        # Execute selected tool
        if decision.tool_name == "evaluate_severity_index":
            res = tools.evaluate_severity_index(grievance_dicts)
            session.findings = res
            tool_results.append({"tool_name": "evaluate_severity_index", "result": res})
            session.audit_log.append({
                "time": get_utc_now(),
                "type": "tool",
                "message": f"Evaluated severity indices: identified {len(res)} high/critical risk items.",
                "details": {"findings": res}
            })

        elif decision.tool_name == "match_municipal_department":
            cat = decision.arguments.get("category", "Other")
            loc = decision.arguments.get("location", "Location Unspecified")
            res = tools.match_municipal_department(cat, loc)
            tool_results.append({"tool_name": "match_municipal_department", "result": res})
            session.audit_log.append({
                "time": get_utc_now(),
                "type": "tool",
                "message": f"Matched department: '{res['assigned_department']}' for category '{cat}'.",
                "details": res
            })

        elif decision.tool_name == "draft_civic_dispatch":
            t_title = decision.arguments.get("title", "Infrastructure Defect")
            t_dept = decision.arguments.get("department", "General Civic Services")
            t_loc = decision.arguments.get("location", "Location Unspecified")
            t_idx = decision.arguments.get("priority_index", 75)
            
            res = tools.draft_civic_dispatch(t_title, t_dept, t_loc, t_idx)
            tool_results.append({"tool_name": "draft_civic_dispatch", "result": res})
            session.pending_action = res
            session.status = "awaiting_approval"
            
            session.audit_log.append({
                "time": get_utc_now(),
                "type": "approval_required",
                "message": f"Drafted municipal dispatch for '{t_title}'. Held behind human approval gate.",
                "details": res
            })
            # Pause loop for human approval
            break

    SESSIONS[session_id] = session
    return session

@app.get("/api/audits/{session_id}", response_model=AuditSession)
def get_audit_session(session_id: str):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Audit session not found.")
    return SESSIONS[session_id]

@app.post("/api/audits/{session_id}/approval", response_model=AuditSession)
def submit_approval(session_id: str, req: ApprovalRequest):
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Audit session not found.")
    
    session = SESSIONS[session_id]

    if session.status != "awaiting_approval":
        raise HTTPException(status_code=409, detail="Session decision already recorded.")

    if req.decision == "approve":
        session.status = "done"
        if session.pending_action:
            session.pending_action["approved"] = True
            session.pending_action["simulation_note"] = "Approved under local educational simulation mode. No external dispatch sent."
        
        dept = session.pending_action.get("department") if session.pending_action else "Municipal Dept"
        session.summary = f"Audit complete. Dispatch draft for '{dept}' was APPROVED (Simulated)."
        session.audit_log.append({
            "time": get_utc_now(),
            "type": "approved_simulation",
            "message": "Human reviewer approved dispatch draft (Simulation Mode).",
            "details": {"reason": req.reason}
        })

    elif req.decision == "reject":
        session.status = "done"
        if session.pending_action:
            session.pending_action["approved"] = False
        
        session.summary = "Audit complete. Dispatch draft was REJECTED by human reviewer."
        session.audit_log.append({
            "time": get_utc_now(),
            "type": "rejected",
            "message": "Human reviewer rejected dispatch draft.",
            "details": {"reason": req.reason}
        })

    SESSIONS[session_id] = session
    return session
