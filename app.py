import os
import shutil
import traceback
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from schemas.fra_schema import build_schema, pretty_print

from ocr.ocr_engine import extract_text
from extractors.entities import extract_entities
from schemas.fra_schema import build_schema

app = FastAPI(
    title="FRA Digitization API",
    version="1.0.0",
    description="Upload FRA claim forms (Form A, Annexures). Extracts structured JSON."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post(
    "/extract",
    summary="Extract FRA Claim Data",
    description="Upload a scanned/digital FRA document (Form A, Annexure-II etc). Returns structured JSON.",
    response_description="Structured JSON containing claimant, location, area, patta etc.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "document_metadata": {
                            "document_type": "Form A - Individual Claim",
                            "reference_number": None,
                            "extraction_date": "2025-09-04T10:30:00Z",
                            "language": "English"
                        },
                        "claimant_details": {
                            "claimant_name": "Ram Singh",
                            "spouse_name": "Sita Devi",
                            "father_mother_name": "Mohan Singh",
                            "tribe_name": "Gond"
                        },
                        "location": {
                            "address": "Village Road, Bhilgaon",
                            "village": "Bhilgaon",
                            "gram_sabha": None,
                            "gram_panchayat": "Bhilgaon GP",
                            "tehsil": "Amravati Tehsil",
                            "district": "Amravati"
                        },
                        "claim_information": {
                            "fra_right_type": "Individual Forest Right",
                            "area_claimed": 3.5,
                            "area_unit": "hectares",
                            "area_claimed_raw": None,
                            "area_claimed_ha": 3.5,
                            "fra_claim_status": "Approved",
                            "patta_number": "PATTA/2025/091",
                            "khasra_number": None,
                            "boundaries": None
                        },
                        "dates": {
                            "dlc_decision_date": "25/08/2025"
                        }
                    }
                }
            }
        }
    }
)
# app.py (replace the extract endpoint implementation body with this snippet)
# inside your existing app.py definitions

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    dst_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(dst_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        raw_text = extract_text(dst_path)
        if not raw_text:
            raise HTTPException(status_code=422, detail="No text detected in file.")

        entities = extract_entities(raw_text)

        # for Annexure-II area conversion, try to convert if raw bigha present
        # (we assume you have utils.area_converter.parse_bigha_string installed)
        try:
            from utils.area_converter import parse_bigha_string
            if entities.get("area_claimed_raw") and not entities.get("area_claimed_ha"):
                ha = parse_bigha_string(entities.get("area_claimed_raw"))
                if ha:
                    entities["area_claimed_ha"] = ha
        except Exception:
            pass

        schema = build_schema(entities)
        pretty = pretty_print(entities)
        return JSONResponse({"json": schema, "pretty_text": pretty})

    except HTTPException:
        raise
    except Exception as e:
        tb = traceback.format_exc(limit=3)
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {e.__class__.__name__}: {e}\n{tb}"
        )
    finally:
        try:
            os.remove(dst_path)
        except Exception:
            pass



if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
