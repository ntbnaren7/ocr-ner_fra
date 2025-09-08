from ocr.ocr_engine import extract_text
from extractors.entities import extract_entities
from schemas.fra_schema import build_schema
import json

if __name__ == "__main__":
    file_path = "sample_docs/sample_fra.png"  # change this

    print("🔹 Running OCR/Text extraction...")
    text = extract_text(file_path)

    print("\n--- Raw Text ---")
    print(text)

    print("\n🔹 Extracting entities...")
    entities = extract_entities(text)
    print(json.dumps(entities, indent=2))

    print("\n🔹 Building schema...")
    schema = build_schema(entities)
    print(json.dumps(schema, indent=2))
