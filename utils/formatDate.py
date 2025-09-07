# formatDate.py
from datetime import datetime
from zoneinfo import ZoneInfo


def formate_date(iso_date: str) -> str:
    # Parsear la fecha ISO (ej: 2025-09-07T18:00:53Z)
    dt_utc = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    dt_utc = dt_utc.replace(tzinfo=ZoneInfo("UTC"))

    # Convertir a UTC-5 (ej: America/Lima)
    dt_local = dt_utc.astimezone(ZoneInfo("America/Lima"))

    # Formato: dd-mm-aaaa hh-mm
    return dt_local.strftime("%d-%m-%Y %H:%M")
