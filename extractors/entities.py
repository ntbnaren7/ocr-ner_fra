# extractors/entities.py
import re
import spacy
from typing import Optional, Dict, Callable

nlp = spacy.load("en_core_web_trf")
FLAGS = re.I | re.M

# Helper regex utils
def _find(pattern: str, text: str) -> Optional[str]:
    m = re.search(pattern, text, flags=FLAGS)
    return m.group(1).strip() if m else None

def _find_all(pattern: str, text: str):
    return re.findall(pattern, text, flags=FLAGS)

# Form detection (broad)
def detect_form_type(text: str) -> str:
    t = text.upper()
    if "ANNEXURE-II" in t or "TITLE FOR FOREST LAND UNDER OCCUPATION" in t:
        return "Annexure-II"
    if "ANNEXURE-III" in t:
        return "Annexure-III"
    if "ANNEXURE-IV" in t:
        return "Annexure-IV"
    if "FORM – A" in t or re.search(r"CLAIM FORM FOR RIGHTS TO FOREST LAND", t):
        return "Form A"
    if "FORM – B" in t or "CLAIM FORM FOR COMMUNITY RIGHTS" in t:
        return "Form B"
    if "FORM – C" in t or "CLAIM FORM FOR RIGHTS TO COMMUNITY FOREST RESOURCE" in t:
        return "Form C"
    return "Unknown"

# Generic fallback extraction used across forms
def extract_common(text: str) -> Dict:
    claimant = _find(r"Name of the claimant(?:\(s\))?:\s*([A-Za-z0-9 ,.'/-]+)", text)
    spouse = _find(r"Name of the spouse:\s*([A-Za-z0-9 ,.'/-]+)", text)
    parent = _find(r"Name of father/mother:\s*([A-Za-z0-9 ,.'/-]+)", text)
    tribe = _find(r"Tribe name:\s*([A-Za-z0-9 ,.'/-]+)", text)
    patta = _find(r"Patta\s*No\.?:\s*([A-Za-z0-9/_-]+)", text)
    dlc = _find(r"Date of DLC decision:\s*(\d{1,2}[/\-]\d{1,2}[/\-]\d{4})", text)

    return {
        "claimant_name": claimant,
        "spouse_name": spouse,
        "father_mother_name": parent,
        "tribe_name": tribe,
        "patta_number": patta,
        "dlc_decision_date": dlc
    }

# Form-specific extractors

def extract_form_a(text: str) -> Dict:
    base = extract_common(text)
    village = _find(r"Village:\s*([A-Za-z0-9 \-.,()]+)", text)
    gp = _find(r"Gram\s*Panchayat:\s*([A-Za-z0-9 \-.,()]+)", text)
    tehsil = _find(r"Tehsil/Taluka:\s*([A-Za-z0-9 \-.,()]+)", text)
    district = _find(r"District:\s*([A-Za-z0-9 \-.,()]+)", text)
    area = _find(r"Area of land claimed:\s*([\d.]+)\s*(?:ha|hectare|hectares)?", text)
    status = _find(r"Claim status:\s*(Approved|Rejected|Pending)", text)
    livelihood = _find(r"Livelihood type:\s*([A-Za-z0-9 ,.-]+)", text)
    water = _find(r"Water source type:\s*([A-Za-z0-9 ,.-]+)", text)

    ent = {
        **base,
        "form_type": "Form A",
        "village": village,
        "gram_panchayat": gp,
        "tehsil": tehsil,
        "district": district,
        "area_claimed": float(area) if area else None,
        "area_unit": "hectares" if area else None,
        "fra_claim_status": status,
        "livelihood_type": livelihood,
        "water_source_type": water
    }
    return ent

def extract_form_b_or_c(text: str) -> Dict:
    base = extract_common(text)
    village = _find(r"Village:\s*([A-Za-z0-9 \-.,()]+)", text) or _find(r"Village/Gram Sabha:\s*([A-Za-z0-9 \-.,()]+)", text)
    gp = _find(r"Gram\s*Panchayat:\s*([A-Za-z0-9 \-.,()]+)", text)
    district = _find(r"District:\s*([A-Za-z0-9 \-.,()]+)", text)
    community_rights = _find(r"Nature of community rights(?:.*):\s*([\s\S]+?)(?:\n\d|\n$)", text)
    area = _find(r"Extent of land .*?(\d+[\d., ]*ha|\d+[\d., ]*hectares)?", text)

    ent = {
        **base,
        "form_type": "Form B/C",
        "village": village,
        "gram_panchayat": gp,
        "district": district,
        "community_rights_description": community_rights,
        "area_claimed_raw": area,
        "area_claimed_ha": None
    }
    return ent

def extract_annexure_ii(text: str) -> Dict:
    base = extract_common(text)
    # Name(s) of holders: often in numbered column — collect by capturing the block
    holders_block = _find(r"Name\(s\) of Holder\(s\)[\s\S]*?:\s*([\s\S]+?)\n\d", text) or _find(r"Name\(s\) of Holder\(s\).*?\n([\s\S]+?)\n\d", text)
    holders = None
    if holders_block:
        # split on newline/semicolon/numbering
        parts = re.split(r"\n|\d\.\s*|\s{2,}|;", holders_block)
        parts = [p.strip().strip(".,") for p in parts if p and len(p.strip())>1]
        holders = parts

    dependents = _find(r"Name of Dependents:\s*([\s\S]+?)\n\d") or _find(r"Name of Dependents:\s*([\s\S]+?)\n", text)
    address = _find(r"Address:\s*([A-Za-z0-9 ,.\-()/]+)", text)
    village = _find(r"Village(?:/Gram Sabha)?:\s*([A-Za-z0-9 ,.\-()]+)", text)
    gram_panchayat = _find(r"Gram Panchayat:\s*([A-Za-z0-9 ,.\-()]+)", text)
    tehsil = _find(r"Tehsil/Taluka:\s*([A-Za-z0-9 ,.\-()]+)", text)
    district = _find(r"District:\s*([A-Za-z0-9 ,.\-()]+)", text)
    st_status = _find(r"Whether Scheduled Tribe.*?:\s*([A-Za-z ,]+)", text)
    area_raw = _find(r"Area:\s*([0-9\-\s:]+ *Bighas)", text) or _find(r"Area:\s*([0-9. ]+ *Bigha|[0-9. ]+ *Bighas)", text)
    khasra = _find(r"Khasra No\.?:\s*([0-9/]+)", text) or _find(r"Khasra No\.?:\s*([A-Za-z0-9/\- ]+)", text)
    boundaries = _find(r"Description of boundaries[\s\S]*?:\s*([\s\S]+?)(?:\n\n|\n\d|$)", text)

    ent = {
        **base,
        "form_type": "Annexure-II",
        "holders": holders,
        "dependents": dependents,
        "address": address,
        "village": village,
        "gram_panchayat": gram_panchayat,
        "tehsil": tehsil,
        "district": district,
        "scheduled_tribe_status": st_status,
        "area_claimed_raw": area_raw,
        "area_claimed_ha": None,
        "khasra_number": khasra,
        "boundaries": boundaries
    }
    return ent

def extract_annexure_others(text: str) -> Dict:
    # Generic extractor for Annexure-III/IV (community resources)
    base = extract_common(text)
    village = _find(r"Village(?:/Gram Sabha)?:\s*([A-Za-z0-9 ,.\-()]+)", text)
    gram_panchayat = _find(r"Gram Panchayat:\s*([A-Za-z0-9 ,.\-()]+)", text)
    nature = _find(r"Nature of community rights:\s*([\s\S]+?)(?:\n\d|$)", text)
    boundaries = _find(r"Description of boundaries[\s\S]*?:\s*([\s\S]+?)(?:\n\n|\n\d|$)", text)

    ent = {
        **base,
        "form_type": "Annexure-Other",
        "village": village,
        "gram_panchayat": gram_panchayat,
        "community_rights_description": nature,
        "boundaries": boundaries
    }
    return ent

# Registry of extractors
EXTRACTOR_REGISTRY: Dict[str, Callable[[str], Dict]] = {
    "Form A": extract_form_a,
    "Form B": extract_form_b_or_c,
    "Form C": extract_form_b_or_c,
    "Annexure-II": extract_annexure_ii,
    "Annexure-III": extract_annexure_others,
    "Annexure-IV": extract_annexure_others
}

def extract_entities(text: str) -> Dict:
    form = detect_form_type(text)
    extractor = EXTRACTOR_REGISTRY.get(form, extract_form_a)  # default to Form A-like
    entities = extractor(text)
    # ensure consistent keys exist — add common keys if missing
    common_keys = [
        "form_type", "claimant_name", "spouse_name", "father_mother_name", "tribe_name",
        "patta_number", "dlc_decision_date",
        "village", "gram_panchayat", "tehsil", "district",
        "area_claimed", "area_unit", "area_claimed_raw", "area_claimed_ha",
        "fra_claim_status", "khasra_number", "boundaries", "dependents", "holders",
        "address", "community_rights_description", "scheduled_tribe_status"
    ]
    for k in common_keys:
        entities.setdefault(k, None)
    return entities
