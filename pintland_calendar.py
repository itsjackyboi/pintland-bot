from datetime import datetime, date
from zoneinfo import ZoneInfo
import re

# -----------------------------
# PINTLAND CONFIG
# -----------------------------

DAY_NAMES = [
    "Mooringday", "Brewsday", "Tidecall",
    "Grogsnap", "Beastwatch", "Lagerhorn",
    "Bloodwake", "Keeldrift", "Hangover"
]

SEASONS = [
    ("Stormtide", 117),
    ("Goldsun", 234),
    ("Veilfrost", 351),
    ("Holiday", 360),
]

EPOCH = date(2026, 1, 1)

BASE_YEAR = 466
BASE_CYCLE = 93

# -----------------------------
# TIME (EST/EDT SAFE, NO PYTZ)
# -----------------------------

def get_today():
    eastern = ZoneInfo("America/New_York")
    return datetime.now(eastern).date()

# -----------------------------
# RUMORS
# -----------------------------

def load_rumors():
    with open("rumors.txt", "r", encoding="utf-8") as f:
        content = f.read()

    raw = re.split(r"\n(?=\d+\.\s)", content.strip())

    cleaned = []
    for r in raw:
        r = re.sub(r"^\d+\.\s*", "", r).strip()
        if r:
            cleaned.append(r)

    return cleaned

RUMORS = load_rumors()

# -----------------------------
# CORE LOGIC
# -----------------------------

def get_calendar_data():
    today = get_today()
    delta_days = (today - EPOCH).days

    dik = delta_days % 9
    day_name = DAY_NAMES[dik]

    doy = (delta_days % 360) + 1

    if doy <= 117:
        season = "Stormtide"
        keg = (doy - 1) // 9 + 1
    elif doy <= 234:
        season = "Goldsun"
        keg = (doy - 118) // 9 + 1
    elif doy <= 351:
        season = "Veilfrost"
        keg = (doy - 235) // 9 + 1
    else:
        season = "Holiday"
        keg = 1

    year_offset = delta_days // 360
    pint_year = BASE_YEAR + year_offset

    cycle = BASE_CYCLE + (year_offset // 5)

    return {
        "day_name": day_name,
        "season": season,
        "keg": keg,
        "year": pint_year,
        "cycle": cycle,
        "doy": doy
    }

# -----------------------------
# RUMOR PICK
# -----------------------------

def get_rumor(doy):
    if not RUMORS:
        return None
    return RUMORS[(doy - 1) % len(RUMORS)]

# -----------------------------
# FINAL MESSAGE
# -----------------------------

def format_message():
    p = get_calendar_data()
    rumor = get_rumor(p["doy"])

    return f"""🍺 Good morning Liquor Kings.

Today is {p['day_name']} in the {p['keg']}th Keg of {p['season']}.

Year {p['year']} — Cycle {p['cycle']}.

📜 Tavern Rumor
{rumor if rumor else "No rumor today..."}

Happy Drinking!"""
