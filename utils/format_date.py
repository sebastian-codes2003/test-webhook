from datetime import datetime
from zoneinfo import ZoneInfo


def formate_date(iso_date: str) -> str:
    dt_utc = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
    dt_utc = dt_utc.replace(tzinfo=ZoneInfo("Etc/UTC"))  # 👈 aquí el fix

    dt_local = dt_utc.astimezone(ZoneInfo("America/Lima"))

    return dt_local.strftime("%d-%m-%Y %H:%M")
