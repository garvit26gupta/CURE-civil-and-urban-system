def evaluate_severity_index(grievances: list[dict]) -> list[dict]:
    """
    Filters grievances where severity is High or Critical and calculates a Priority Index.
    """
    findings = []
    for g in grievances:
        sev = g.get("severity")
        if sev in ["High", "Critical"]:
            priority_index = 95 if sev == "Critical" else 75
            findings.append({
                "title": g.get("title"),
                "category": g.get("category"),
                "location": g.get("location") or "Location Unspecified",
                "severity": sev,
                "priority_index": priority_index
            })
    return findings

def match_municipal_department(category: str, location: str) -> dict:
    """
    Maps grievance category to the responsible municipal department.
    """
    mapping = {
        "Roads & Bridges": "Department of Transportation & Infrastructure",
        "Water & Sanitation": "Bureau of Water Works",
        "Public Safety": "Municipal Emergency & Safety Services",
        "Pollution & Environment": "Environmental Protection Agency",
        "Power & Grid": "Public Electrical Grid Division",
        "Other": "General Civic Services"
    }
    assigned = mapping.get(category, "General Civic Services")
    return {
        "category": category,
        "assigned_department": assigned,
        "priority_level": "Urgent Dispatch Required"
    }

def draft_civic_dispatch(title: str, department: str, location: str, priority_index: int) -> dict:
    """
    Constructs formal municipal dispatch draft text. Does not execute external dispatch.
    """
    notice = (
        f"Subject: Official Civic Issue Dispatch Notice - Urgent Repair Request\n\n"
        f"To: {department}\n"
        f"Location: {location}\n"
        f"Issue: {title}\n"
        f"Priority Index: {priority_index}/100\n\n"
        f"Notice: An automated civic grievance assessment has identified a localized infrastructure issue requiring department review. "
        f"Please review this dispatch draft and verify site accessibility.\n\n"
        f"Status: DRAFT ONLY - PENDING LOCAL SIMULATION APPROVAL."
    )
    return {
        "title": title,
        "department": department,
        "location": location,
        "priority_index": priority_index,
        "notice_text": notice,
        "sent": False
    }
