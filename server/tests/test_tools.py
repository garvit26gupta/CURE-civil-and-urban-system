from app.tools import evaluate_severity_index, match_municipal_department, draft_civic_dispatch

def test_severity_evaluation():
    sample_items = [
        {"title": "Crack", "severity": "Critical", "category": "Roads & Bridges", "location": "Bridge 1"},
        {"title": "Trash", "severity": "Low", "category": "Other", "location": "Park"},
        {"title": "Leak", "severity": "High", "category": "Water & Sanitation", "location": "Street A"}
    ]
    results = evaluate_severity_index(sample_items)
    assert len(results) == 2
    critical_item = next(r for r in results if r["severity"] == "Critical")
    assert critical_item["priority_index"] == 95
    high_item = next(r for r in results if r["severity"] == "High")
    assert high_item["priority_index"] == 75

def test_department_matching():
    res = match_municipal_department("Roads & Bridges", "Main St")
    assert res["assigned_department"] == "Department of Transportation & Infrastructure"
    
    res_water = match_municipal_department("Water & Sanitation", "4th Ave")
    assert res_water["assigned_department"] == "Bureau of Water Works"

def test_dispatch_draft_not_sent():
    draft = draft_civic_dispatch("Bridge Defect", "Department of Transportation", "Main St", 95)
    assert draft["sent"] is False
    assert "DRAFT ONLY" in draft["notice_text"]
