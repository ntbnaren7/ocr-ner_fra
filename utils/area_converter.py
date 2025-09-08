def parse_bigha_string(raw: str) -> float:
    """
    Convert "00-02-00 Bighas" format to hectares.
    Himachal context: 1 Bigha ≈ 0.08 hectares.
    For demo, treat "00-02-00" = 2 Bighas.
    """
    if not raw:
        return None

    try:
        parts = raw.replace("Bighas", "").strip().split("-")
        parts = [int(p) for p in parts if p.strip().isdigit()]

        total_bighas = 0
        if len(parts) == 3:
            total_bighas = parts[0] * 20 + parts[1] + parts[2] / 20
        elif len(parts) == 2:
            total_bighas = parts[0] + parts[1] / 20
        elif len(parts) == 1:
            total_bighas = parts[0]
        else:
            return None

        return round(total_bighas * 0.08, 3)
    except Exception:
        return None
