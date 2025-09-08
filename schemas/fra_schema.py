# schemas/fra_schema.py
from typing import Dict, Any
from datetime import datetime

def build_schema(entities: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "document_metadata": {
            "document_type": entities.get("form_type") or "Unknown FRA Form",
            "reference_number": None,
            "extraction_date": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "language": "English"
        },
        "claimant_details": {
            "claimant_name": entities.get("claimant_name"),
            "spouse_name": entities.get("spouse_name"),
            "father_mother_name": entities.get("father_mother_name"),
            "holders": entities.get("holders"),
            "dependents": entities.get("dependents"),
            "tribe_name": entities.get("tribe_name"),
            "scheduled_tribe_status": entities.get("scheduled_tribe_status")
        },
        "location": {
            "address": entities.get("address"),
            "village": entities.get("village"),
            "gram_panchayat": entities.get("gram_panchayat"),
            "gram_sabha": entities.get("gram_sabha"),
            "tehsil": entities.get("tehsil"),
            "district": entities.get("district"),
        },
        "claim_information": {
            "fra_right_type": entities.get("fra_right_type"),
            "area_claimed": entities.get("area_claimed"),
            "area_unit": entities.get("area_unit"),
            "area_claimed_raw": entities.get("area_claimed_raw"),
            "area_claimed_ha": entities.get("area_claimed_ha"),
            "fra_claim_status": entities.get("fra_claim_status"),
            "patta_number": entities.get("patta_number"),
            "khasra_number": entities.get("khasra_number"),
            "boundaries": entities.get("boundaries"),
            "community_rights_description": entities.get("community_rights_description")
        },
        "dates": {
            "dlc_decision_date": entities.get("dlc_decision_date")
        }
    }

def pretty_print(entities: Dict[str, Any]) -> str:
    """
    Build a human-readable summary string from the extracted entities.
    """
    lines = []
    lines.append(f"Form Type: {entities.get('form_type') or 'Unknown'}")
    # Claimant/holders
    if entities.get("holders"):
        lines.append("Holders:")
        for h in entities.get("holders"):
            lines.append(f"  - {h}")
    else:
        lines.append(f"Claimant: {entities.get('claimant_name') or 'N/A'}")
        if entities.get("spouse_name"):
            lines.append(f"Spouse: {entities.get('spouse_name')}")
        if entities.get("father_mother_name"):
            lines.append(f"Father/Mother: {entities.get('father_mother_name')}")

    if entities.get("dependents"):
        lines.append(f"Dependents: {entities.get('dependents')}")

    # Location
    loc = []
    if entities.get("village"):
        loc.append(f"Village: {entities.get('village')}")
    if entities.get("gram_panchayat"):
        loc.append(f"Gram Panchayat: {entities.get('gram_panchayat')}")
    if entities.get("tehsil"):
        loc.append(f"Tehsil: {entities.get('tehsil')}")
    if entities.get("district"):
        loc.append(f"District: {entities.get('district')}")
    if loc:
        lines.append("Location: " + " | ".join(loc))

    # Area
    if entities.get("area_claimed_raw"):
        raw = entities.get("area_claimed_raw")
        ha = entities.get("area_claimed_ha")
        if ha:
            lines.append(f"Area (raw): {raw} (~{ha} ha)")
        else:
            lines.append(f"Area (raw): {raw}")
    elif entities.get("area_claimed"):
        lines.append(f"Area: {entities.get('area_claimed')} {entities.get('area_unit') or 'ha'}")

    if entities.get("khasra_number"):
        lines.append(f"Khasra/Survey: {entities.get('khasra_number')}")
    if entities.get("patta_number"):
        lines.append(f"Patta No: {entities.get('patta_number')}")
    if entities.get("fra_claim_status"):
        lines.append(f"Claim Status: {entities.get('fra_claim_status')}")
    if entities.get("boundaries"):
        lines.append(f"Boundaries: {entities.get('boundaries')}")
    if entities.get("dlc_decision_date"):
        lines.append(f"DLC Decision: {entities.get('dlc_decision_date')}")

    return "\n".join(lines)
