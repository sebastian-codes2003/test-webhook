from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Fallback: si ZoneInfo no tiene "America/Lima"  
LIMA_TZ = timezone(timedelta(hours=-5))

def formate_date(iso_date: str) -> str:
    """Convierte un ISO 8601 UTC a dd-mm-aaaa hh:mm en Lima"""

    # Parsear con/ sin milisegundos
    try:
        dt_utc = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        dt_utc = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Asegurar que sea UTC
    dt_utc = dt_utc.replace(tzinfo=timezone.utc)

    # Intentar convertir a Lima con ZoneInfo
    try:
        lima_tz = ZoneInfo("America/Lima")
    except ZoneInfoNotFoundError:
        lima_tz = LIMA_TZ  # fallback UTC-5 fijo

    dt_local = dt_utc.astimezone(lima_tz)

    return dt_local.strftime("%d-%m-%Y %H:%M")
