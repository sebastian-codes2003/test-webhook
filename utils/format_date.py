from datetime import datetime, timezone
from zoneinfo import ZoneInfo


def formate_date(iso_date: str) -> str:

    # Intentar parseo con y sin milisegundos
    try:
        dt_utc = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        dt_utc = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%fZ")

    # Asignar timezone UTC (siempre disponible)
    dt_utc = dt_utc.replace(tzinfo=timezone.utc)

    # Convertir a tu zona local
    dt_local = dt_utc.astimezone(ZoneInfo("America/Lima"))

    # Formatear
    return dt_local.strftime("%d-%m-%Y %H:%M")
