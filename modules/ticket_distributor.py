import os
import re
from datetime import datetime
import pandas as pd

def read_csv_any_encoding(path: str) -> pd.DataFrame:
    encodings = ["utf-8", "utf-8-sig", "latin1", "windows-1252"]
    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    raise Exception("Tidak dapat membaca file CSV dengan encoding yang didukung (utf-8, latin1, windows-1252).")

def sanitize_incident_id(value) -> str:
    """Ambil hanya karakter alfanumerik seperti INC0000XXX"""
    if pd.isna(value):
        return ""
    s = str(value).strip()
    cleaned = re.sub(r"[^A-Za-z0-9]", "", s)
    return cleaned.upper()

def distribute_tickets(
    file_path: str,
    names_input: str,
    mode: str = "equal",
    tickets_per_person: int = None,
    output_dir: str = "data"
):
    """
    Logika pemrosesan & pembagian tiket.
    Menghasilkan file CSV di folder output_dir ('data/') dan summary count per agent.
    
    Returns:
        (output_csv_path, summary_counts_dict, error_msg)
    """
    os.makedirs(output_dir, exist_ok=True)

    # 1. BACA FILE (EXCEL / CSV)
    try:
        if file_path.lower().endswith((".xlsx", ".xls")):
            df = pd.read_excel(file_path)
        else:
            df = read_csv_any_encoding(file_path)
    except Exception as e:
        return None, None, f"❌ Gagal membaca file: {e}"

    # 2. VALIDASI KOLOM & DATA
    if "Incident ID*+" not in df.columns:
        matched_col = None
        for col in df.columns:
            if "incident id" in str(col).lower():
                matched_col = col
                break
        if matched_col:
            df.rename(columns={matched_col: "Incident ID*+"}, inplace=True)
        else:
            return None, None, "❌ Kolom 'Incident ID*+' tidak ditemukan di file."

    tickets = (
        df["Incident ID*+"]
        .dropna()
        .apply(sanitize_incident_id)
        .tolist()
    )
    tickets = [x for x in tickets if x]

    if not tickets:
        return None, None, "❌ Tidak ada Incident ID yang valid ditemukan dalam file."

    if isinstance(names_input, str):
        names = [n.strip() for n in names_input.split(",") if n.strip()]
    else:
        names = [n.strip() for n in names_input if str(n).strip()]

    if not names:
        return None, None, "❌ Daftar nama agent kosong."

    results = {}

    # 3. PROSES DISTRIBUSI
    if mode == "equal":
        base = len(tickets) // len(names)
        sisa = len(tickets) % len(names)
        idx = 0

        for i, name in enumerate(names):
            jumlah = base + (1 if i < sisa else 0)
            results[name.upper()] = tickets[idx : idx + jumlah]
            idx += jumlah

    elif mode == "fixed":
        if not tickets_per_person or tickets_per_person <= 0:
            return None, None, "❌ Jumlah tiket per person harus lebih dari 0 untuk mode 'fixed'."

        idx = 0
        for name in names:
            assigned = tickets[idx : idx + tickets_per_person]
            results[name.upper()] = assigned
            idx += len(assigned)

        if idx < len(tickets):
            results["SISA TIKET"] = tickets[idx:]
    else:
        return None, None, f"❌ Mode '{mode}' tidak dikenali. Pilih 'equal' atau 'fixed'."

    # 4. EXPORT KE CSV
    rows = []
    summary_counts = {}

    for name, incs in results.items():
        summary_counts[name] = len(incs)
        for inc in incs:
            rows.append([
                name,
                inc,
                f"'Incident ID*+' = \"{inc}\" OR"
            ])

    out_df = pd.DataFrame(
        rows,
        columns=[
            "NAMA",
            "INCIDENT ID",
            "FORMAT QUERY"
        ]
    )

    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"Distribusi_Tiket_{timestamp_str}.csv"
    output_path = os.path.join(output_dir, output_filename)

    out_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig"
    )

    return output_path, summary_counts, None
