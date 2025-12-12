# 📝 OCR + NER for English Documents

This project focuses on extracting **structured information** from scanned English documents using **OCR (Optical Character Recognition)** combined with **NER (Named Entity Recognition)**. The goal is to automatically identify and extract key entities like names, patta numbers, age, date of birth, and other important fields from unstructured documents.

This tool was developed as part of **SIH 2025** to facilitate automated data extraction and preprocessing for official or administrative documents.

---

## 🚀 Features

- **OCR-based Text Extraction**  
  Converts scanned documents or images into machine-readable text.

- **Named Entity Recognition (NER)**  
  Extracts specific entities automatically, including:
  - Name  
  - Patta Number  
  - Age  
  - Date of Birth (DOB)  
  - Gender  
  - Address  
  - Other relevant document-specific fields

- **Structured Output**  
  Provides extracted data in a structured format (JSON, CSV, etc.) for further use.

- **Flexible Document Handling**  
  Works with multiple types of English documents like forms, certificates, or official records.

---

## 🛠️ Installation

Clone the repository:

```bash
git clone https://github.com/your-username/ocr-ner-documents.git
cd ocr-ner-documents
```

Install dependencies (Python example):
```python
pip install -r requirements.txt
```
Ensure you have Tesseract OCR installed if using pytesseract.

---

## ⚡ Usage

Extract entities from a single document:
```python
from ocr_ner import extract_entities

# Provide the path to your document
document_path = "documents/sample_doc.pdf"

entities = extract_entities(document_path)
print(entities)
```

Batch process multiple documents:
```python
from ocr_ner import batch_extract_entities

documents = ["documents/doc1.pdf", "documents/doc2.pdf", "documents/doc3.pdf"]
results = batch_extract_entities(documents)

for res in results:
    print(res)
```

---

## 📚 How It Works

### OCR (Text Extraction)
Uses tools like `pytesseract` to read text from scanned images or PDFs.

### NER (Entity Recognition)
Applies trained NLP models or regex-based rules to identify and extract specific entities.

### Structured Output
Extracted entities are returned as dictionaries, JSON, or CSV for easy integration into other workflows.

---

## 🎯 Use Cases

- Automating **data entry** from forms and certificates.  
- Preprocessing documents for **database population**.  
- Extracting **personal or official information** for analytics or reporting.  
- Integrating into **verification pipelines** for administrative processes.

---

## 🖼️ Preview

Example output from a sample document:

```json
{
  "Name": "John Doe",
  "Patta Number": "12345",
  "Age": "35",
  "Date of Birth": "01-01-1990",
  "Gender": "Male",
  "Address": "123 Main Street, City, Country"
}
