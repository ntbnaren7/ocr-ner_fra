import os
import uuid
from typing import Any, List, Tuple

import numpy as np
import pdfplumber
from pdf2image import convert_from_path
from paddleocr import PaddleOCR
from PIL import Image
import cv2
import docx

# ---- Paths / setup ----
POPPLER_PATH = r"C:\poppler\poppler-25.07.0\Library\bin"  # <- your confirmed path
DEBUG_DIR = "debug"
os.makedirs(DEBUG_DIR, exist_ok=True)

# New flag name per deprecation
ocr = PaddleOCR(use_textline_orientation=True, lang='en')

# ---- PDF helpers ----
def extract_text_from_pdf(pdf_path: str) -> str:
    out = []
    with pdfplumber.open(pdf_path) as pdf:
        for p in pdf.pages:
            t = p.extract_text() or ""
            if t.strip():
                out.append(t)
    return "\n".join(out).strip()

def pdf_to_images(pdf_path: str):
    if not os.path.exists(POPPLER_PATH):
        raise FileNotFoundError(f"Poppler path not found: {POPPLER_PATH}")
    return convert_from_path(pdf_path, poppler_path=POPPLER_PATH)

# ---- Preprocess variants ----
def to_numpy(img_or_path) -> np.ndarray:
    if isinstance(img_or_path, np.ndarray):
        return img_or_path
    if isinstance(img_or_path, Image.Image):
        return np.array(img_or_path.convert("RGB"))
    if isinstance(img_or_path, str):
        return np.array(Image.open(img_or_path).convert("RGB"))
    raise TypeError(f"Unsupported image type: {type(img_or_path)}")

def pp_none(img: np.ndarray) -> np.ndarray:
    return img

def pp_binary(img: np.ndarray) -> np.ndarray:
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    _, th = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return cv2.cvtColor(th, cv2.COLOR_GRAY2RGB)

def pp_adaptive(img: np.ndarray) -> np.ndarray:
    g = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    th = cv2.adaptiveThreshold(g, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 31, 9)
    return cv2.cvtColor(th, cv2.COLOR_GRAY2RGB)

def pp_unsharp(img: np.ndarray) -> np.ndarray:
    blur = cv2.GaussianBlur(img, (0, 0), 1.0)
    sharp = cv2.addWeighted(img, 1.6, blur, -0.6, 0)
    return sharp

def pp_upscale(img: np.ndarray, scale: float) -> np.ndarray:
    h, w = img.shape[:2]
    return cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

# ---- Paddle result normalizer (supports old & new formats) ----
def normalize_line(line: Any) -> Tuple[np.ndarray, str, float]:
    if isinstance(line, dict):
        pts = line.get("points")
        box = np.array(pts, dtype=np.int32) if pts is not None else None
        txt = line.get("transcription", "") or ""
        conf = float(line.get("score", 0.0) or 0.0)
        return box, txt, conf
    # old format: [box, (text, conf)]
    try:
        box = np.array(line[0], dtype=np.int32)
        txt = line[1][0] or ""
        conf = float(line[1][1] or 0.0)
        return box, txt, conf
    except Exception:
        return None, "", 0.0

def draw_boxes(result: List[Any], np_img: np.ndarray, fname_prefix: str) -> str:
    img = np_img.copy()
    any_box = False
    for res in result:
        for line in res:
            box, txt, conf = normalize_line(line)
            if box is None:
                continue
            try:
                cv2.polylines(img, [box], True, (0, 255, 0), 2)
                any_box = True
            except Exception:
                pass
    out = os.path.join(DEBUG_DIR, f"{fname_prefix}_{uuid.uuid4().hex}.jpg")
    cv2.imwrite(out, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    return out

# ---- Core OCR (single pass) ----
def ocr_once(np_img: np.ndarray, conf_cut: float = 0.4, tag: str = "pass") -> Tuple[str, float, int, str]:
    result = ocr.ocr(np_img)
    debug_path = draw_boxes(result, np_img, f"ocr_debug_{tag}")

    texts = []
    confs = []
    for res in result:
        for line in res:
            _, t, c = normalize_line(line)
            if t and c >= conf_cut:
                texts.append(t)
                confs.append(c)

    text = " ".join(texts).strip()
    avg_conf = float(np.mean(confs)) if confs else 0.0
    return text, avg_conf, len(text), debug_path

# ---- Multi-pass OCR with selection ----
def run_ocr_on_image(img_or_path) -> str:
    base = to_numpy(img_or_path)

    variants = []
    # original, sharpened, binary, adaptive; also upscaled 1.5x and 2x for some
    variants.append(("orig", pp_none(base)))
    variants.append(("sharp", pp_unsharp(base)))
    variants.append(("bin", pp_binary(base)))
    variants.append(("ada", pp_adaptive(base)))
    variants.append(("orig_1p5", pp_upscale(base, 1.5)))
    variants.append(("bin_1p5", pp_binary(pp_upscale(base, 1.5))))
    variants.append(("ada_1p5", pp_adaptive(pp_upscale(base, 1.5))))
    variants.append(("orig_2x", pp_upscale(base, 2.0)))
    variants.append(("bin_2x", pp_binary(pp_upscale(base, 2.0))))
    variants.append(("ada_2x", pp_adaptive(pp_upscale(base, 2.0))))

    results = []
    dump_lines = []

    for tag, img in variants:
        text, avg_conf, nchar, dbg = ocr_once(img, conf_cut=0.4, tag=tag)
        results.append((nchar, avg_conf, text))
        dump_lines.append(f"[{tag}] chars={nchar} avg_conf={avg_conf:.3f} dbg={os.path.basename(dbg)}\n{text[:400]}\n")

    # Save a dump for debugging/demo
    dump_path = os.path.join(DEBUG_DIR, "last_ocr_dump.txt")
    with open(dump_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(dump_lines))
    print(f"🔹 OCR dump saved: {dump_path}")

    # pick best by chars, then by avg conf
    results.sort(key=lambda x: (x[0], x[1]))
    best = results[-1] if results else (0, 0.0, "")
    return best[2].strip()

# ---- Public entry ----
def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    text = ""

    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
        if not text:
            for img in pdf_to_images(file_path):
                chunk = run_ocr_on_image(img)
                if chunk:
                    text += chunk + "\n"
    elif ext in (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"):
        text = run_ocr_on_image(file_path)
    elif ext in (".docx", ".doc"):
        try:
            doc = docx.Document(file_path)
            paras = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n".join(paras)
        except Exception as e:
            raise ValueError(f"Failed to read DOCX: {e}")
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    return text.strip()

