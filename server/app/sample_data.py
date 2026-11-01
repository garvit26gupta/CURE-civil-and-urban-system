from app.models import Grievance

def sample_grievances() -> list[Grievance]:
    return [
        Grievance(
            title="Main Street Bridge Structural Concrete Crack",
            date="2026-09-14",
            category="Roads & Bridges",
            severity="Critical",
            location="Main Street Bridge, Span 4",
            raw_line="2026-09-14 Major structural failure concrete crack under Main St Bridge"
        ),
        Grievance(
            title="River Road Main Water Valve Leak",
            date="2026-09-15",
            category="Water & Sanitation",
            severity="High",
            location="River Road & 4th Ave Intersection",
            raw_line="2026-09-15 Heavy high-pressure water leaking near River Rd"
        ),
        Grievance(
            title="Central Park Unauthorized Waste Dumping",
            date="2026-09-12",
            category="Pollution & Environment",
            severity="Medium",
            location="Central Park East Gate Entrance",
            raw_line="2026-09-12 Chemical drums and industrial plastic trash piled in park"
        ),
        Grievance(
            title="Oak Street Broken Streetlights Block 5",
            date="2026-09-10",
            category="Power & Grid",
            severity="Low",
            location="Oak Street, 500 Block",
            raw_line="2026-09-10 Night lights out on entire 5th block of Oak"
        ),
        Grievance(
            title="5th Avenue Exposed High-Voltage Line",
            date="2026-09-16",
            category="Power & Grid",
            severity="Critical",
            location="5th Avenue & Elm St",
            raw_line="2026-09-16 Power transformer cable dangling down to sidewalk level"
        ),
        Grievance(
            title="Downtown Market Damaged Pedestrian Guardrail",
            date="2026-09-08",
            category="Public Safety",
            severity="Medium",
            location="Downtown Market Plaza",
            raw_line="2026-09-08 Metal railing broken and sharp edge sticking out"
        ),
        Grievance(
            title="Pine Street Open Sewer Manhole",
            date="2026-09-16",
            category="Public Safety",
            severity="Critical",
            location="Pine Street outside House #42",
            raw_line="2026-09-16 Open manhole cover missing completely on primary road"
        ),
        Grievance(
            title="Industrial Zone Toxic Chemical Effluent Flow",
            date="2026-09-13",
            category="Pollution & Environment",
            severity="High",
            location="North Industrial Canal Drain 3",
            raw_line="2026-09-13 Strong sulfur odor and dark foam pouring into storm drain"
        ),
        Grievance(
            title="Sunset Blvd Deep Pothole Cluster",
            date="2026-09-11",
            category="Roads & Bridges",
            severity="Medium",
            location="Sunset Blvd & 12th St",
            raw_line="2026-09-11 Multiple deep holes causing severe tire damage"
        ),
        Grievance(
            title="Westside Elementary School Zone Signal Failure",
            date="2026-09-16",
            category="Public Safety",
            severity="High",
            location="Westside Elementary Crosswalk",
            raw_line="2026-09-16 Traffic light flashing red in all directions during drop-off"
        ),
        Grievance(
            title="Harbor View Sewage Backflow Overflow",
            date="2026-09-15",
            category="Water & Sanitation",
            severity="Critical",
            location="Harbor View Residential Lane",
            raw_line="2026-09-15 Raw sewage backing up into street drainage gutters"
        ),
        Grievance(
            title="Commercial District Abandoned Vehicle Obstruction",
            date="2026-09-05",
            category="Other",
            severity="Low",
            location="Commerce Way Alleyway",
            raw_line="2026-09-05 Rusting van blocking delivery dock for 3 weeks"
        ),
        Grievance(
            title="Elm Street Dead Tree Hazard Above Power Lines",
            date="2026-09-14",
            category="Power & Grid",
            severity="High",
            location="Elm Street near 8th Ave",
            raw_line="2026-09-14 Large dead branch hanging directly over high voltage line"
        ),
        Grievance(
            title="Civic Center Fountain Water Filtration Clog",
            date="2026-09-02",
            category="Other",
            severity="Low",
            location="Civic Center Courtyard",
            raw_line="2026-09-02 Water dirty and pump making grinding noise"
        )
    ]
